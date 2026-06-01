#!/usr/bin/env python3
"""Extract term entries from OIML G 18:2010 PDF using pdftotext layout output.

Uses a hybrid approach:
- Page headers determine column positions for continuation lines
- First line of each entry uses regex-based parsing (more robust)
- ID detection anchors entry boundaries

Outputs structured JSON to scripts/extracted_data.json.
"""

import json
import re
import sys

# Clause number patterns used in OIML publications
CLAUSE_PAT = (
    r'T\.\d+(?:\.\d+)*'                # T.7, T.2.10.2
    r'|T\.[a-z]\.\d+(?:\.\d+)*'        # T.a.2, T.c.2.4
    r'|T\d+\.\d+(?:\.\d+)*'            # T6.3
    r'|\d+(?:\.\d+)+(?:\([^)]+\))?'    # 3.1, 2.4.16, 2.4(annex 6)
    r'|\d+\.\d+\+\d+\.\d+'             # 2.2+2.3
    r'|\d+(?:\([^)]+\))?'              # 1, 2(annex 6)
    r'|T'                               # standalone T (R053:1982)
    r'|G\.\d+-\d+'                     # G.3-1
)
# Lookahead: clause must be followed by punctuation, whitespace, paren, or end
CLAUSE_END = r'(?=[.,\s)]|$)'


def parse_entries(text_file):
    with open(text_file, 'r', encoding='utf-8') as f:
        all_lines = [l.rstrip('\n') for l in f.readlines()]

    # Find all page header lines to build a page boundary map
    page_headers = []
    for i, line in enumerate(all_lines):
        if ('Term' in line and 'Reference' in line and
                'Definition' in line and 'Notes' in line and 'ID' in line):
            cols = {
                'ref': line.index('Reference'),
                'def': line.index('Definition'),
                'notes': line.index('Notes'),
                'id': line.index('ID'),
            }
            page_headers.append((i, cols))

    # Build a map: for each line, what column positions apply?
    line_cols = {}
    for idx, (header_line, cols) in enumerate(page_headers):
        # Next header or end of file
        next_header = page_headers[idx + 1][0] if idx + 1 < len(page_headers) else len(all_lines)
        for i in range(header_line + 1, next_header):
            line_cols[i] = cols

    # Parse entries
    entries = []
    current_entry = None

    for i, line in enumerate(all_lines):
        # Skip page headers, OIML headers, page footers, blank lines
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('OIML G 18:2010'):
            continue
        if re.match(r'^Page \d+ of \d+$', stripped):
            continue
        if ('Term' in stripped and 'Reference' in stripped and
                'Definition' in stripped and 'Notes' in stripped and 'ID' in stripped):
            continue
        # Skip figure pages (after "Page 267 of 269")
        if 'R128:2000, Figure 1' in stripped or 'R080-1:2009, Figure 1' in stripped:
            continue

        # Check for 5-digit ID at end of line
        id_match = re.search(r'(\d{5})\s*$', line.rstrip())
        if id_match:
            # Verify this is actually in the ID column area
            id_pos = line.rfind(id_match.group(1))
            cols = line_cols.get(i, {'notes': 120})

            if id_pos >= cols.get('notes', 120) - 10:
                entry_id = id_match.group(1)

                # Save previous entry
                if current_entry is not None:
                    entries.append(finalize_entry(current_entry))

                # Parse first line using regex-based approach
                parsed = parse_first_line(line, id_match.start())
                current_entry = {
                    'id': entry_id,
                    'term': parsed['term'],
                    'reference_parts': [parsed['reference']] if parsed['reference'] else [],
                    'definition_parts': [parsed['definition']] if parsed['definition'] else [],
                    'notes_parts': [parsed['notes']] if parsed['notes'] else [],
                }
                continue

        # Continuation line
        if current_entry is None:
            continue

        cols = line_cols.get(i, {'ref': 35, 'def': 50, 'notes': 120, 'id': 160})
        defn = line[cols['def']:cols['notes']].strip()
        notes = line[cols['notes']:cols.get('id', 200)].strip()
        # Remove any trailing 5-digit numbers from notes (shouldn't be there on continuation)
        notes = re.sub(r'\s*\d{5}\s*$', '', notes).strip()

        # Scan the area before the def column for clause-like patterns.
        # The clause may start slightly left of the ref column boundary.
        pre_def = line[:cols['def']].strip()
        clause_re = rf'(?:^|\s)({CLAUSE_PAT}){CLAUSE_END}'
        clause_m = re.search(clause_re, pre_def)
        if clause_m:
            clause_text = clause_m.group(1)
            current_entry['reference_parts'].append(clause_text)
            before_clause = pre_def[:clause_m.start()].strip()
            after_clause = pre_def[clause_m.end():].strip()
            # before_clause is term continuation text (in the term column area)
            if before_clause and any(len(w) >= 4 for w in before_clause.split()):
                current_entry['term'] += ' ' + before_clause
            # Merge short after_clause with defn (column boundary splits a word)
            if after_clause and 1 <= len(after_clause) <= 3 and defn:
                if after_clause.isalpha() and defn[0].isalpha() and defn[0].islower():
                    defn = after_clause + defn
                else:
                    current_entry['definition_parts'].insert(0, after_clause)
            elif after_clause:
                current_entry['definition_parts'].insert(0, after_clause)
        elif pre_def:
            # No clause found — check for term continuation or column bleed
            if any(len(w) >= 4 for w in pre_def.split()):
                current_entry['term'] += ' ' + pre_def
            elif pre_def and 1 <= len(pre_def) <= 3 and defn:
                if pre_def.isalpha() and defn[0].isalpha() and defn[0].islower():
                    defn = pre_def + defn
                else:
                    current_entry['definition_parts'].insert(0, pre_def)
            else:
                current_entry['definition_parts'].insert(0, pre_def)
        if defn:
            current_entry['definition_parts'].append(defn)
        if notes:
            current_entry['notes_parts'].append(notes)

    if current_entry is not None:
        entries.append(finalize_entry(current_entry))

    return entries


