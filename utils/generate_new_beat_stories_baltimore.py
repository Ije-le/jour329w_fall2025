#!/usr/bin/env python3
"""
Generate `new_beat_stories_baltimore.json` by removing any "tags" keys from
`enhanced_beat_stories_baltimore.json`.

Run in codespaces terminal:

    python3 utils/generate_new_beat_stories_baltimore.py

The script writes the cleaned file next to the original.
"""
import json
from pathlib import Path

INPUT = Path('opara/cns_collections/enhanced_beat_stories_baltimore.json')
OUTPUT = INPUT.with_name('new_beat_stories_baltimore.json')


def remove_tags(obj):
    """Recursively remove keys named 'tags' (case-insensitive) from dicts and
    process lists/other types unchanged."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            try:
                if isinstance(k, str) and k.lower() == 'tags':
                    continue
            except Exception:
                pass
            out[k] = remove_tags(v)
        return out
    elif isinstance(obj, list):
        return [remove_tags(i) for i in obj]
    else:
        return obj


def main():
    if not INPUT.exists():
        print('Input file not found:', INPUT)
        raise SystemExit(1)
    with INPUT.open('r', encoding='utf-8') as f:
        data = json.load(f)
    cleaned = remove_tags(data)
    with OUTPUT.open('w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print('Wrote', OUTPUT)


if __name__ == '__main__':
    main()
