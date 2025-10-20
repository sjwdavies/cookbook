# Taylor‑Davies Recipe Architect — Modular Persona Pack v2.0

An expert‑level, **modular** ChatGPT persona that creates, refines, and stores family recipes.  
Outputs are **human summary → JSON → Markdown** (in that order), with a Nutrition module that computes **per‑portion macros** and **% RDA** (adult + child bands).

This README is self‑contained. Anyone can follow it to recreate the persona from scratch in ChatGPT using the files in this pack.

---

## 1) What’s in this pack?

```
taylor-davies-modular-persona-pack-v2.0/
├── README.md                                  ← this guide
├── tdra_instructions_core_v2.md               ← the persona’s core instructions (≤ 8k)
├── modules/
│   └── persona_nutrition_addendum_v1.0.md     ← nutrition module (v1.0)
├── reference/
│   ├── nutrition_reference_uk_2025.csv        ← per‑100 g ingredient nutrition
│   └── rda_reference_uk_2025.json             ← adult + child RDA tables
└── schema/
    └── recipe_schema.json                     ← JSON output structure (for the persona to follow)
```

**Core vs Modules**  
- **Core (v2.0)** defines identity, workflow, output order, and formatting rules.  
- **Modules (v1.x)** add domain logic (Nutrition is the first).  
- **Reference** files feed modules with data (CSV/JSON).  
- **Schema** keeps JSON consistent for automation.

> The persona is designed to scale: add future modules (e.g., *Seasonality*, *Weaning*, *Leftovers*) under `modules/` without editing the core.

---

## 2) Prerequisites

- Access to **ChatGPT → Create a GPT** (the GPT builder).  
- You do **not** need any APIs or external services.  
- (Optional) Enable **Code Interpreter** capability during setup for stronger JSON handling.

---

## 3) Create the persona in ChatGPT (from scratch)

1. **Open the GPT Builder**  
   ChatGPT → **Explore GPTs** → **Create** → **Configure**.

2. **Name & Description**  
   - **Name:** `Taylor‑Davies Recipe Architect`  
   - **Description:** `Modular expert recipe developer that asks clarifying questions, outputs JSON + Markdown, and computes nutrition & RDA using uploaded data.`

3. **Instructions (Core)**  
   - Open `tdra_instructions_core_v2.md` from this pack.  
   - **Copy all** the text and **paste it into the Instructions box**.  
   - It’s under 8k characters to avoid UI limits.

4. **Upload Knowledge files** (drag/drop under **Knowledge**)  
   Upload **all** of the following:
   - `modules/persona_nutrition_addendum_v1.0.md`  
   - `schema/recipe_schema.json`  
   - `reference/nutrition_reference_uk_2025.csv`  
   - `reference/rda_reference_uk_2025.json`

   > The Core tells the persona to consult these modular files and references. There is no separate “Response Format” UI; the schema is enforced by the Instructions + Knowledge combo.

5. **Capabilities**  
   - Enable **Code Interpreter** (recommended).  
   - Browsing / Image tools: off (not needed).

6. **Save** the GPT.

---

## 4) How it behaves (at a glance)

1) **Clarify** missing details (adult/child portions, child age in months, time/equipment, must‑use/avoid, spice level).  
2) **Propose** a short plan; you approve or tweak.  
3) **Finalise** (after approval) and output in this **exact order**:  
   - **Concise chat summary**  
   - **JSON** matching `schema/recipe_schema.json`  
   - **Markdown** (pure MD; headings/lists have blank lines)  
4) **Ask once**: “Store to memory and save JSON?” If yes, it offers a downloadable JSON and suggests a filename like `data/recipes/<slug>.json`.

**Nutrition module:**  
- Converts units to grams (tsp=5g, tbsp=15g, ml=1g, L=1000g, g=g, kg=1000g; whole item=100g by default).  
- Maps ingredients to canonical names using `nutrition_reference_uk_2025.csv`.  
- Computes **per‑adult‑portion**: kcal (0 dp), protein/carbs/fat (1 dp), salt (2 dp).  
- Calculates **% RDA** for **adults** and for **child age band** (if provided), and outputs a table for **all bands**.  
- If mapping or units are uncertain → values **null** and a brief note in `meta.assumptions[]`.

---

## 5) Test the persona

**Prompt example**  
> “Butter chicken for 2 adults + 1 child (18 months), mild spice, 45 mins total, hob only, no nuts.”

**Expect**  
- Clarifying questions (only what’s missing).  
- A proposed plan → you approve.  
- Final output: **summary → JSON → Markdown**.  
- JSON includes `nutrition`, `meta.adult_rda_percent`, `meta.child_rda_percent` (if age provided), `meta.child_rda_percent_by_band`, and `meta.assumptions`.  
- Markdown uses standard syntax and lints cleanly (blank lines around headings and lists).

---

## 6) Troubleshooting

- **Instructions too long**: Only paste the **Core** file. All other content lives under **Knowledge**.  
- **JSON shape mismatches**: Ensure `schema/recipe_schema.json` is uploaded; remind the model in your prompt to “follow the schema in Knowledge.”  
- **Nutrition seems off**: Expand or correct `reference/nutrition_reference_uk_2025.csv` to include the exact ingredients you use; the model will then match them more accurately.  
- **Child RDA missing**: Make sure you specify `child_age_months` during clarifications.

---

## 7) Maintaining and extending the persona

- **Versioning**  
  - Core: this pack is **v2.0**.  
  - Nutrition module: **v1.0**.  
  - When you update a module, bump its version (e.g., `persona_nutrition_addendum_v1.1.md`) and upload the new file under Knowledge.

- **Adding new modules** (e.g., Seasonality)  
  - Create `modules/persona_seasonal_addendum_v1.0.md` with: *Purpose*, *When to apply*, *Rules*, *Output impact*.  
  - Upload it under **Knowledge** — no edits to the Core required.

- **Updating reference data**  
  - Add rows/columns to `reference/nutrition_reference_uk_2025.csv` (e.g., fibre, sugars) and update the rules in the module file if new fields affect output.

---

## 8) Optional: store this pack in your GitHub repo

Suggested structure:
```
/persona/
  README.md
  tdra_instructions_core_v2.md
  /modules/
    persona_nutrition_addendum_v1.0.md
  /reference/
    nutrition_reference_uk_2025.csv
    rda_reference_uk_2025.json
  /schema/
    recipe_schema.json
```

Commit message example:
```
chore(persona): add modular persona pack v2.0 (nutrition module v1.0)
```

---

## 9) License & attribution
Use freely within the Taylor‑Davies family projects. If re‑using externally, please keep a link back to this README and credit “Taylor‑Davies Recipe Architect — Modular Core v2.0”.

---

### You’re ready.
Open the GPT builder, paste the Core, upload the Knowledge files, and test with your favourite recipe idea.
