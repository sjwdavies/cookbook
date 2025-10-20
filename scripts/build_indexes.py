#!/usr/bin/env python3
from pathlib import Path
import re
import os

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "recipes"

# Build a markdown link path from the file being written to the target under recipes/
from pathlib import Path as _Path

def rel_link(from_file: _Path, target_rel_to_recipes: str) -> str:
    """Return POSIX-style relative link from `from_file` to `recipes/target_rel_to_recipes`."""
    target_abs = (RECIPES / target_rel_to_recipes).resolve()
    start_dir = _Path(from_file).resolve().parent
    rel = os.path.relpath(target_abs, start=start_dir)
    return rel.replace(os.sep, "/")

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
    page_path = RECIPES / "_all.md"
    lines = ["# All Recipes", ""]
    for p in sorted(all_recipe_files()):
        rel = p.relative_to(RECIPES)
        title = load_title(p)
        lines.append(f"- [{title}]({rel_link(page_path, rel.as_posix())})")
    write(RECIPES / "_all.md", "\n".join(lines))

def build_category_indexes():
    for cat_dir in sorted(RECIPES.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name in ("tags",):
            continue
        if not any(cat_dir.glob("*.md")):
            continue
        index_path = cat_dir / "_index.md"
        lines = [f"# {cat_dir.name.replace('-', ' ').title()}", ""]
        for p in sorted(cat_dir.glob("*.md")):
            if p.name in ("_index.md",):
                continue
            title = load_title(p)
            rel = p.relative_to(RECIPES)
            lines.append(f"- [{title}]({rel_link(index_path, rel.as_posix())})")
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
    tags_index = RECIPES / "tags.md"
    lines = ["# Tags", ""]
    for t in sorted(tag_map.keys()):
        lines.append(f"- [{t}]({rel_link(tags_index, f'tags/{t}.md')}) ({len(tag_map[t])})")
    write(RECIPES / "tags.md", "\n".join(lines))
    tag_dir = RECIPES / "tags"
    for t, files in tag_map.items():
        tag_page = RECIPES / 'tags' / f"{t}.md"
        lines = [f"# {t.title()}", ""]
        for p in sorted(files):
            title = load_title(p)
            rel = p.relative_to(RECIPES)
            lines.append(f"- [{title}]({rel_link(tag_page, rel.as_posix())})")
        write(tag_dir / f"{t}.md", "\n".join(lines))

def main():
    build_all()
    build_category_indexes()
    build_tags()
    print("Indexes built.")

if __name__ == "__main__":
    main()
