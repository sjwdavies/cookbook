#!/usr/bin/env python3
import json, re, textwrap, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "recipes"
RECIPES = ROOT / "recipes"

TEMPLATE = """# {title}

- Serves: {serves}
- Prep Time: {prep_time}
- Cook Time: {cook_time}
- Equipment: {equipment}
- Difficulty: {difficulty}
- Tags: {tags}

## Ingredients

{ingredients_md}

## Method

{method_md}

## Notes

{notes_md}

## Nutrition (Per Portion)

| Nutrient | Amount | %RDA |
|----------|--------|------|
| Energy   | {kcal_a} | {rda_kcal_a} |
| Protein  | {p_a} | {rda_p_a} |
| Carbs    | {c_a} | {rda_c_a} |
| Fat      | {f_a} | {rda_f_a} |
| Salt     | {na_a} | {rda_na_a} |
"""

def render(md, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")

def fmt(val, suffix=""):
    if val is None or val == "":
        return "N/A"
    return f"{val}{suffix}"

# --- Markdown post-processing to satisfy markdownlint (MD013, MD022, MD032) ---
def format_markdown(md: str, width: int = 80) -> str:
    """
    Wrap long lines and enforce blanks around headings/lists.

    - Preserves code blocks (```), tables (| ...), and headings (# ...)
    - Wraps paragraphs and list items to a maximum width
    - Ensures a single blank line around headings and between blocks
    """
    out = []
    in_code = False

    lines = md.splitlines()
    for line in lines:
        raw = line.rstrip()

        # toggle code block preservation
        if raw.strip().startswith("```"):
            in_code = not in_code
            out.append(raw)
            continue

        if in_code:
            out.append(raw)
            continue

        # leave GitHub-style tables alone
        if raw.strip().startswith("|"):
            out.append(raw)
            continue

        # Headings: ensure blank line before/after, no wrapping
        if re.match(r"^\s*#{1,6}\s", raw):
            if out and out[-1] != "":
                out.append("")
            out.append(raw)
            out.append("")
            continue

        # Blank lines: collapse multiples
        if raw.strip() == "":
            if out and out[-1] != "":
                out.append("")
            continue

        # List items: wrap with proper hanging indent
        def _wrap_list_item(line: str, width: int) -> str | None:
            line = line.rstrip()
            # bullets: "- " or "* "
            if line.startswith(("- ", "* ")):
                bullet, rest = line[:2], line[2:].strip()
                return textwrap.fill(
                    rest,
                    width=width,
                    initial_indent=bullet,
                    subsequent_indent="  ",
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            # numbered list: "1. ", "12. " etc.
            m = re.match(r"^(\s*)(\d+\. )(.+)$", line)
            if m:
                indent, num, rest = m.groups()
                initial = f"{indent}{num}"
                return textwrap.fill(
                    rest.strip(),
                    width=width,
                    initial_indent=initial,
                    subsequent_indent=" " * len(initial),
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            return None

        wrapped_li = _wrap_list_item(raw, width)
        if wrapped_li is not None:
            out.append(wrapped_li)
            continue

        # Paragraph text: wrap
        out.append(
            textwrap.fill(
                raw.strip(),
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )

    # de-dup trailing blanks and ensure single trailing newline
    cleaned = []
    for l in out:
        if not (cleaned and cleaned[-1] == "" and l == ""):
            cleaned.append(l)
    return ("\n".join(cleaned)).rstrip() + "\n"

def main():
    # collect expected markdown paths
    expected_paths = set()

    for js in DATA.rglob("*.json"):
        with open(js, encoding="utf-8") as f:
            obj = json.load(f)
        title = obj["title"]
        category = obj.get("category", "uncategorised").lower().replace(" ", "-")
        slug = obj.get("slug") or js.stem.lower().replace(" ", "-")
        out_path = RECIPES / category / f"{slug}.md"
        expected_paths.add(out_path)

        # ingredients
        ingredients = obj.get("ingredients", [])
        ingredients_md = "\n".join(f"- {i}" for i in ingredients) or "N/A"

        # method
        method = obj.get("method", [])
        method_md = "\n".join(f"{i+1}. {step}" for i, step in enumerate(method)) or "N/A"

        notes_md = obj.get("notes", "N/A")

        md = TEMPLATE.format(
            title=title,
            primary_category=category,
            serves=obj.get("serves","N/A"),
            prep_time=obj.get("prep_time","N/A"),
            cook_time=obj.get("cook_time","N/A"),
            equipment=", ".join(obj.get("equipment", [])) or "N/A",
            difficulty=obj.get("difficulty","Easy"),
            tags=", ".join(obj.get("tags", [])) or "N/A",
            ingredients_md=ingredients_md,
            method_md=method_md,
            notes_md=notes_md,
            kcal_a=fmt(obj.get("nutrition",{}).get("energy_kcal"), " kcal"),
            rda_kcal_a=fmt(obj.get("meta",{}).get("adult_rda_percent",{}).get("energy_kcal"), "%"),
            p_a=fmt(obj.get("nutrition",{}).get("protein_g"), " g"),
            rda_p_a=fmt(obj.get("meta",{}).get("adult_rda_percent",{}).get("protein_g"), "%"),
            c_a=fmt(obj.get("nutrition",{}).get("carbs_g"), " g"),
            rda_c_a=fmt(obj.get("meta",{}).get("adult_rda_percent",{}).get("carbs_g"), "%"),
            f_a=fmt(obj.get("nutrition",{}).get("fat_g"), " g"),
            rda_f_a=fmt(obj.get("meta",{}).get("adult_rda_percent",{}).get("fat_g"), "%"),
            na_a=fmt(obj.get("nutrition",{}).get("salt_g"), " g"),
            rda_na_a=fmt(obj.get("meta",{}).get("adult_rda_percent",{}).get("salt_g"), "%"),
        )

        md = format_markdown(md, width=80)
        render(md, out_path)

    # cleanup: delete any .md in recipes/ with no JSON source
    for md in RECIPES.rglob("*.md"):
        if md.name in ("_all.md", "tags.md") or md.parent.name == "tags":
            continue
        if md not in expected_paths:
            print(f"Removing stale recipe {md}")
            md.unlink()

if __name__ == "__main__":
    main()