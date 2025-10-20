# Addendum Module: Nutrition and RDA Calculation v1.1

## Purpose

Extends the Core with nutrition, macro, and RDA calculations.

## Calculation Rules

- Use `nutrition_reference_uk_2025.csv` and `rda_reference_uk_2025.json`.
- Ingredient mapping is case‑insensitive with loose “contains” match.
- Unit to gram conversions:
  - tsp = 5 g
  - tbsp = 15 g
  - ml = 1 g
  - L = 1000 g
  - g = g
  - kg = 1000 g
- If no unit, assume 100 g.
- Ignore “to taste” items except numeric salt.
- Compute per‑adult‑portion totals, then %RDA for adults and children.

### Rounding

- kcal: integer.
- Protein, Carbohydrates, Fat: 1 dp.
- Salt: 2 dp.
- RDA %: 1 dp.

### Output Fields

`nutrition`, `meta.adult_rda_percent`, `meta.child_rda_percent`,
`meta.child_rda_percent_by_band`, and `meta.assumptions`.

If data unknown, set to `null` and note the assumption.

### References

- `reference/nutrition_reference_uk_2025.csv`.
- `reference/rda_reference_uk_2025.json`.
