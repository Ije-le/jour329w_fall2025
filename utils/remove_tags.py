#!/usr/bin/env python3
"""
Remove all 'tags' keys from a JSON file (recursively) and write output to a new file.
Usage: python utils/remove_tags.py path/to/input.json
Output file: same directory, named <original>.no-tags.json
"""
import json
import sys
from pathlib import Path


def remove_tags(obj):
    """Recursively remove any keys named 'tags' (case-insensitive) from dicts and from items in lists."""
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() == 'tags':
                # skip this key entirely
                continue
            new[k] = remove_tags(v)
        return new
    elif isinstance(obj, list):
        return [remove_tags(item) for item in obj]
    else:
        return obj


def main():
    if len(sys.argv) < 2:
        print('Usage: python utils/remove_tags.py path/to/input.json')
        sys.exit(2)
    inp = Path(sys.argv[1])
    if not inp.exists():
        print('Input file not found:', inp)
        sys.exit(1)
    out = inp.with_name(inp.stem + '.no-tags' + inp.suffix)
    with inp.open('r', encoding='utf-8') as f:
        data = json.load(f)
    cleaned = remove_tags(data)
    with out.open('w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print('Wrote', out)


if __name__ == '__main__':
    main()
