#!/usr/bin/env python3
"""Generate Glossarist v3 concept YAML files from extracted JSON data.

Creates:
  g18-glossarist/register.yaml
  g18-glossarist/concepts/{id}.yaml  (one file per entry)
"""

import json
import os
import re
import uuid


BASE_DIR = '/Users/mulgogi/src/mn/oiml-terms'
CONCEPTS_DIR = os.path.join(BASE_DIR, 'g18-glossarist', 'concepts')
REGISTER_FILE = os.path.join(BASE_DIR, 'g18-glossarist', 'register.yaml')
INPUT_FILE = os.path.join(BASE_DIR, 'scripts', 'extracted_data.json')

DATASET_URI = 'urn:oiml:pub:g:18:2010'
DATE_ACCEPTED = '2024-01-01T00:00:00+00:00'


def deterministic_uuid(namespace, name):
    """Generate a deterministic UUID based on namespace and name."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f'{namespace}/{name}'))


def escape_yaml(text):
    """Escape text for YAML single-quoted strings."""
    if not text:
        return "''"
    # For single-quoted strings, double any single quotes
    text = text.replace("'", "''")
    return f"'{text}'"


def format_yaml_value(text):
    """Format a text value for YAML output, using block style for multi-line."""
    if not text:
        return '[]'
    if '\n' in text:
        lines = text.split('\n')
        return '|\n' + '\n'.join(f'      {l}' for l in lines)
    return escape_yaml(text)


def generate_concept_yaml(entry, concept_uuid, eng_uuid):
    """Generate the full concept YAML (3 documents) for a single entry."""
    entry_id = entry['id']
    term = entry['term']
    definition = entry['definition']
    notes = entry['notes']
    ref = entry['reference']

    # Source info
    source_doc = ref['source'] if ref else ''
    clause = ref['clause'] if ref else ''

    # Build source YAML
    source_lines = []
    if source_doc:
        source_entry = f"""  - origin:
      ref:
        source: {source_doc}"""
        if clause:
            source_entry += f"""
      locality:
        type: clause
        reference_from: {escape_yaml(clause)}"""
        source_entry += f"""
    type: authoritative"""
        source_lines.append(source_entry)

    # Notes
    notes_yaml = ' []'
    if notes:
        # Split notes by numbered items (1. ..., 2. ..., etc.)
        note_items = re.split(r'(?=\d+\.\s)', notes)
        note_items = [n.strip() for n in note_items if n.strip()]
        if note_items:
            notes_yaml = '\n'
            for ni in note_items:
                notes_yaml += f'  - content: {escape_yaml(ni)}\n'
        else:
            notes_yaml = f'\n  - content: {escape_yaml(notes)}\n'

    # Definition
    if definition:
        definition_yaml = f'\n  - content: {escape_yaml(definition)}'
    else:
        definition_yaml = ' []'

    # Source YAML for localized concept
    lc_source_yaml = ''
    if source_lines:
        lc_source_yaml = '\n'.join(f'  {l}' for l in source_lines)
        lc_source_yaml = '\n  sources:\n' + lc_source_yaml

    # Concept-level sources
    concept_sources = ''
    if source_lines:
        concept_sources = '\n  sources:\n' + '\n'.join(source_lines)

    # Build the 3-document YAML
    yaml = f"""---
data:
  identifier: '{entry_id}'
  localized_concepts:
    eng: {eng_uuid}
  sources:
  - origin:
      ref:
        source: {source_doc}
    locality:
      type: clause
      reference_from: {escape_yaml(clause) if clause else "''"}
    type: authoritative
status: valid
id: {concept_uuid}
schema_version: '3'
---
data:
  dates:
  - date: '{DATE_ACCEPTED}'
    type: accepted
  definition:{definition_yaml}
  examples: []
  id: {entry_id}-eng
  notes:{notes_yaml}
  sources:
  - origin:
      ref:
        source: {source_doc}
      locality:
        type: clause
        reference_from: {escape_yaml(clause) if clause else "''"}
    type: authoritative
  terms:
  - type: expression
    normative_status: preferred
    designation: {escape_yaml(term)}
  language_code: eng
  entry_status: valid
date_accepted: '{DATE_ACCEPTED}'
id: {eng_uuid}
"""

    return yaml


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    print(f"Generating {len(entries)} concept YAML files...")

    # Create directories
    os.makedirs(CONCEPTS_DIR, exist_ok=True)

    # Generate concept IDs list for register
    concept_ids = []

    for entry in entries:
        entry_id = entry['id']
        concept_ids.append(entry_id)

        # Generate deterministic UUIDs
        concept_uuid = deterministic_uuid('oiml-g18', f'concept/{entry_id}')
        eng_uuid = deterministic_uuid('oiml-g18', f'concept/{entry_id}/eng')

        yaml_content = generate_concept_yaml(entry, concept_uuid, eng_uuid)

        # Write concept file
        concept_file = os.path.join(CONCEPTS_DIR, f'{entry_id}.yaml')
        with open(concept_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

    # Write register.yaml
    register_content = f"schema_version: '3'\nconcepts:\n"
    for cid in sorted(concept_ids, key=lambda x: (int(x.rstrip('ab')), x[-1] if x[-1].isalpha() else '')):
        register_content += f"  - '{cid}'\n"

    with open(REGISTER_FILE, 'w', encoding='utf-8') as f:
        f.write(register_content)

    print(f"Generated {len(entries)} concept files in {CONCEPTS_DIR}")
    print(f"Register file: {REGISTER_FILE}")

    # Show sample
    sample = os.path.join(CONCEPTS_DIR, f'{entries[0]["id"]}.yaml')
    print(f"\nSample file ({sample}):")
    with open(sample) as f:
        print(f.read()[:500])


if __name__ == '__main__':
    main()
