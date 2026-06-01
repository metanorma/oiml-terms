# Task 2: Generate Glossarist v3 concept YAML files

Convert extracted JSON data into Glossarist v3 YAML format.

## Structure per concept YAML file (3 documents separated by `---`)
1. **Concept metadata**: identifier, localized_concepts, sources, status
2. **English localized concept**: dates, definition, examples, notes, terms, language_code
3. (French will be added later when French PDF is available)

## Key decisions
- `identifier` = the 5-digit ID (e.g. "02070")
- `sources` parsed from Reference column into `{source, locality}` format
- UUIDs generated deterministically for each entry
- Only English content for now (French pending)
- No domain grouping (flat list, as G 18 doesn't have sections like VIML)

## Output
- `g18-glossarist/concepts/{id}.yaml` for each of ~2,125 entries
- `g18-glossarist/register.yaml` listing all concept IDs

## Dependencies
- Task 1 output: `scripts/extracted_data.json`
