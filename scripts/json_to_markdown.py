#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import os
from pathlib import Path

from md_utils import format_markdown, ROOT, RECIPES

# Source of truth
DATA = ROOT / "data" / "recipes"

# Minimal template — adapt fields to your JSON schema as needed
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
"""


def render(md: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")


def _fmt(val, suffix: str = "") -> str:
    if val is None or val == "":
        return "N/A"
    return f"{val}{suffix}"


def _slug_from_title(title: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9 -]", "", title).strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s


def main():
    # Track the markdown files we expect (to delete stale ones later)
    expected_paths: set[Path] = set()

    for js in DATA.rglob("*.json"):
        with open(js, encoding="utf-8") as f:
            obj = json.load(f)

        title = obj.get("title") or js.stem.replace("-", " ").title()
        category = (obj.get("category") or "uncategorised").strip().lower().replace(" ", "-")
        slug = (obj.get("slug") or _slug_from_title(title)).lower()

        out_path = RECIPES / category / f"{slug}.md"
        expected_paths.add(out_path)

        # Ingredients
        ingredients = obj.get("ingredients", [])
        ingredients_md = "\n".join(f"- {i}" for i in ingredients) or "N/A"

        # Method
        method = obj.get("method", [])
        method_md = "\n".join(f"{i+1}. {step}" for i, step in enumerate(method)) or "N/A"

        # Notes
        notes_md = obj.get("notes", "N/A")

        # Equipment list to CSV
        equipment_csv = ", ".join(obj.get("equipment", [])) or "N/A"

        # Tags list to CSV (lowercase for consistency with index builder)
        tags_csv = ", ".join([str(t).strip().lower() for t in obj.get("tags", [])]) or "N/A"

        md = TEMPLATE.format(
            title=title,
            serves=obj.get("serves", "N/A"),
            prep_time=obj.get("prep_time", "N/A"),
            cook_time=obj.get("cook_time", "N/A"),
            equipment=equipment_csv,
            difficulty=obj.get("difficulty", "Easy"),
            tags=tags_csv,
            ingredients_md=ingredients_md,
            method_md=method_md,
            notes_md=notes_md,
        )

        # Wrap to satisfy markdownlint (MD013 etc.)
        md = format_markdown(md, width=80)
        render(md, out_path)

    # Cleanup: delete any recipe .md with no JSON source
    for md in RECIPES.rglob("*.md"):
        # Keep indexes and tag pages; recipes live under category folders
        if md.name in ("_all.md", "tags.md") or md.parent.name == "tags":
            continue
        if md not in expected_paths:
            print(f"Removing stale recipe {md}")
            md.unlink(missing_ok=True)

    print("JSON → Markdown sync complete; stale recipes removed.")


if __name__ == "__main__":
    main()