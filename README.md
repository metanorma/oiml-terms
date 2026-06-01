# OIML G 18:2010 — Alphabetical List of Terms

This repository contains the OIML G 18:2010 (Alphabetical List of Terms Defined in OIML Recommendations and Documents) as a [Glossarist](https://glossarist.org) dataset (v3), deployed as an interactive concept browser via GitHub Pages.

## Repository Structure

```
├── g18-glossarist/           # Glossarist v3 dataset
│   ├── register.yaml         # Lists all concept IDs
│   └── concepts/             # 2,125 concept YAML files
├── site-config.yml           # Concept-browser site configuration
├── about.md                  # About page (English)
├── about-fra.md              # About page (French)
├── logos/                    # OIML logos (SVG)
├── scripts/                  # Extraction/generation scripts
│   ├── extract_data.py       # PDF → JSON extraction
│   └── generate_yaml.py      # JSON → Glossarist YAML generation
├── reference-docs/           # Source PDF (g018-e10.pdf)
├── package.json              # Build config
└── .github/workflows/        # CI/CD for GitHub Pages
```

## Source

- **OIML G 18:2010** — Alphabetical list of terms defined in OIML Recommendations and Documents
- Source PDF: `reference-docs/g018-e10.pdf`

## Building

```bash
npm install --ignore-scripts
mkdir -p node_modules/@glossarist
ln -sf /path/to/concept-browser node_modules/@glossarist/concept-browser

DATASET_SOURCE_G18="$(pwd)/g18-glossarist" \
  node node_modules/@glossarist/concept-browser/cli/index.mjs build
```

## Dataset Statistics

- **2,125** concept entries (including 7 disambiguated duplicates)
- **2,125** entries with clause numbers (100%)
- **416** entries with notes
- **English** content (French to be added)
- Sourced from OIML Recommendations (R: 1,876), Documents (D: 210), and Basic Publications (B: 39)
- 7 duplicate IDs disambiguated with letter suffixes (a/b)
- 2 figures extracted: R128:2000 Figure 1 and R080-1:2009 Figure 1

## Data Extraction

The extraction pipeline:

1. `pdftotext -layout reference-docs/g018-e10.pdf /tmp/g018-e10.txt`
2. `python3 scripts/extract_data.py` → `scripts/extracted_data.json`
3. `python3 scripts/generate_yaml.py` → `g18-glossarist/`

## License

Copyright © OIML. All terminology content is sourced from OIML publications.