def parse_first_line(line, id_start):
    """Parse the first line of an entry using regex-based column detection.

    Returns dict with term, reference, definition, notes.
    """
    # Remove the ID from the end
    content = line[:id_start].rstrip()

    # Find the reference pattern: R/D/B/G followed by digits, optional -digits, :digits
    ref_match = re.search(r'([RDGB]\d+(?:-\d+)?:\d+)', content)
    if ref_match:
        term = content[:ref_match.start()].strip()
        after_ref = content[ref_match.end():].strip()

        # The reference might have a comma and clause after it
        # e.g., "R101:1991, T.7" - the ", T.7" is part of the reference
        # But on the first line, the clause might be after the reference
        # Look for ", " followed by clause-like pattern
        ref_text = ref_match.group(1)

        # After the reference, there might be a comma + clause number
        # The clause starts with ", " and the definition starts after
        # We detect this by looking at the content after the reference
        if after_ref.startswith(','):
            clause_match = re.match(
                rf',\s*({CLAUSE_PAT}){CLAUSE_END}',
                after_ref
            )
            if clause_match:
                ref_text = ref_text + ', ' + clause_match.group(1)
                remaining = after_ref[clause_match.end():].strip()
            else:
                # No clear clause - definition starts after comma
                remaining = after_ref[1:].strip()
        else:
            remaining = after_ref

        # Now split remaining into definition and notes
        # Notes start where there's a large gap (5+ spaces) in the middle
        defn, notes = split_def_notes(remaining)

        return {
            'term': term,
            'reference': ref_text,
            'definition': defn,
            'notes': notes,
        }
    else:
        # No reference found - try column-position fallback
        # This handles edge cases like terms starting with parentheses
        return {
            'term': content.strip(),
            'reference': '',
            'definition': '',
            'notes': '',
        }


