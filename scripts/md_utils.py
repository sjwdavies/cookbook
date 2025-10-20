#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown utilities for formatting and link building
Shared by json_to_markdown.py and build_indexes.py
"""

import os
import re
import textwrap
from pathlib import Path

# Repo roots
ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "recipes"


def rel_link(from_file: Path, target_rel_to_recipes: str) -> str:
    """
    Return a POSIX-style relative link from `from_file` to a target under recipes/.

    Parameters
    ----------
    from_file : Path
        The markdown file that will contain the link (absolute or relative to repo root).
    target_rel_to_recipes : str
        The target path *relative to* the recipes/ directory, e.g. "arthur/soup.md".

    Returns
    -------
    str : A relative path string suitable for a Markdown link, using '/' separators.
    """
    target_abs = (RECIPES / target_rel_to_recipes).resolve()
    start_dir = Path(from_file).resolve().parent
    rel = os.path.relpath(target_abs, start=start_dir)
    return rel.replace(os.sep, "/")


def format_markdown(md: str, width: int = 80) -> str:
    """
    Wrap long lines and enforce blanks around headings/lists (markdownlint-friendly).

    - Preserves code blocks (```), tables (| ...), and headings (# ...)
    - Wraps paragraphs and list items to a maximum width
    - Ensures a single blank line around headings and between blocks
    """
    out = []
    in_code = False
    lines = md.splitlines()

    def _wrap_list_item(line: str, width: int) -> str | None:
        line = line.rstrip()
        # Bulleted list: "- " or "* "
        if line.startswith(("- ", "* ")):
            bullet, rest = line[:2], line[2:].strip()
            return textwrap.fill(
                rest,
                width=width,
                initial_indent=bullet,
                subsequent_indent="  ",  # hanging indent
                break_long_words=False,
                break_on_hyphens=False,
            )
        # Numbered list: "1. ", "12. " etc.
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

    for line in lines:
        raw = line.rstrip()

        # Toggle code block preservation
        if raw.strip().startswith("```"):
            in_code = not in_code
            out.append(raw)
            continue

        if in_code:
            out.append(raw)
            continue

        # Leave GitHub-style tables alone
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

    # De-dup trailing blanks and ensure single trailing newline
    cleaned = []
    for l in out:
        if not (cleaned and cleaned[-1] == "" and l == ""):
            cleaned.append(l)
    return ("\n".join(cleaned)).rstrip() + "\n"