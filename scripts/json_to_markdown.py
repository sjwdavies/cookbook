#!/usr/bin/env python3
import json, sys, pathlib, re

def fmt_ing(i: dict) -> str:
    qty = (i.get("quantity") or "").strip()
    unit = (i.get("unit") or "").strip()
    item = (i.get("item") or "").strip()
    note = (i.get("note") or "").strip()

    parts = []
    if qty: parts.append(qty)
    if unit: parts.append(unit)         # handles "" gracefully
    if item: parts.append(item)
    line = " ".join(parts).strip()
    if note:
        line += f" ({note})"
    return f"- {line}"

def list_block(title: str, items) -> str:
    if not items: return ""
    out = [f"## {title}"]
    for x in items:
        out.append(f"- {x}")
    out.append("")  # trailing newline
    return "\n".join(out)

def to_slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def render_markdown(data: dict) -> str:
    title = data.get("title", "").strip()
    slug = data.get("slug") or to_slug(title)

    serves = data.get("serves", "").strip()
    prep_time = data.get("prep_time", "").strip()
    cook_time = data.get("cook_time", "").strip()
    difficulty = data.get("difficulty", "").strip()

    equipment = data.get("equipment") or []
    tags = data.get("tags") or []
    categories = data.get("categories") or []

    ingredients = data.get("ingredients") or []
    method = data.get("method") or []
    notes = data.get("notes") or []

    # --- YAML front matter ---
    fm_lines = [
        "---",
        f'title: "{title}"',
        f"slug: {slug}",
    ]
    if serves:     fm_lines.append(f'serves: "{serves}"')
    if prep_time:  fm_lines.append(f'prep_time: "{prep_time}"')
    if cook_time:  fm_lines.append(f'cook_time: "{cook_time}"')
    if difficulty: fm_lines.append(f'difficulty: "{difficulty}"')

    if equipment:
        fm_lines.append("equipment:")
        for e in equipment:
            fm_lines.append(f"  - {e}")

    if tags:
        fm_lines.append("tags:")
        for t in tags:
            fm_lines.append(f"  - {t}")

    if categories:
        fm_lines.append("categories:")
        for c in categories:
            fm_lines.append(f"  - {c}")

    fm_lines.append("---\n")

    # --- Body ---
    body = []

    # quick facts list (serves, times, difficulty, tags shown inline too)
    bullets = []
    if serves:     bullets.append(f"- Serves: {serves}")
    if prep_time:  bullets.append(f"- Prep Time: {prep_time}")
    if cook_time:  bullets.append(f"- Cook Time: {cook_time}")
    if equipment:  bullets.append(f"- Equipment: {', '.join(equipment)}")
    if difficulty: bullets.append(f"- Difficulty: {difficulty}")
    if tags:       bullets.append(f"- Tags: {', '.join(tags)}")
    if bullets:
        body.append("\n".join(bullets) + "\n")

    # sections
    body.append("## Ingredients")
    if ingredients:
        for ing in ingredients:
            body.append(fmt_ing(ing))
    else:
        body.append("_No ingredients listed._")
    body.append("")

    body.append(list_block("Method", method))
    if notes:
        body.append(list_block("Notes", notes))

    return "\n".join(fm_lines + body).rstrip() + "\n"

def main():
    if len(sys.argv) != 3:
        print("Usage: json_to_markdown.py <input.json> <output.md>")
        sys.exit(2)
    in_path = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2])

    data = json.loads(in_path.read_text(encoding="utf-8"))

    # Basic sanity checks
    required = ["title", "ingredients", "method"]
    missing = [k for k in required if k not in data]
    if missing:
        raise SystemExit(f"Recipe missing keys: {missing}")

    md = render_markdown(data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")

if __name__ == "__main__":
    main()