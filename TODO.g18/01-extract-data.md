# Task 1: Extract structured data from G 18 PDF

Parse the PDF table data into structured JSON (one entry per ID).

## Source
- `reference-docs/g018-e10.pdf` (273 pages, ~2,125 term entries)

## Table structure (5 columns)
- **Term** (col 0-37): The term designation
- **Reference** (col 38-52): OIML document reference (e.g. R101:1991, T.7)
- **Definition** (col 53-121): Definition text
- **Notes** (col 122-167): Notes (optional)
- **ID** (col 168+): 5-digit unique ID

## Key parsing challenges
- Multi-line entries (definition and notes span multiple rows)
- Reference can span 2 lines (e.g. "R140:2007," then "T.2.4")
- Math symbols (µ, χ, superscripts, subscripts) need proper encoding
- Some entries have empty notes column
- Page headers/footers need stripping
- The last 2 pages (268-269) contain figures, not terms

## Output
- `scripts/extracted_data.json` — array of objects: `{id, term, reference, definition, notes}`

## Dependencies
- `pdftotext -layout` output at `/tmp/g018-e10.txt` (already extracted)
- Python 3 with PyMuPDF (for fallback/validation)
