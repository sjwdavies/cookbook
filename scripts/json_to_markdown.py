#!/usr/bin/env python3
import json, re, textwrap, os
from pathlib import Path
from md_utils import format_markdown

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

md = format_markdown(md, width=80)

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