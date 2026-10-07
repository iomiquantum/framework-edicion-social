#!/usr/bin/env python3
"""Read-only ASR pre-QA; never approves takes, edits transcripts, or closes ingest."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata


def normalize(text):
    plain = unicodedata.normalize("NFKD", str(text).casefold())
    return re.findall(r"[a-z0-9]+", "".join(c for c in plain if not unicodedata.combining(c)))


NUMBERS = {
    "cero": 0, "uno": 1, "un": 1, "una": 1, "dos": 2, "tres": 3,
    "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9,
    "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14,
    "quince": 15, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18,
    "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidos": 22,
    "veintitres": 23, "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26,
    "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90,
}
MARKER_WORDS = {"marcador", "markador", "toma", "corregir", "inicio", "aprobada", "aprobado", "descartar"}


def number_at(tokens, index):
    if index >= len(tokens):
        return None
    token = tokens[index][0]
    if token.isdigit():
        return int(token)
    number = NUMBERS.get(token)
    if number is not None and number >= 30 and index + 2 < len(tokens):
        if tokens[index + 1][0] == "y" and 1 <= NUMBERS.get(tokens[index + 2][0], 0) <= 9:
            return number + NUMBERS[tokens[index + 2][0]]
    return number


def analyze(data, duration, first, last, source_sha256=None):
    findings = []

    def finding(code, severity, message, **evidence):
        findings.append({"code": code, "severity": severity, "message": message, **evidence})

    raw = data.get("words") if isinstance(data, dict) else data
    report = {
        "schema_version": "1.0.0", "status": "fail", "source_sha256": source_sha256,
        "source_duration_s": duration, "expected_videos": [f"VIDEO-{n:02d}" for n in range(first, last + 1)],
        "observed_videos": [], "marker_candidates": [], "metrics": {}, "findings": findings,
        "human_review_completed": False, "ingest_ready": False,
        "scope": "ASR reliability only; does not approve takes, audio, corrections or individual editing",
    }
    if not isinstance(raw, list) or not raw:
        finding("WORDS_MISSING", "error", "Expected a nonempty list or an object containing words.")
        return report
    words, tokens = [], []
    invalid = []
    for index, word in enumerate(raw):
        try:
            if not isinstance(word, dict):
                raise ValueError("word must be an object")
            text = word.get("text", word.get("word"))
            if not isinstance(text, str) or not text.strip():
                raise ValueError("text/word must be a nonempty string")
            if isinstance(word.get("start"), bool) or isinstance(word.get("end"), bool):
                raise ValueError("boolean timestamp")
            start, end = float(word["start"]), float(word["end"])
            if not math.isfinite(start) or not math.isfinite(end):
                raise ValueError("non-finite timestamp")
            words.append({"index": index, "text": text, "start": start, "end": end})
            tokens.extend((token, start, end, index) for token in normalize(text))
        except (KeyError, TypeError, ValueError) as error:
            invalid.append({"word_index": index, "reason": str(error)})
    if invalid:
        finding("WORD_INVALID", "error", "Malformed words or timestamps.", count=len(invalid), examples=invalid[:10])
    zero = [w for w in words if w["end"] == w["start"]]
    reversed_words = [w for w in words if w["end"] < w["start"] or w["start"] < 0]
    if reversed_words:
        finding("TIMESTAMP_INVALID_RANGE", "error", "Negative or reversed timestamp ranges.", count=len(reversed_words), examples=reversed_words[:10])
    zero_ratio = len(zero) / len(words) if words else 0
    if zero_ratio >= .05:
        finding("ZERO_DURATION_RATIO", "error" if zero_ratio >= .15 else "warning",
                "Many words have zero duration; alignment needs review.", count=len(zero), ratio=round(zero_ratio, 6), examples=zero[:5])
    regressions, overlaps = [], []
    for before, after in zip(words, words[1:]):
        if after["start"] < before["start"] - .02:
            regressions.append({"before_index": before["index"], "after_index": after["index"],
                                "before_start_s": before["start"], "after_start_s": after["start"],
                                "regression_s": round(before["start"] - after["start"], 6)})
        if after["start"] < before["end"] - .04:
            overlaps.append({"before_index": before["index"], "after_index": after["index"],
                             "start_s": after["start"], "previous_end_s": before["end"]})
    if regressions:
        finding("TIMESTAMPS_NON_MONOTONIC", "error" if any(x["regression_s"] > .10 for x in regressions) else "warning",
                "Word order moves backwards in time; inspect chunk overlaps before cuts.", count=len(regressions), examples=regressions[:10])
    if overlaps:
        finding("WORD_TIME_OVERLAP", "warning", "Adjacent word ranges overlap; ASR chunks may require reconciliation.", count=len(overlaps), examples=overlaps[:10])
    over = [w for w in words if w["end"] > duration + .02 or w["start"] > duration + .02]
    if over:
        maximum = max(max(w["start"], w["end"]) - duration for w in over)
        finding("SOURCE_DURATION_EXCEEDED", "error" if maximum > .10 else "warning",
                "Timestamps exceed source duration.", count=len(over), maximum_overrun_s=round(maximum, 6), examples=over[:10])

    candidates = []
    for i, (token, start, _, index) in enumerate(tokens):
        if token != "video":
            continue
        j = i + 1
        if j < len(tokens) and tokens[j][0] in {"numero", "n"}:
            j += 1
        number = number_at(tokens, j)
        nearby = {t[0] for t in tokens[max(0, i - 4):i + 7]}
        if number is not None and start <= tokens[j][1] <= start + 8:
            candidates.append({"video_id": f"VIDEO-{number:02d}", "start_s": start, "word_index": index,
                               "marker_context": bool(nearby & {"marcador", "markador", "toma"}),
                               "text": " ".join(t[0] for t in tokens[max(0, i - 2):i + 6])})
    observed = sorted({c["video_id"] for c in candidates if c["marker_context"]})
    missing = sorted(set(report["expected_videos"]) - set(observed))
    if missing:
        finding("VIDEO_COVERAGE_MISSING", "error", "Expected video markers are absent or unreadable; verify against source audio.", missing_videos=missing)
    weak = [c for c in candidates if not c["marker_context"]]
    if weak:
        finding("VIDEO_REFERENCE_WITHOUT_MARKER", "warning", "Numbered video references lack marker/take context and do not prove batch coverage.", examples=weak[:10])

    # Require long, diverse phrases and repeated evidence spread in time.
    # Short fillers and marker/correction boilerplate cannot trigger this check.
    repetitions = []
    token_text = [t[0] for t in tokens]
    correction_times = sorted(t[1] for t in tokens if t[0] == "corregir")
    for size in (10, 8, 6):
        positions = defaultdict(list)
        for i in range(len(tokens) - size + 1):
            phrase = tuple(token_text[i:i + size])
            if len(set(phrase)) < 4 or set(phrase) & MARKER_WORDS:
                continue
            # Genuine retakes often repeat long sentences. Their first 20 s
            # after an explicit correction are excluded from loop evidence.
            previous_correction = bisect_right(correction_times, tokens[i][1]) - 1
            if previous_correction >= 0 and tokens[i][1] - correction_times[previous_correction] <= 20:
                continue
            positions[phrase].append(i)
        for phrase, indices in positions.items():
            nonoverlap = []
            for i in indices:
                if not nonoverlap or i >= nonoverlap[-1] + size:
                    nonoverlap.append(i)
            if len(nonoverlap) < 20:
                continue
            times = sorted(tokens[i][1] for i in nonoverlap)
            span = times[-1] - times[0]
            bins = len({int(t // 15) for t in times})
            if span < 60 or bins < 4:
                continue
            share = len(nonoverlap) * size / max(1, len(tokens))
            repetitions.append({"phrase": " ".join(phrase), "occurrences": len(nonoverlap),
                                "start_s": times[0], "end_s": times[-1], "span_s": round(span, 6),
                                "distinct_15s_bins": bins, "token_share": round(share, 6)})
    if repetitions:
        examples = sorted(repetitions, key=lambda x: (x["token_share"], x["occurrences"]), reverse=True)[:3]
        finding("MASSIVE_NGRAM_REPETITION", "error" if examples[0]["token_share"] >= .15 else "warning",
                "Long phrases repeat at least 20 times across >=60 s and >=4 time bins; possible ASR loop, not a take decision.", examples=examples)

    # Time coverage is advisory: silence/pauses can be real, and must be listened to.
    merged = []
    for start, end in sorted((max(0, w["start"]), min(duration, w["end"])) for w in words if 0 <= w["start"] <= min(w["end"], duration) and w["end"] <= duration + .02):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    gaps, cursor = [], 0
    for start, end in merged + [[duration, duration]]:
        if start - cursor >= 15:
            gaps.append({"start_s": cursor, "end_s": start, "duration_s": round(start - cursor, 6)})
        cursor = max(cursor, end)
    if gaps:
        finding("TRANSCRIPT_LONG_GAPS", "warning", "Transcript leaves >=15 s uncovered; may be silence or omitted speech. Audio review required.", count=len(gaps), examples=gaps[:10])
    report.update(observed_videos=observed, marker_candidates=candidates,
                  metrics={"word_count": len(raw), "valid_word_count": len(words), "normalized_token_count": len(tokens),
                           "zero_duration_count": len(zero), "zero_duration_percent": round(zero_ratio * 100, 3),
                           "non_monotonic_count": len(regressions), "adjacent_overlap_count": len(overlaps),
                           "covered_time_s": round(sum(e - s for s, e in merged), 6)},
                  status="fail" if any(f["severity"] == "error" for f in findings) else "warn" if findings else "pass")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--duration", required=True, type=float, help="Source duration in seconds")
    parser.add_argument("--desde", required=True, type=int)
    parser.add_argument("--hasta", required=True, type=int)
    parser.add_argument("--source-sha256", help="Optional declared source SHA-256; never verified by this script")
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration) or args.duration <= 0 or args.desde < 1 or args.hasta < args.desde:
        parser.error("positive finite duration and valid video range required")
    if args.source_sha256 is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", args.source_sha256):
        parser.error("--source-sha256 must contain exactly 64 hex characters")
    try:
        encoded = args.transcript.read_bytes()
        report = analyze(json.loads(encoded), args.duration, args.desde, args.hasta, args.source_sha256)
        report.update(transcript_path=str(args.transcript.resolve()), transcript_sha256=hashlib.sha256(encoded).hexdigest(), source_hash_verified=False)
    except (OSError, ValueError) as error:
        report = {"status": "fail", "findings": [{"code": "TRANSCRIPT_UNREADABLE", "severity": "error", "message": str(error)}],
                  "human_review_completed": False, "ingest_ready": False}
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
