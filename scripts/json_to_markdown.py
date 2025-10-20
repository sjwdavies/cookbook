#!/usr/bin/env python3
"""
json_to_markdown.py

Usage:
  # Batch mode (used by CI): scans data/recipes and writes to recipes/
  python scripts/json_to_markdown.py

  # Single-file mode (local testing)
  python scripts/json_to_markdown.py <input.json> <output.md>
"""
import json, sys, pathlib, re, itertools
from typing import Iterable, Dict, Any, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "recipes"
OUT_DIR = ROOT / "recipes"

# ---------------- formatting helpers ----------------

def _as_list(v) -> List[str]:
    if v is None:
        return []
    if isinstance(v, str):
        s = v.strip()
        return [s] if s else []
    if isinstance(v, Iterable):
        return [str(x).strip() for x in v if str(x).strip()]
    return []

def to_slug(title: str) -> str:
    s = (title or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "untitled"

def fmt_ing(i: Dict[str, Any]) -> str:
    qty  = str(i.get("quantity") or "").strip()
    unit = str(i.get("unit") or "").strip()
    item = str(i.get("item") or "").strip()
    note = str(i.get("note") or "").strip()

    parts = []
    if qty: parts.append(qty)
    if unit: parts.append(unit)
    if item: parts.append(item)
    line = " ".join(parts).strip()
    if note:
        line += f" ({note})"
    return f"- {line or '_unspecified_'}"

def list_block(title: str, items: Iterable[str]) -> str:
    items = [str(x).strip() for x in items if str(x).strip()]
    if not items:
        return ""
    out = [f"## {title}"]
    out.extend(f"- {x}" for x in items)
    out.append("")  # trailing newline
    return "\n".join(out)

def render_markdown(data: Dict[str, Any]) -> str:
    title = str(data.get("title") or "").strip()
    if not title:
        raise ValueError("Recipe must include a non-empty 'title'")

    slug = str(data.get("slug") or "").strip() or to_slug(title)

    serves     = str(data.get("serves") or "").strip()
    prep_time  = str(data.get("prep_time") or "").strip()
    cook_time  = str(data.get("cook_time") or "").strip()
    difficulty = str(data.get("difficulty") or "").strip()

    equipment  = _as_list(data.get("equipment"))
    tags       = _as_list(data.get("tags"))
    categories = _as_list(data.get("categories"))

    ingredients = data.get("ingredients") or []
    if not isinstance(ingredients, list):
        raise ValueError("'ingredients' must be a list")
    method = data.get("method") or []
    if not isinstance(method, list):
        raise ValueError("'method' must be a list")
    notes  = _as_list(data.get("notes"))

    # ---------- YAML front matter ----------
    fm = ["---",
          f'title: "{title.replace(chr(34), "\\\"")}"',
          f"slug: {slug}"]
    if serves:     fm.append(f'serves: "{serves}"')
    if prep_time:  fm.append(f'prep_time: "{prep_time}"')
    if cook_time:  fm.append(f'cook_time: "{cook_time}"')
    if difficulty: fm.append(f'difficulty: "{difficulty}"')

    if equipment:
        fm.append("equipment:")
        fm.extend(f"  - {e}" for e in equipment)
    if tags:
        fm.append("tags:")
        fm.extend(f"  - {t}" for t in tags)
    if categories:
        fm.append("categories:")
        fm.extend(f"  - {c}" for c in categories)
    fm.append("---\n")

    # ---------- Body ----------
    bullets = []
    if serves:     bullets.append(f"- Serves: {serves}")
    if prep_time:  bullets.append(f"- Prep Time: {prep_time}")
    if cook_time:  bullets.append(f"- Cook Time: {cook_time}")
    if equipment:  bullets.append(f"- Equipment: {', '.join(equipment)}")
    if difficulty: bullets.append(f"- Difficulty: {difficulty}")
    if tags:       bullets.append(f"- Tags: {', '.join(tags)}")

    body: List[str] = []
    if bullets:
        body.append("\n".join(bullets) + "\n")

    body.append("## Ingredients")
    if ingredients:
        body.extend(fmt_ing(i) for i in ingredients)
    else:
        body.append("_No ingredients listed._")
    body.append("")

    body.append(list_block("Method", method))
    if notes:
        body.append(list_block("Notes", notes))

    return "\n".join(itertools.chain(fm, body)).rstrip() + "\n"

# ---------------- single & batch modes ----------------

def convert_file(in_path: pathlib.Path, out_path: pathlib.Path) -> None:
    data = json.loads(in_path.read_text(encoding="utf-8"))
    md = render_markdown(data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")

def batch_convert() -> int:
    if not DATA_DIR.exists():
        print(f"[warn] {DATA_DIR} does not exist; nothing to do")
        return 0

    json_files = sorted(DATA_DIR.rglob("*.json"))
    # Skip example files (e.g., example.json, example-*.json, _example.json)
    json_files = [
        f for f in json_files
        if not (
            f.name.lower().startswith("example") or
            f.name.lower() == "_example.json"
        )
    ]
    if not json_files:
        print(f"[warn] No JSON files found under {DATA_DIR}")
        return 0

    ok = 0
    for src in json_files:
        try:
            data = json.loads(src.read_text(encoding="utf-8"))
            title = str(data.get("title") or "").strip()
            slug  = str(data.get("slug") or "").strip() or to_slug(title or src.stem)
            cats  = _as_list(data.get("categories"))
            category = cats[0].lower() if cats else "uncategorised"
            out_md = OUT_DIR / category / f"{slug}.md"
            convert_file(src, out_md)
            print(f"[ok] {src.relative_to(ROOT)} → {out_md.relative_to(ROOT)}")
            ok += 1
        except Exception as e:
            print(f"[fail] {src.relative_to(ROOT)}: {e}")
    return 0 if ok == len(json_files) else 1

def main() -> int:
    if len(sys.argv) == 1:
        # Batch mode for CI
        return batch_convert()
    elif len(sys.argv) == 3:
        # Single-file mode
        in_path = pathlib.Path(sys.argv[1]).resolve()
        out_path = pathlib.Path(sys.argv[2]).resolve()
        convert_file(in_path, out_path)
        print(f"[ok] {in_path} → {out_path}")
        return 0
    else:
        print("Usage: json_to_markdown.py <input.json> <output.md>")
        return 2

if __name__ == "__main__":
    sys.exit(main())