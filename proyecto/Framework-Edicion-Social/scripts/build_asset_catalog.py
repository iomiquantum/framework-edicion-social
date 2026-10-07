#!/usr/bin/env python3
import hashlib
import html
import json
from collections import Counter
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "library"
CATALOG = LIBRARY / "catalog.json"
MARKDOWN = LIBRARY / "CATALOGO.md"
HTML = LIBRARY / "catalogo.html"


def load_catalog():
    with CATALOG.open(encoding="utf-8") as handle:
        return json.load(handle)


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def validate_assets(assets):
    seen = set()
    for asset in assets:
        asset_id = asset["id"]
        if asset_id in seen:
            raise ValueError(f"Duplicate asset id: {asset_id}")
        seen.add(asset_id)
        path = LIBRARY / asset["file"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing catalog asset: {path}")
        actual = digest(path)
        if actual != asset["sha256"]:
            raise ValueError(f"Hash mismatch for {asset_id}: {actual}")


def build_markdown(catalog):
    assets = catalog["assets"]
    counts = Counter(asset["type"] for asset in assets)
    lines = [
        "# Catálogo maestro de recursos",
        "",
        f"Generado desde `library/catalog.json` · {len(assets)} recursos · actualización {catalog['updated_at']}.",
        "",
        "Este índice es para consulta humana. `catalog.json` es la fuente de verdad y los proyectos conservan una copia local de cada recurso utilizado.",
        "",
        "## Resumen",
        "",
        "| Tipo | Cantidad |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{kind}` | {counts[kind]} |" for kind in sorted(counts))
    lines.extend([
        "",
        "## Recursos",
        "",
        "| ID | Tipo | Nombre | Descripción | Política | Usos | Archivo |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ])
    for asset in sorted(assets, key=lambda item: (item["type"], item["id"])):
        description = asset["description"].replace("|", "\\|")
        lines.append(
            f"| `{asset['id']}` | `{asset['type']}` | {asset['name']} | {description} | "
            f"`{asset['reuse']['policy']}` | {asset['reuse']['usage_count']} | "
            f"[`{asset['file']}`]({asset['file']}) |"
        )
    lines.extend([
        "",
        "## Regla de consulta",
        "",
        "Antes de generar, buscar por intención, etiquetas, `best_for` y restricciones. Reutilizar solo cuando coincida el significado; una semejanza visual no basta para marcas, datos o evidencia.",
        "",
        "Regenerar este archivo y la galería mediante:",
        "",
        "```bash",
        "python3 scripts/build_asset_catalog.py",
        "```",
        "",
    ])
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")


def media_preview(asset):
    src = quote(asset["file"])
    if asset["type"] in {"icon", "image", "logo"}:
        return f'<div class="preview checker"><img src="{src}" alt=""></div>'
    if asset["type"] in {"sfx", "bgm"}:
        return f'<div class="preview audio"><audio controls preload="none" src="{src}"></audio></div>'
    return '<div class="preview placeholder">Sin previsualización</div>'


def build_html(catalog):
    cards = []
    types = sorted({asset["type"] for asset in catalog["assets"]})
    for asset in sorted(catalog["assets"], key=lambda item: (item["type"], item["id"])):
        search_text = " ".join([
            asset["id"],
            asset["name"],
            asset["description"],
            *asset["semantic_tags"],
            *asset["best_for"],
            *asset["avoid_for"],
        ]).lower()
        tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in asset["semantic_tags"][:6])
        cards.append(f'''
        <article class="card" data-type="{html.escape(asset['type'])}" data-search="{html.escape(search_text, quote=True)}">
          {media_preview(asset)}
          <div class="body">
            <div class="meta"><code>{html.escape(asset['id'])}</code><b>{html.escape(asset['type'])}</b></div>
            <h2>{html.escape(asset['name'])}</h2>
            <p>{html.escape(asset['description'])}</p>
            <div class="tags">{tags}</div>
            <dl>
              <div><dt>Reutilización</dt><dd>{html.escape(asset['reuse']['policy'])}</dd></div>
              <div><dt>Usos</dt><dd>{asset['reuse']['usage_count']}</dd></div>
              <div><dt>Estado</dt><dd>{html.escape(asset['status'])}</dd></div>
            </dl>
            <a href="{quote(asset['file'])}">{html.escape(asset['file'])}</a>
          </div>
        </article>''')
    options = "".join(f'<option value="{html.escape(kind)}">{html.escape(kind)}</option>' for kind in types)
    document = f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Catálogo maestro de recursos</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background:#0b1020; color:#f6f7fb; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; }}
    header {{ position:sticky; top:0; z-index:2; padding:24px clamp(18px,4vw,56px); background:rgba(11,16,32,.94); backdrop-filter:blur(18px); border-bottom:1px solid #29314a; }}
    h1 {{ margin:0 0 7px; font-size:clamp(24px,4vw,42px); }} header p {{ margin:0; color:#abb5ce; }}
    .controls {{ display:flex; gap:10px; margin-top:18px; }} input,select {{ min-height:44px; border:1px solid #3a4563; border-radius:12px; background:#141b30; color:white; padding:0 14px; font:inherit; }} input {{ flex:1; }}
    main {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(285px,1fr)); gap:18px; padding:26px clamp(18px,4vw,56px) 60px; }}
    .card {{ overflow:hidden; border:1px solid #29314a; border-radius:18px; background:#12192c; box-shadow:0 12px 32px rgba(0,0,0,.18); }}
    .preview {{ min-height:155px; display:grid; place-items:center; background:linear-gradient(135deg,#1b2541,#101629); }}
    .checker {{ background-color:#e9edf6; background-image:linear-gradient(45deg,#cbd3e2 25%,transparent 25%),linear-gradient(-45deg,#cbd3e2 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#cbd3e2 75%),linear-gradient(-45deg,transparent 75%,#cbd3e2 75%); background-size:24px 24px; background-position:0 0,0 12px,12px -12px,-12px 0; }}
    .preview img {{ width:110px; height:110px; object-fit:contain; filter:drop-shadow(0 7px 14px rgba(0,0,0,.25)); }} audio {{ width:88%; }}
    .body {{ padding:18px; }} .meta {{ display:flex; justify-content:space-between; align-items:center; gap:10px; color:#aeb9d5; }} .meta b {{ color:#56d8c7; text-transform:uppercase; font-size:12px; letter-spacing:.08em; }}
    h2 {{ margin:12px 0 8px; font-size:20px; }} .body p {{ color:#c7cee0; line-height:1.48; min-height:64px; }}
    .tags {{ display:flex; flex-wrap:wrap; gap:6px; }} .tags span {{ padding:5px 8px; border-radius:999px; background:#232d49; color:#cbd5ee; font-size:12px; }}
    dl {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:16px 0; }} dl div {{ min-width:0; }} dt {{ color:#7f8baa; font-size:11px; }} dd {{ margin:3px 0 0; overflow:hidden; text-overflow:ellipsis; font-size:13px; }}
    a {{ color:#69d9ff; word-break:break-all; }} .hidden {{ display:none; }}
    @media (max-width:560px) {{ .controls {{ flex-direction:column; }} dl {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Biblioteca maestra</h1>
    <p>{len(catalog['assets'])} recursos reutilizables · actualización {html.escape(catalog['updated_at'])}</p>
    <div class="controls">
      <input id="q" type="search" placeholder="Buscar por intención, nombre, ID o etiqueta…" autofocus>
      <select id="type"><option value="">Todos los tipos</option>{options}</select>
    </div>
  </header>
  <main id="grid">{''.join(cards)}</main>
  <script>
    const q=document.querySelector('#q'), type=document.querySelector('#type'), cards=[...document.querySelectorAll('.card')];
    function filter() {{ const term=q.value.trim().toLowerCase(), kind=type.value; cards.forEach(card=>card.classList.toggle('hidden',!!((term&&!card.dataset.search.includes(term))||(kind&&card.dataset.type!==kind)))); }}
    q.addEventListener('input',filter); type.addEventListener('change',filter);
  </script>
</body>
</html>'''
    HTML.write_text(document, encoding="utf-8")


def main():
    catalog = load_catalog()
    validate_assets(catalog["assets"])
    build_markdown(catalog)
    build_html(catalog)
    print(f"OK: {len(catalog['assets'])} assets -> {MARKDOWN.name}, {HTML.name}")


if __name__ == "__main__":
    main()
