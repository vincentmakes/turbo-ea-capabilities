---
name: translate-language
description: Translate the catalogue into a target language by generating sidecar files under catalogue/i18n/<locale>/. Two modes — Whole-Language (user names ONLY a language; skill produces or refreshes a sidecar for every L1 in catalogue/_index.yaml) and Single-L1 (user names one L1 + a language; skill produces or refreshes one sidecar). The user always speaks in language NAMES and capability NAMES; the skill resolves to BCP-47 tags and BC-IDs internally.
---

# translate-language

Translate the English source catalogue into a target language as **sidecar files** under `catalogue/i18n/<locale>/`. Source files in `catalogue/L1-*.yaml` are never modified — translations are additive and locale-neutral fields (id, level, industry, references, deprecation, metadata) are never duplicated.

Two modes:

- **Whole-Language mode** *(preferred for greenfield locale rollout)* — user names ONLY a target language (e.g. *"French"*, *"German"*, *"Brazilian Portuguese"*). You produce or refresh a sidecar for **every L1** registered in `catalogue/_index.yaml`.
- **Single-L1 mode** — user names one L1 by name plus a language. You produce or refresh exactly one sidecar.

**Surface = names, not codes.** Resolve language → BCP-47 (French → `fr`, Brazilian Portuguese → `pt-BR`, Simplified Chinese → `zh`, German → `de`, Spanish → `es`, Latin American Spanish → `es-419`) and L1 names → IDs internally. Show the resolved tag once for confirmation.

You **must** comply with `business-capability-governance-model.md` Part A naming rules (§5) — adapted to the target language — and never edit `catalogue/L1-*.yaml`, `dist/api/**`, or `packages/py/.../data/**`.

## Step 1 — Establish context

1. Read **`schema/i18n.schema.json`** to confirm the sidecar shape and the whitelist of translatable fields.
2. Read **`catalogue/_index.yaml`** for the full L1 list.
3. List existing locales: `ls catalogue/i18n/` so you know which sidecars already exist (refresh vs. greenfield).
4. If a sidecar already exists for the target locale (e.g. `catalogue/i18n/fr/L1-actuarial-management.yaml`), read **at least one** of them to absorb the prior translator's terminology. Cross-L1 terminology consistency matters more than per-L1 fluency — if every L1 chooses a different French word for "Reserving", the catalogue becomes useless.
5. Read 1–2 source L1s relevant to the user's industry focus to absorb the description tone before translating.

## Step 2 — Confirm scope

- **Whole-Language** — confirm:
  - target language name and resolved BCP-47 tag,
  - refresh strategy: **skip-existing** (default — only translate L1s with no sidecar yet), **fill-gaps** (touch existing sidecars but only add entries that are missing), or **overwrite** (rewrite everything).
- **Single-L1** — confirm: L1 name → ID, target language, overwrite-or-merge if a sidecar already exists.

Show the resolved tag once. **Do not loop back per-L1 for confirmation in Whole-Language mode.** One approval covers the whole language.

## Step 3 — Translate

For each L1 in scope:

1. Load the source L1 tree (read the YAML directly — there is no helper CLI for translation).
2. For every node in the tree, translate the **whitelisted** fields only:
   - `name` — apply target-language equivalents of §5 noun-phrase / Title Case rules. Conventions vary: French uses sentence case for capability names; German capitalises every noun; Spanish uses sentence case. Research the convention before mass-translating.
   - `description` — preserve the 1–3 sentence outcome-orientation. Do not paraphrase into a process description, do not invent new scope, do not lose nuance.
   - `in_scope`, `out_of_scope`, `aliases` — translate item-by-item if present in source; **omit the array entirely** if source has none. Do not invent.
3. **Do NOT translate**:
   - `id`, `level`, `industry`, `references` (URLs), `deprecated`, `successor_id`, `metadata` — these stay in the source L1 file and are inherited by the build.
   - **Acronyms with no target-language equivalent** (e.g. *IFRS 17*, *Solvency II*, *ORSA*, *PML*, *AAL*, *CSM*). Keep them; gloss them parenthetically on first use in a description if helpful.
4. **Maintain a glossary across the L1 set** so the same source term always lands the same target term (e.g. *"Reserving"* → *"Provisionnement"* everywhere, never sometimes *"Réserves"*). When in doubt, search prior sidecars for the term first. In Whole-Language mode, build the glossary as you go and apply it consistently to all L1s in the run.

## Step 4 — Write sidecars

Write each sidecar to `catalogue/i18n/<locale>/L1-<same-slug>.yaml`. The slug **must** match the source filename exactly so per-L1 CODEOWNERS apply transitively.

Required top-level fields per `schema/i18n.schema.json`:

- `locale: <bcp47>` — must equal the parent directory name.
- `source: L1-<slug>.yaml` — must match an indexed L1 file.
- `entries:` — map of `BC-id -> {name, description, ...}`. Every key must resolve to a node in the source tree.

Optional:

- `metadata:` — translator credits, review status, completion notes (free-form).

## Step 5 — Validate

Run, in order:

```bash
npm run lint          # full catalogue + sidecar lint (schema, ID resolution, orphans, locale/dir match)
npm run build:api     # confirms per-locale dist artefacts build
```

Common failures and fixes:

- **Schema** → missing `locale` / `source` / `entries`, or an untranslatable field appeared in `entries.<id>` (only the whitelisted fields are allowed by `additionalProperties: false`).
- **Orphaned entry** → entry id no longer exists in the source tree (capability was renamed, moved, or deprecated). Either remove the orphan or update to the new id.
- **Locale tag / directory mismatch** → directory is `fr-CA` but file says `locale: fr`; align them.
- **Source filename mismatch** → `source:` does not point to a file registered in `catalogue/_index.yaml`.

Do **not** loosen the schema, the lint rules, or the source files to make the sidecar pass. Fix the sidecar.

## Step 6 — Hand off

Summarise using *names* and the resolved tag:

- **Whole-Language, complete** — *"Translated `<N>` L1(s) into `<Language>` (`<bcp47>`): `<comma-separated names>`. Sidecars under `catalogue/i18n/<bcp47>/`. Coverage: `<X>`/`<Y>` nodes (`<%>`)."*
- **Whole-Language, partial** — list which source nodes still need translation per L1, grouped by L1 name.
- **Single-L1** — *"Translated `<L1 name>` into `<Language>` (`<bcp47>`). `<X>`/`<Y>` nodes (`<%>`)."*

Always close with: *"Open a PR; CODEOWNERS for `catalogue/i18n/<bcp47>/` (and per-L1) will be auto-requested."*

## What this skill must not do

- Edit any file outside `catalogue/i18n/<target-locale>/`.
- Translate URLs, identifiers, industry tags, levels, or any non-whitelisted field.
- Invent capabilities not present in the source tree (no orphaned entries).
- Refresh / overwrite an existing sidecar without explicit user approval (Step 2's refresh strategy is required).
- Skip lint validation.
- Loosen `schema/i18n.schema.json` or `scripts/lint.ts` to make a draft pass.
- Translate into a language the user has not explicitly approved (no auto-detection from the user's prompt language).
