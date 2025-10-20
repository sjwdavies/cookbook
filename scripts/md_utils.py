#!/usr/bin/env python3
"""
Markdown utilities for formatting and link building.
Shared by json_to_markdown.py and build_indexes.py
"""

import os, re, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "recipes"

def rel_link(from_file: Path, target_rel_to_recipes: str) -> str:
    """Return POSIX-style relative link from `from_file` to a target under recipes/."""
    target_abs = (RECIPES / target_rel_to_recipes).resolve()
    start_dir = Path(from_file).resolve().parent
    rel = os.path.relpath(target_abs, start=start_dir)
    return rel.replace(os.sep, "/")

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

    def _wrap_list_item(line: str, width: int) -> str | None:
        line = line.rstrip()
        if line.startswith(("- ", "* ")):
            bullet, rest = line[:2], line[2:].strip()
            return textwrap.fill(
                rest, width=width,
                initial_indent=bullet,
                subsequent_indent="  ",
                break_long_words=False,
                break_on_hyphens=False,
            )
        m = re.match(r"^(\s*)(\d+\. )(.+)$", line)
        if m:
            indent, num, rest = m.groups()
            initial = f"{indent}{num}"
            return textwrap.fill(
                rest.strip(), width=width,
                initial_indent=initial,
                subsequent_indent=" " * len(initial),
                break_long_words=False,
                break_on_hyphens=False,
            )
        return None

    for line in lines:
        raw = line.rstrip()
        if raw.strip().startswith("```"):
            in_code = not in_code
            out.append(raw)
            continue
        if in_code:
            out.append(raw)
            continue
        if raw.strip().startswith("|"):
            out.append(raw)
            continue
        if re.match(r"^\s*#{1,6}\s", raw):
            if out and out[-1] != "":
                out.append("")
            out.append(raw)
            out.append("")
            continue
        if raw.strip() == "":
            if out and out[-1] != "":
                out.append("")
            continue
        wrapped_li = _wrap_list_item(raw, width)
        if wrapped_li is not None:
            out.append(wrapped_li)
            continue
        out.append(textwrap.fill(
            raw.strip(), width=width,
            break_long_words=False, break_on_hyphens=False
        ))

    cleaned = []
    for l in out:
        if not (cleaned and cleaned[-1] == "" and l == ""):
            cleaned.append(l)
    return ("\n".join(cleaned)).rstrip() + "\n"