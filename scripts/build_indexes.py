#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "recipes"

def load_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"^#\s+(.+)$", text, flags=re.M)
    return m.group(1).strip() if m else path.stem.replace("-", " ").title()

def all_recipe_files():
    for p in RECIPES.rglob("*.md"):
        if p.name in ("index.md", "_all.md", "tags.md") or "tags/" in str(p):
            continue
        yield p

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")

def build_all():
    lines = ["# All Recipes", ""]
    for p in sorted(all_recipe_files()):
        rel = p.relative_to(RECIPES)
        title = load_title(p)
        lines.append(f"- [{title}]({rel.as_posix()})")
    write(RECIPES / "_all.md", "\n".join(lines))

def build_category_indexes():
    for cat_dir in sorted(RECIPES.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name in ("tags",):
            continue
        if not any(cat_dir.glob("*.md")):
            continue
        lines = [f"# {cat_dir.name.replace('-', ' ').title()}", ""]
        for p in sorted(cat_dir.glob("*.md")):
            if p.name in ("_index.md",):
                continue
            title = load_title(p)
            rel = p.relative_to(RECIPES)
            lines.append(f"- [{title}]({rel.as_posix()})")
        write(cat_dir / "_index.md", "\n".join(lines))

def build_tags():
    tag_map = {}
    for p in all_recipe_files():
        text = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^\-\s*Tags:\s*(.+)$", text, flags=re.M | re.I)
        if not m:
            continue
        tags = [t.strip().lower() for t in m.group(1).split(",") if t.strip()]
        for t in tags:
            tag_map.setdefault(t, []).append(p)
    lines = ["# Tags", ""]
    for t in sorted(tag_map.keys()):
        lines.append(f"- [{t}](tags/{t}.md) ({len(tag_map[t])})")
    write(RECIPES / "tags.md", "\n".join(lines))
    tag_dir = RECIPES / "tags"
    for t, files in tag_map.items():
        lines = [f"# {t.title()}", ""]
        for p in sorted(files):
            title = load_title(p)
            rel = p.relative_to(RECIPES)
            lines.append(f"- [{title}]({rel.as_posix()})")
        write(tag_dir / f"{t}.md", "\n".join(lines))

def main():
    build_all()
    build_category_indexes()
    build_tags()
    print("Indexes built.")

if __name__ == "__main__":
    main()
