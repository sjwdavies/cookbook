#!/usr/bin/env python3
"""
json_to_markdown.py - full drop-in with content-digest incrementals.

- Preserves full rendering: front matter, Ingredients, Method, Notes, Nutrition.
- Adds SHA-256 digest tracking via `source_digest` in front matter.
- Incremental by default; `--force` to rebuild all.
- Single-file mode still supported.
"""
from __future__ import annotations

import json
import sys
import re
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------- Helpers ----------

def kebab(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s\-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "recipe"

def ensure_blank_line(lines: List[str]) -> None:
    if lines and lines[-1].strip() != "":
        lines.append("")

def yaml_escape(v: Any) -> str:
    # Quote if needed
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if any(ch in s for ch in [":", "-", "{", "}", "[", "]", "#", '"', "'", "<", ">", "&"]):
        return json.dumps(s, ensure_ascii=False)
    return s

def fmt_num(val: Optional[float], dp_default: int = 1) -> str:
    if val is None:
        return "—"
    try:
        if abs(val - round(val)) < 1e-9:
            return str(int(round(val)))
        if dp_default == 2:
            return f"{val:.2f}"
        return f"{val:.1f}"
    except Exception:
        return "—"

def json_sha256(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()

def read_front_matter(md_path: Path) -> Tuple[Dict[str, str], int]:
    """Return (front_matter_dict, end_index_line). If no FM, return ({}, -1)."""
    try:
        lines = md_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}, -1
    if not lines or lines[0].strip() != "---":
        return {}, -1
    fm: Dict[str, str] = {}
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            return fm, i
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return {}, -1

# ---------- Rendering ----------

def to_yaml_front_matter(data: Dict[str, Any]) -> List[str]:
    title = str(data.get("title") or "").strip()
    slug = str(data.get("slug") or kebab(title))
    cats = data.get("categories") or []
    if isinstance(cats, str):
        cats = [cats]
    tags = data.get("tags") or []
    audience = data.get("audience") or ""
    source = data.get("_source_path") or ""
    digest = data.get("_source_digest") or ""

    fm: List[str] = []
    fm.append("---")
    fm.append(f"title: {yaml_escape(title)}")
    fm.append(f"slug: {yaml_escape(slug)}")
    if cats:
        fm.append("categories:")
        for c in cats:
            fm.append(f"  - {yaml_escape(str(c))}")
    if tags:
        fm.append("tags:")
        for t in tags:
            fm.append(f"  - {yaml_escape(str(t))}")
    if audience:
        fm.append(f"audience: {yaml_escape(audience)}")
    if source:
        fm.append(f"source: {yaml_escape(source)}")
    if digest:
        fm.append(f"source_digest: {yaml_escape(digest)}")
    fm.append("---")
    fm.append("")
    return fm

def render_section_ingredients(data: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    lines.append("## Ingredients")
    lines.append("")
    ings = data.get("ingredients") or []
    for it in ings:
        qty = str(it.get("quantity") or "").strip()
        unit = str(it.get("unit") or "").strip()
        item = str(it.get("item") or "").strip()
        note = str(it.get("note") or "").strip()
        left = " ".join([p for p in [qty, unit] if p]).strip()
        label = f"- {left} {item}".strip()
        lines.append(label if not note else f"{label}, {note}")
    lines.append("")
    return lines

def render_section_method(data: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    lines.append("## Method")
    lines.append("")
    steps = data.get("method") or []
    for i, step in enumerate(steps, 1):
        s = str(step).strip()
        lines.append(f"{i}. {s}")
    lines.append("")
    return lines

def render_section_notes(data: Dict[str, Any]) -> List[str]:
    notes = data.get("notes") or []
    if not notes:
        return []
    lines: List[str] = []
    lines.append("## Notes")
    lines.append("")
    for n in notes:
        s = str(n).strip()
        lines.append(f"- {s}")
    lines.append("")
    return lines

def render_nutrition_blocks(data: Dict[str, Any]) -> List[str]:
    nutrition = data.get("nutrition") or {}
    if not isinstance(nutrition, dict) or not nutrition:
        return []
    meta = data.get("meta") or {}
    adult = meta.get("adult_rda_percent") or {}
    child = meta.get("child_rda_percent") or {}
    child_band = (meta.get("child_age_band") or "").strip()
    by_band = meta.get("child_rda_percent_by_band") or {}

    lines: List[str] = []
    # Per adult portion table
    lines.append("## Nutrition (per adult portion)")
    lines.append("")
    hdr_child = f"Child %RDA ({child_band})" if child_band else "Child %RDA"
    lines.append(f"| Nutrient | Amount | Adult %RDA | {hdr_child} |")
    lines.append("|---|---:|---:|---:|")

    def row(key: str, label: str, unit: str = ""):
        amt = nutrition.get(key, None)
        a = adult.get(key, None)
        c = child.get(key, None)
        val = fmt_num(amt, 0 if key == "energy_kcal" else (2 if key == "salt_g" else 1))
        if unit and val != "—":
            val = f"{val} {unit}"
        lines.append(f"| {label} | {val} | {fmt_num(a)} | {fmt_num(c)} |")  # noqa: E501

    row("energy_kcal", "Energy (kcal)")
    row("protein_g", "Protein (g)")
    row("carbs_g", "Carbs (g)")
    row("fat_g", "Fat (g)")
    row("salt_g", "Salt (g)")
    lines.append("")

    # Child RDA by band reference table
    if isinstance(by_band, dict) and by_band:
        lines.append("## Child RDA by band (reference)")
        lines.append("")
        lines.append("| Band | Energy % | Protein % | Carbs % | Fat % | Salt % |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for band, vals in by_band.items():
            e = fmt_num(vals.get("energy_kcal"))
            p = fmt_num(vals.get("protein_g"))
            c = fmt_num(vals.get("carbs_g"))
            f = fmt_num(vals.get("fat_g"))
            s = fmt_num(vals.get("salt_g"))
            lines.append(f"| {band} | {e} | {p} | {c} | {f} | {s} |")
        lines.append("")
    return lines

def render_markdown(data: Dict[str, Any]) -> str:
    title = str(data.get("title") or "").strip()
    if not title:
        raise ValueError("Recipe must include a non-empty 'title'")
    slug = str(data.get("slug") or kebab(title))
    data["slug"] = slug  # persist for path decision

    fm = to_yaml_front_matter(data)
    body: List[str] = []

    # Summary (optional)
    summary = str(data.get("summary") or "").strip()
    if summary:
        body.append(summary)
        body.append("")

    body.extend(render_section_ingredients(data))
    body.extend(render_section_method(data))
    body.extend(render_section_notes(data))

    # Nutrition
    nut = render_nutrition_blocks(data)
    if nut:
        ensure_blank_line(body)
        body.extend(nut)

    return "\n".join(fm + body)

# ---------- IO / CLI ----------

def write_markdown(md_path: Path, content: str) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(content, encoding="utf-8")

def compute_output_path(data: Dict[str, Any], out_root: Path) -> Path:
    cats = data.get("categories") or []
    if isinstance(cats, list) and cats:
        cat = kebab(str(cats[0]))
    elif isinstance(cats, str) and cats:
        cat = kebab(cats)
    else:
        cat = "uncategorised"
    slug = data.get("slug") or kebab(str(data.get("title","untitled")))
    return out_root / cat / f"{slug}.md"

def should_rebuild(json_path: Path, md_path: Path, new_digest: str, force: bool) -> bool:
    if force or not md_path.exists():
        return True
    fm, _ = read_front_matter(md_path)
    old_digest = fm.get("source_digest", "")
    if old_digest:
        return old_digest != new_digest
    # No digest recorded yet -> rebuild once to seed digest
    return True

def convert_file(json_path: Path, out_root: Path, force: bool = False) -> Path:
    digest = json_sha256(json_path)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["_source_path"] = str(json_path)
    data["_source_digest"] = digest
    out_md = compute_output_path(data, out_root)

    if should_rebuild(json_path, out_md, digest, force):
        content = render_markdown(data)
        write_markdown(out_md, content)
        print(f"✓ Updated {json_path.name} -> {out_md}")
    else:
        print(f"• Skipped {json_path.name} (no changes)")
    return out_md

def batch_convert(repo_root: Path, force: bool = False) -> None:
    data_dir = repo_root / "data" / "recipes"
    out_root = repo_root / "recipes"
    json_files = sorted(data_dir.glob("*.json"))
    for jf in json_files:
        convert_file(jf, out_root, force=force)

def main(argv: List[str]) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    # Single-file mode: python scripts/json_to_markdown.py src.json dst.md
    if len(argv) == 3 and not argv[1].startswith("--"):
        inp = Path(argv[1])
        outp = Path(argv[2])
        digest = json_sha256(inp)
        data = json.loads(inp.read_text(encoding="utf-8"))
        data["_source_path"] = str(inp)
        data["_source_digest"] = digest
        content = render_markdown(data)
        write_markdown(outp, content)
        print(f"✓ Wrote {outp}")
        return 0

    # Batch mode (incremental by digest). Use --force to rebuild all.
    force = "--force" in argv
    batch_convert(repo_root, force=force)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))