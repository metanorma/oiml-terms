# OIML G 18:2010 — Alphabetical List of Terms

[![Deploy](https://github.com/metanorma/oiml-terms/actions/workflows/build_deploy.yml/badge.svg)](https://github.com/metanorma/oiml-terms/actions/workflows/build_deploy.yml)

This repository contains **OIML G 18:2010** (Alphabetical List of Terms Defined in OIML Recommendations and Documents) as a [Glossarist](https://glossarist.org) v3 dataset, deployed as an interactive concept browser on GitHub Pages.

**Live site:** [https://metanorma.github.io/oiml-terms/](https://metanorma.github.io/oiml-terms/)

## About

OIML G 18:2010 is a guide published by the [International Organization of Legal Metrology (OIML)](https://www.oiml.org) that compiles all terms and definitions from the "Terminology" sections of current OIML Recommendations, Documents, and Basic Publications into a single alphabetical list.

This project provides:

- A **Glossarist v3 dataset** in `g18-glossarist/` with 2,125 concept entries
- An **interactive concept browser** built with `@glossarist/concept-browser`
- **Automated deployment** to GitHub Pages via GitHub Actions

## Repository Structure

```
├── g18-glossarist/           # Glossarist v3 dataset
│   ├── register.yaml         # Lists all concept IDs
│   └── concepts/             # 2,125 concept YAML files
├── scripts/                  # Extraction and generation scripts
│   ├── extract_data.py       # PDF → JSON extraction
│   └── generate_yaml.py      # JSON → Glossarist YAML generation
├── reference-docs/           # Source PDF and extracted figures
│   ├── g018-e10.pdf          # Source document (273 pages)
│   ├── R128-2000-Figure1.png
│   └── R080-1-2009-Figure1.png
├── logos/                    # OIML logos (SVG, light/dark variants)
├── site-config.yml           # Concept-browser site configuration
├── about.md                  # About page (English)
├── about-fra.md              # About page (French)
├── package.json              # Build/dev scripts
├── .github/workflows/        # CI/CD for GitHub Pages
```

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Concept entries | 2,125 |
| Entries with clause numbers | 2,125 (100%) |
| Entries with notes | 416 |
| Unique source documents | 88 |
| Figures extracted | 2 |

**By source type:**

- OIML Recommendations (R): 1,876 terms from 62 documents
- OIML Documents (D): 210 terms from 17 documents
- OIML Basic Publications (B): 39 terms from 9 documents

**Top sources:** R076-1:2006 (119), R051-1:2006 (114), R107-1:2007 (91), R117-1:2007 (77), R061-1:2004 (68)

**Duplicate IDs:** 7 original IDs appeared twice (different terms from different sources). These are disambiguated with letter suffixes:

| Original ID | Disambiguated |
|-------------|---------------|
| 00474 | 00474a, 00474b |
| 00763 | 00763a, 00763b |
| 01213 | 01213a, 01213b |
| 01291 | 01291a, 01291b |
| 01508 | 01508a, 01508b |
| 01669 | 01669a, 01669b |
| 02348 | 02348a, 02348b |

## Figures

Two figures were extracted from PDF pages 268–269 using PyMuPDF:

- **R128:2000 Figure 1** — referenced by term 01890 (non-automatic weighing instrument)
- **R080-1:2009 Figure 1** — referenced by terms 00652, 00916, 00602

Both are available in screen resolution and 300 DPI in `reference-docs/`.

## Data Extraction Pipeline

### Prerequisites

- `poppler` (for `pdftotext`)
- Python 3

### Steps

```bash
# 1. Extract text with layout preservation
pdftotext -layout reference-docs/g018-e10.pdf /tmp/g018-e10.txt

# 2. Parse the 5-column table into structured JSON
python3 scripts/extract_data.py

# 3. Generate Glossarist v3 YAML files
python3 scripts/generate_yaml.py
```

### Extraction details

The source PDF has a 5-column table (Term, Reference, Definition, Notes, ID) with per-page column headers. Key parsing techniques:

- **`pdftotext -layout`** preserves column positions, enabling position-based field extraction
- **Per-page column header detection** handles pages with varying column widths
- **Clause pattern matching** covers: `T.N`, `T.a.N`, `T.N.N`, `G.N-N`, `N.N+N.N`, `N.N(annex)`, and standalone `T`
- **Column bleed fix** merges 1–3 character word fragments split by column boundary misalignment
- **Term continuation detection** handles multi-line terms where the term wraps into the reference column area
- **Duplicate ID disambiguation** assigns letter suffixes (a/b) when the same 5-digit ID appears in different source documents

## Data Quality

- 1 entry with a genuinely empty definition (01455: magnetic constant — defined only by symbol in the source)
- 1 entry with a minor garbled prefix (01933: ancillary device)
- Column bleed artifacts largely resolved; residual issues are limited to individual characters

## Building Locally

```bash
# Install dependencies (concept-browser must be linked)
npm install --ignore-scripts
mkdir -p node_modules/@glossarist
ln -sf /path/to/concept-browser node_modules/@glossarist/concept-browser

# Build the static site
npm run build
```

The `build` script runs `npx concept-browser build`. Configuration is read from `site-config.yml`:

- `basePath: /oiml-terms/` — base URL for GitHub Pages deployment
- `DATASET_SOURCE_G18` env var — points to the local dataset directory

Output goes to `dist/`.

## Development Server

```bash
npm run dev
```

This runs Vite from the concept-browser's own `node_modules` (to avoid conflict with the system Ruby `vite` gem), with `DATASET_SOURCE_G18` pointing to the local dataset.

## Deployment

Pushing to `main` triggers the GitHub Actions workflow (`.github/workflows/build_deploy.yml`) which:

1. Checks out the repo
2. Clones `concept-browser` from GitHub
3. Builds the site (basePath read from `site-config.yml`)
4. Deploys to GitHub Pages

The workflow also runs on `pull_request` (build only, no deploy) and supports `workflow_dispatch` and `repository_dispatch`.

## French

French content is not yet available. The site config and about page include French translations, but the dataset itself contains English-only concepts. French terms will be added when the French PDF (`g018-f10.pdf`) becomes available.

## License

Copyright © OIML. All terminology content is sourced from OIML publications.