def split_def_notes(text):
    """Split text into definition and notes by finding a large gap."""
    if not text:
        return '', ''

    # Look for a gap of 5+ spaces in the middle of the text
    # This indicates the boundary between definition and notes columns
    gap_match = re.search(r'\S(\s{5,})\S', text)
    if gap_match:
        # Make sure the gap is not at the very beginning or end
        gap_pos = gap_match.start() + 1
        if gap_pos > len(text) * 0.3:  # Gap should be in the right portion
            defn = text[:gap_match.start() + 1].strip()
            notes = text[gap_match.end() - 1:].strip()
            return defn, notes

    return text.strip(), ''


def parse_reference(ref_text):
    """Parse reference text into structured form."""
    raw = ref_text.strip()
    raw = re.sub(r'\s+', ' ', raw).strip()
    if not raw:
        return None

    match = re.match(r'([RDGB]\d+(-\d+)?:\d+)(?:[,\s]+(.+))?$', raw, re.DOTALL)
    if match:
        source_doc = match.group(1)
        clause = match.group(3) or ''
        return {
            'source': f'OIML {source_doc}',
            'clause': clause.strip(),
            'raw': raw
        }

    return {'source': raw, 'clause': '', 'raw': raw}


def clean_text(text):
    """Clean extracted text."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def finalize_entry(entry):
    """Convert raw entry parts into final structured form."""
    ref_text = ' '.join(p for p in entry['reference_parts'] if p)
    def_text = ' '.join(p for p in entry['definition_parts'] if p)
    notes_text = ' '.join(p for p in entry['notes_parts'] if p)

    return {
        'id': entry['id'],
        'term': clean_text(entry['term']),
        'reference': parse_reference(ref_text),
        'definition': clean_text(def_text),
        'notes': clean_text(notes_text) if notes_text.strip() else '',
    }


def main():
    text_file = '/tmp/g018-e10.txt'
    output_file = '/Users/mulgogi/src/mn/oiml-terms/scripts/extracted_data.json'

    entries = parse_entries(text_file)
    entries.sort(key=lambda e: e['id'])

    # Check for duplicates
    ids = [e['id'] for e in entries]
    seen = {}
    dupes = []
    for e in entries:
        if e['id'] in seen:
            dupes.append((e['id'], seen[e['id']], e))
        else:
            seen[e['id']] = e

    if dupes:
        print(f"\nWARNING: {len(dupes)} duplicate IDs found:")
        for did, first, second in dupes:
            print(f"  ID {did}:")
            print(f"    1) '{first['term']}' ref={first['reference']}")
            print(f"    2) '{second['term']}' ref={second['reference']}")

    # Disambiguate duplicate IDs by appending letter suffix
    seen_ids = {}
    for e in entries:
        if e['id'] in seen_ids:
            # First occurrence gets 'a', second gets 'b'
            first = seen_ids[e['id']]
            if not first['id'].endswith(('a', 'b')):
                first['id'] = first['id'] + 'a'
            e['id'] = e['id'] + 'b'
        else:
            seen_ids[e['id']] = e

    entries = sorted(entries, key=lambda e: e['id'])

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"\nExtracted {len(entries)} unique entries to {output_file}")

    # Show first few entries
    for e in entries[:5]:
        print(f"\n  ID: {e['id']}")
        print(f"  Term: {e['term']}")
        ref = e['reference']
        if ref:
            print(f"  Ref: {ref['source']}, {ref['clause']}")
        print(f"  Def: {e['definition'][:100]}...")
        if e['notes']:
            print(f"  Notes: {e['notes'][:100]}...")

    # Quality check: entries with missing data
    missing_def = [e for e in entries if not e['definition']]
    missing_ref = [e for e in entries if not e['reference']]
    print(f"\nEntries missing definition: {len(missing_def)}")
    print(f"Entries missing reference: {len(missing_ref)}")
    if missing_ref:
        for e in missing_ref[:5]:
            print(f"  ID {e['id']}: '{e['term']}'")


if __name__ == '__main__':
    main()
