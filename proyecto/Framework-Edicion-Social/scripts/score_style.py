#!/usr/bin/env python3
"""Score the style catalog against a creative blueprint deterministically.

The scorer is intentionally conservative. It selects only when the leading
eligible style clears both an absolute threshold and a minimum margin over the
runner-up. Otherwise it records a valid abstention with structured reasons.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path


DIMENSIONS = (
    "topic_and_intent",
    "narrative_rhythm",
    "source_geometry",
    "platform_fit",
    "brand_tone",
)
ELIGIBLE_STATUSES = {"candidate", "testing", "approved"}
STATUS_ORDER = {"approved": 0, "testing": 1, "candidate": 2, "deprecated": 3}
SCORING_VERSION = "style-score-v1"
DEFAULT_THRESHOLD = 0.62
DEFAULT_MARGIN = 0.08
DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "styles/catalog.json"


def load_json(path: Path | str):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path | str):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def document_sha256(document):
    payload = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_tag(value):
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def normalized_tags(values, *, field):
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise ValueError(f"{field} must be an array of strings")
    return sorted({tag for item in values if (tag := normalize_tag(item))})


def normalized_weights(catalog):
    raw = catalog.get("selection_weights")
    if not isinstance(raw, dict):
        raise ValueError("style catalog is missing selection_weights")
    weights = {}
    for dimension in DIMENSIONS:
        value = raw.get(dimension)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"selection weight {dimension} must be a non-negative number")
        weights[dimension] = float(value)
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("selection weights must have a positive total")
    return {name: round(value / total, 8) for name, value in weights.items()}


def style_tags(style, dimension):
    profile = style.get("selection_profile", {})
    profile_dimension = profile.get(dimension, {}) if isinstance(profile, dict) else {}
    if not isinstance(profile_dimension, dict):
        raise ValueError(f"{style.get('id', '<unknown>')} selection_profile.{dimension} must be an object")
    positive = profile_dimension.get("best_for", style.get("best_for", []))
    negative = profile_dimension.get("avoid_for", style.get("avoid_for", []))
    return (
        normalized_tags(positive, field=f"{style.get('id')}.best_for"),
        normalized_tags(negative, field=f"{style.get('id')}.avoid_for"),
    )


def score_dimension(signals, positive_tags, negative_tags):
    if not signals:
        return 0.5, [], [], "Sin señales: puntuación neutral 0.500000."
    positives = sorted(set(signals) & set(positive_tags))
    negatives = sorted(set(signals) & set(negative_tags))
    denominator = len(signals)
    positive_ratio = len(positives) / denominator
    negative_ratio = len(negatives) / denominator
    score = max(0.0, min(1.0, 0.5 + 0.5 * positive_ratio - negative_ratio))
    parts = [f"{len(positives)}/{denominator} señales favorables"]
    if negatives:
        parts.append(f"{len(negatives)} conflicto(s)")
    else:
        parts.append("sin conflictos")
    return round(score, 6), positives, negatives, "; ".join(parts) + f"; puntuación {score:.6f}."


def score_one_style(style, signals_by_dimension, weights):
    style_id = style.get("id")
    status = style.get("status")
    if not isinstance(style_id, str) or not style_id:
        raise ValueError("every style requires a non-empty id")
    if status not in STATUS_ORDER:
        raise ValueError(f"{style_id} has unsupported status {status!r}")

    dimensions = []
    weighted_score = 0.0
    all_positive = set()
    all_negative = set()
    for dimension in DIMENSIONS:
        positive_tags, negative_tags = style_tags(style, dimension)
        signals = signals_by_dimension[dimension]
        score, positives, negatives, explanation = score_dimension(signals, positive_tags, negative_tags)
        weighted_score += score * weights[dimension]
        all_positive.update(positives)
        all_negative.update(negatives)
        dimensions.append(
            {
                "dimension": dimension,
                "weight": weights[dimension],
                "score": score,
                "signals": signals,
                "positive_matches": positives,
                "negative_matches": negatives,
                "explanation": explanation,
            }
        )

    eligible = status in ELIGIBLE_STATUSES
    final_score = round(weighted_score, 6)
    eligibility = "elegible" if eligible else f"no elegible por estado {status}"
    explanation = (
        f"{style_id}: {final_score:.6f}; {eligibility}; "
        f"{len(all_positive)} coincidencia(s) y {len(all_negative)} conflicto(s)."
    )
    return {
        "style_id": style_id,
        "style_status": status,
        "version": style.get("version", "0.0.0"),
        "canonical_path": style.get("canonical_path", style_id),
        "score": final_score,
        "eligible": eligible,
        "dimensions": dimensions,
        "positive_matches": sorted(all_positive),
        "negative_matches": sorted(all_negative),
        "explanation": explanation,
    }


def build_decision(
    blueprint,
    catalog,
    *,
    blueprint_sha256=None,
    catalog_sha256=None,
    catalog_path="styles/catalog.json",
    threshold=DEFAULT_THRESHOLD,
    abstention_margin=DEFAULT_MARGIN,
    decision_id=None,
):
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    if (
        isinstance(abstention_margin, bool)
        or not isinstance(abstention_margin, (int, float))
        or not 0 <= abstention_margin <= 1
    ):
        raise ValueError("abstention_margin must be between 0 and 1")

    blueprint_id = blueprint.get("blueprint_id")
    if not isinstance(blueprint_id, str) or not blueprint_id:
        raise ValueError("blueprint_id is required")
    raw_signals = blueprint.get("style_selection_signals")
    if not isinstance(raw_signals, dict):
        raise ValueError("creative blueprint is missing style_selection_signals")
    signals_by_dimension = {
        dimension: normalized_tags(raw_signals.get(dimension, []), field=f"style_selection_signals.{dimension}")
        for dimension in DIMENSIONS
    }
    weights = normalized_weights(catalog)
    styles = catalog.get("styles")
    if not isinstance(styles, list):
        raise ValueError("style catalog styles must be an array")

    ranking = [score_one_style(style, signals_by_dimension, weights) for style in styles]
    ranking.sort(
        key=lambda item: (
            not item["eligible"],
            -item["score"],
            STATUS_ORDER[item["style_status"]],
            item["style_id"],
        )
    )
    eligible = [item for item in ranking if item["eligible"]]
    reasons = []
    selected_style_id = None
    score_margin = None
    if not eligible:
        reasons.append("no_eligible_styles")
        explanation = "Abstención: el catálogo no contiene estilos elegibles."
    else:
        top = eligible[0]
        second = eligible[1] if len(eligible) > 1 else None
        score_margin = round(top["score"] - second["score"], 6) if second else top["score"]
        if top["score"] < threshold:
            reasons.append("below_threshold")
        if second is not None and score_margin < abstention_margin:
            reasons.append("ambiguous_margin")
        if reasons:
            explanation = (
                f"Abstención: {top['style_id']} lidera con {top['score']:.6f}, "
                f"umbral {threshold:.6f} y margen {score_margin:.6f}; "
                f"razones: {', '.join(reasons)}."
            )
        else:
            selected_style_id = top["style_id"]
            explanation = (
                f"Seleccionado {top['style_id']} con {top['score']:.6f}; "
                f"supera el umbral {threshold:.6f} y el margen mínimo {abstention_margin:.6f} "
                f"con margen observado {score_margin:.6f}."
            )

    if decision_id is None:
        suffix = re.sub(r"[^A-Z0-9_-]+", "-", blueprint_id.upper()).strip("-")
        decision_id = f"STYLE-DECISION-{suffix}"
    return {
        "schema_version": "1.0.0",
        "decision_id": decision_id,
        "blueprint_id": blueprint_id,
        "blueprint_sha256": blueprint_sha256 or document_sha256(blueprint),
        "catalog_path": str(catalog_path),
        "catalog_sha256": catalog_sha256 or document_sha256(catalog),
        "scoring_version": SCORING_VERSION,
        "weights": weights,
        "threshold": round(float(threshold), 6),
        "abstention_margin": round(float(abstention_margin), 6),
        "status": "abstained" if reasons else "selected",
        "selected_style_id": selected_style_id,
        "score_margin": score_margin,
        "abstention_reasons": reasons,
        "ranking": ranking,
        "explanation": explanation,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blueprint", required=True, help="Creative blueprint JSON")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Style catalog JSON")
    parser.add_argument("--output", help="Write decision JSON; stdout when omitted")
    parser.add_argument("--decision-id")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--abstention-margin", type=float, default=DEFAULT_MARGIN)
    parser.add_argument("--require-selection", action="store_true", help="Exit 1 when the valid result abstains")
    args = parser.parse_args()

    blueprint_path = Path(args.blueprint).expanduser().resolve()
    catalog_path = Path(args.catalog).expanduser().resolve()
    try:
        decision = build_decision(
            load_json(blueprint_path),
            load_json(catalog_path),
            blueprint_sha256=sha256(blueprint_path),
            catalog_sha256=sha256(catalog_path),
            catalog_path=str(catalog_path),
            threshold=args.threshold,
            abstention_margin=args.abstention_margin,
            decision_id=args.decision_id,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"style decision error: {error}", file=sys.stderr)
        return 2

    payload = json.dumps(decision, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    if args.require_selection and decision["status"] != "selected":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
