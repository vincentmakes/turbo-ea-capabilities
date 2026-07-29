# Licensing

This repository is **dual-licensed**, split along the data/code seam.

The **catalogue** — the capability, process and value-stream records, and the reference model
that documents them — is curated reference *content*. It is licensed under
**[Creative Commons Attribution 4.0 International](LICENSE)** (CC BY 4.0): free to use, adapt
and redistribute, including commercially, provided you credit the source.

The **tooling** — build scripts, CLIs, JSON Schemas, the Astro site, the Python library, the
Claude skills — is ordinary software and is licensed under **[MIT](LICENSE-CODE)**.

`SPDX-License-Identifier: CC-BY-4.0 AND MIT`

## Which licence applies to which path

| Path | Licence |
| --- | --- |
| `catalogue/**` (including `catalogue/i18n/**`) | CC BY 4.0 |
| `dist/api/**` and `packages/py/src/turbo_ea_capabilities/data/**` — generated from `catalogue/` | CC BY 4.0 |
| `README.md`, `business-capability-governance-model.md` | CC BY 4.0 |
| `scripts/**`, `schema/**`, `site/**` | MIT |
| `packages/py/src/turbo_ea_capabilities/*.py`, `packages/py/tests/**` | MIT |
| `.claude/**`, `CLAUDE.md`, `.github/**` | MIT |
| Root configuration — `package.json`, `tsconfig.json`, `style.css` | MIT |

Files on the MIT side carry an `SPDX-License-Identifier: MIT` header where the format allows
one. Files on the CC BY side carry no header — this table is authoritative for them, so that
the YAML source of truth stays free of boilerplate.

## Required attribution

When you share or adapt the catalogue, credit:

> Turbo EA Capabilities by Vincent Verdet — Turbo EA,
> <https://github.com/vincentmakes/turbo-ea-capabilities>, CC BY 4.0

The same string is served in `dist/api/version.json` (`attribution`) so downstream consumers
of the JSON API receive it programmatically.

You must also indicate if you made changes, and you may not apply legal terms or technological
measures that legally restrict others from doing anything the licence permits. You may not
imply endorsement by Turbo EA or Vincent Verdet.

## Third-party attributions

[`NOTICE`](NOTICE) lists the third-party frameworks this catalogue cross-walks to — APQC PCF®,
BIAN, TM Forum eTOM, ITIL®, SCOR®/DCOR, COBIT®, SHRM-BoCK, ISO 55000, ISO 31000, COSO ERM,
TOGAF®, BIZBOK®, ACORD, ICMM. None of them are redistributed here; the catalogue cites their
identifiers only. `NOTICE` applies regardless of which side of the split a file falls on, and
CC BY 4.0 § 3(a)(1) requires you to retain it when redistributing the catalogue.
