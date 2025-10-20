# Taylor‑Davies Recipe Architect — Modular Persona Pack v2.0.2

This release of the Taylor‑Davies Recipe Architect persona is fully
lint‑compliant. All Markdown adheres to **MD013**, **MD022**, and **MD032**.

## Files Overview

```
README.md
tdra_instructions_core_v2.md
/modules/persona_nutrition_addendum_v1.0.md
/reference/nutrition_reference_uk_2025.csv
/reference/rda_reference_uk_2025.json
/schema/recipe_schema.json
```

## Setup in ChatGPT

1. Open ChatGPT → **Explore GPTs** → **Create** → **Configure**.
2. Name: **Taylor‑Davies Recipe Architect**.
3. Paste `tdra_instructions_core_v2.md` into the Instructions box.
4. Upload all remaining files under **Knowledge**.
5. Enable **Code Interpreter**, disable other tools.
6. Save the GPT.

## Key Features

- Outputs **summary → JSON → Markdown**.
- Markdown always passes MD013, MD022, MD032.
- Nutrition derived from reference CSV + JSON.
- Computes per‑portion macros and %RDA (adult + child).

## Example Prompt

> Butter chicken for 2 adults and 1 child (18 months), mild spice, 45 minutes,
> hob only, no nuts.

The persona will ask clarifying questions, then produce clean outputs.

## Versioning

Core v2.0.2 • Nutrition module v1.0

## License

Use freely within Taylor‑Davies family projects. Credit required for reuse.
