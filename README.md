# OIML G 18:2010 — Alphabetical List of Terms

[![Deploy](https://github.com/metanorma/oiml-terms/actions/workflows/build_deploy.yml/badge.svg)](https://github.com/metanorma/oiml-terms/actions/workflows/build_deploy.yml)

Online terminology browser for **OIML G 18:2010** (Alphabetical List of Terms Defined in OIML Recommendations and Documents), deployed at [metanorma.github.io/oiml-terms](https://metanorma.github.io/oiml-terms/).

Built with the [Glossarist Concept Browser](https://github.com/glossarist/concept-browser) — a statically deployable SPA for browsing terminology datasets.

## Contents

- [Repository structure](#repository-structure)
- [Dataset](#dataset)
- [Building locally](#building-locally)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Updating the dataset](#updating-the-dataset)

## Repository structure

```
oiml-terms/
├── site-config.yml          Site configuration (branding, features, dataset, base path)
├── about.md                 About page (English)
├── about-fra.md             About page (French)
├── g18-glossarist/          Glossarist v3 dataset (source of truth)
│   ├── register.yaml        Dataset metadata and concept list
│   └── concepts/            2,125 concept YAML files
├── logos/                    OIML logo files (SVG, light/dark variants)
├── scripts/                  Python extraction and generation scripts
│   ├── extract_data.py      PDF → JSON extraction
│   └── generate_yaml.py     JSON → Glossarist YAML generation
├── reference-docs/           Source PDF and extracted figures
└── .github/workflows/
    └── build_deploy.yml     CI: build + deploy to GitHub Pages
```

Build artifacts (gitignored): `dist/`, `public/`, `.datasets/`, `node_modules/`.

## Dataset

The `g18-glossarist/` directory contains the Glossarist v3 dataset with **2,125 concept entries** compiled from 88 OIML publications:

| Source type | Terms | Documents |
|-------------|-------|-----------|
| Recommendations (R) | 1,876 | 62 |
| Documents (D) | 210 | 17 |
| Basic Publications (B) | 39 | 9 |

Each concept is a YAML file with English designations, definitions, notes, and source references.

### Disambiguated IDs

Seven IDs appeared in multiple source documents with different terms. These are disambiguated with letter suffixes:

| Original | Disambiguated |
|----------|---------------|
| 00474 | 00474a, 00474b |
| 00763 | 00763a, 00763b |
| 01213 | 01213a, 01213b |
| 01291 | 01291a, 01291b |
| 01508 | 01508a, 01508b |
| 01669 | 01669a, 01669b |
| 02348 | 02348a, 02348b |

## Building locally

Prerequisites: Node.js 20+

```sh
npm install --ignore-scripts @glossarist/concept-browser
npm install --prefix node_modules/@glossarist/concept-browser sharp 2>/dev/null || true
npx concept-browser build
```

The CLI reads `site-config.yml` from the current directory, fetches the dataset from `g18-glossarist/` (via `localPath`), generates static data, and builds the SPA into `dist/`.

To preview the build:

```sh
npx vite preview
```

## Configuration

All configuration is in `site-config.yml`. Key fields:

```yaml
basePath: /oiml-terms/               # Subpath for GitHub Pages deployment

datasets:
  - id: g18
    localPath: g18-glossarist         # Dataset source directory
    ref: "OIML G 18:2010"            # Publication reference (shown in sidebar provenance)
    owner: OIML
    sourceRepo: https://github.com/metanorma/oiml-terms

branding:
  primaryColor: "#004996"
  logo:
    localPath: logos/oiml-logo.svg
    localLight: logos/oiml-logo-icon-light.svg
    localDark: logos/oiml-logo-icon-dark.svg
```

- **`basePath`** — sets the URL subpath for GitHub Pages. No `BASE_PATH` env var needed.
- **`localPath`** — points to the local dataset directory. No `DATASET_SOURCE_*` env var needed.
- **`ref`** — publication reference shown in the sidebar provenance section.
- **Branding** — logo variants for light/dark mode, colors, Google Fonts.

The site supports English and French UI (`uiLanguages` in config). About pages are provided in both languages (`about.md`, `about-fra.md`).

## Deployment

Pushing to `main` triggers the GitHub Actions workflow (`.github/workflows/build_deploy.yml`):

1. Checks out the repo
2. Installs `@glossarist/concept-browser` from npm
3. Runs `npx concept-browser build`
4. Deploys `dist/` to GitHub Pages

All configuration comes from `site-config.yml` — the only env var is `GITHUB_TOKEN`.

## Updating the dataset

The `scripts/` directory contains Python scripts for extracting terms from the source PDF:

```bash
# Prerequisites: poppler (for pdftotext), Python 3

# 1. Extract text from PDF
pdftotext -layout reference-docs/g018-e10.pdf /tmp/g018-e10.txt

# 2. Parse the 5-column table into structured JSON
python3 scripts/extract_data.py

# 3. Generate Glossarist v3 YAML files
python3 scripts/generate_yaml.py
```

After updating the dataset, commit the changes to `g18-glossarist/` and push to `main` to trigger a rebuild.

### Extraction details

The source PDF has a 5-column table (Term, Reference, Definition, Notes, ID). Key parsing techniques:

- **`pdftotext -layout`** preserves column positions for position-based field extraction
- **Per-page column header detection** handles varying column widths
- **Clause pattern matching** covers: `T.N`, `T.a.N`, `T.N.N`, `G.N-N`, `N.N+N.N`, `N.N(annex)`, and standalone `T`
- **Column bleed fix** merges character fragments split by column boundary misalignment
- **Duplicate ID disambiguation** assigns letter suffixes when the same 5-digit ID appears in different source documents

## License

Copyright OIML. All terminology content is sourced from OIML publications.
