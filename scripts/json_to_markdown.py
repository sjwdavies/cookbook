#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "recipes"
OUT_DIR = ROOT / "recipes"

TEMPLATE = '''# {title}

- Category: {primary_category}
- Serves: {serves}
- Prep time: {prep_time}
- Cook time: {cook_time}
- Equipment: {equipment}
- Difficulty: {difficulty}
- Tags: {tags}

## Ingredients
{ingredients_md}

## Method
{method_md}

## Notes
{notes_md}

## Nutrition (per adult portion)
- Energy: {kcal_a}  —  % RDA (Adult): {rda_kcal_a}
- Protein: {p_a}  —  % RDA: {rda_p_a}
- Carbs: {c_a}  —  % RDA: {rda_c_a}
- Fat: {f_a}  —  % RDA: {rda_f_a}
- Salt: {na_a}  —  % RDA: {rda_na_a}  (target ≤6 g/day)
'''.rstrip() + "\n"

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s

def render(md, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")

def main():
    json_files = sorted(DATA_DIR.glob("*.json"))
    if not json_files:
        print("No JSON recipes found.")
        return
    for jf in json_files:
        obj = json.loads(jf.read_text(encoding="utf-8"))
        title = obj.get("title", "Untitled")
        categories = obj.get("categories", ["uncategorised"])
        primary = categories[0]
        # Build ingredient lines
        ing_lines = []
        for ing in obj.get("ingredients", []):
            qty = ing.get("quantity","")
            unit = ing.get("unit","")
            item = ing.get("item","")
            note = ing.get("note","")
            line = f"- {qty} {unit} {item}".replace("  ", " ").strip()
            if note:
                line += f", {note}"
            ing_lines.append(line)
        ingredients_md = "\n".join(ing_lines) if ing_lines else "- (none)"
        method_md = "\n".join([f"{i+1}. {step}" for i, step in enumerate(obj.get("method", []))]) or "1. (steps pending)"
        notes_md = "\n".join([f"- {n}" for n in obj.get("notes", [])]) or "- (none)"
        equip = ", ".join(obj.get("equipment", []))
        tags = ", ".join(obj.get("tags", []))
        # Nutrition placeholders
        def fmt(x, unit=""):
            return "N/A" if x in (None, "",) else (f"{x}{unit}")
        md = TEMPLATE.format(
            title=title,
            primary_category=primary,
            serves=obj.get("serves","N/A"),
            prep_time=obj.get("prep_time","N/A"),
            cook_time=obj.get("cook_time","N/A"),
            equipment=equip or "N/A",
            difficulty=obj.get("difficulty","Easy"),
            tags=tags or "N/A",
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
        out_path = OUT_DIR / primary / f"{obj.get('slug') or slugify(title)}.md"
        render(md, out_path)
        print("Generated", out_path)

if __name__ == "__main__":
    main()
