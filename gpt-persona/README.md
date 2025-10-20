# Taylor‑Davies Recipe Architect — Modular Persona Pack v2.1.0

This release fully complies with markdownlint rules **MD001–MD048** and provides
a modular persona setup for ChatGPT.

## Files Overview

```text
README.md
tdra_instructions_core_v2.1.md
/modules/persona_nutrition_addendum_v1.1.md
/reference/nutrition_reference_uk_2025.csv
/reference/rda_reference_uk_2025.json
/schema/recipe_schema.json
```

## Setup in ChatGPT

1. Open ChatGPT → **Explore GPTs** → **Create** → **Configure**.
2. Name: **Taylor‑Davies Recipe Architect**.
3. Paste the contents of `tdra_instructions_core_v2.1.md` into the Instructions
   box.
4. Upload all other files under **Knowledge**.
5. Enable **Code Interpreter** and disable other tools.
6. Save the GPT.

## Key Features

- Outputs **summary → JSON → Markdown**.
- Markdown always follows markdownlint **MD001–MD048**.
- Nutrition derived from reference CSV and JSON.
- Computes per‑portion macros and %RDA for adults and children.

## Example Prompt

> Butter chicken for 2 adults and 1 child (18 months), mild spice, 45 minutes,
> hob only, no nuts.

The persona will ask clarifying questions, then produce clean Markdown and JSON.

## Versioning

Core v2.1 • Nutrition module v1.1

## License

Use freely within Taylor‑Davies family projects. Credit required for reuse.

---

# Appendix: Markdownlint Rule Summary

| ID | Description |
|----|--------------|
| MD001 | Heading levels should only increment by one level at a time |
| MD002 | First heading should be a top-level heading |
| MD003 | Heading style |
| MD004 | Unordered list style |
| MD005 | List indentation |
| MD006 | Consider starting bulleted lists at the beginning of the line |
| MD007 | Unordered list indentation |
| MD009 | No trailing spaces |
| MD010 | No hard tabs |
| MD011 | Reversed link syntax |
| MD012 | Multiple consecutive blank lines |
| MD013 | Line length |
| MD014 | Dollar signs used before commands without showing output |
| MD018 | No space after hash on atx style heading |
| MD019 | Multiple spaces after hash on atx style heading |
| MD020 | No space inside hashes on closed atx style heading |
| MD021 | Multiple spaces inside hashes on closed atx style heading |
| MD022 | Headings should be surrounded by blank lines |
| MD023 | Headings must start at the beginning of the line |
| MD024 | Multiple headings with the same content |
| MD025 | Multiple top-level headings in the same document |
| MD026 | Trailing punctuation in heading |
| MD027 | Multiple spaces after blockquote symbol |
| MD028 | Blank line inside blockquote |
| MD029 | Ordered list item prefix |
| MD030 | Spaces after list markers |
| MD031 | Fenced code blocks should be surrounded by blank lines |
| MD032 | Lists should be surrounded by blank lines |
| MD033 | Inline HTML |
| MD034 | Bare URL used |
| MD035 | Horizontal rule style |
| MD036 | Emphasis used instead of a heading |
| MD037 | Spaces inside emphasis markers |
| MD038 | Spaces inside code span elements |
| MD039 | Spaces around link text |
| MD040 | Fenced code blocks should have a language specified |
| MD041 | First line in a file should be a top-level heading |
| MD042 | No empty links |
| MD043 | Required heading structure |
| MD044 | Proper names should have the correct capitalization |
| MD045 | Images should have alternate text |
| MD046 | Code block style consistency |
| MD047 | Files should end with a single newline character |
| MD048 | Code fence style consistency |
