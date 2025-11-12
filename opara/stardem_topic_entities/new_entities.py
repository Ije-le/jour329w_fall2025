#!/usr/bin/env python3
"""
Extract people/places/organizations from the Arts & Culture topic file using the project's
`llm` Python API (as documented by https://llm.datasette.io/en/stable/usage.html).

This script:
- reads a topic JSON (default: `arts_culture_stories.json` in the same directory)
- calls the specified model exactly ONCE with the full set of stories (default: groq/meta-llama/llama-4-maverick-17b-128e-instruct)
- expects the model to return EXACTLY one JSON array with one object per input story. Each object must have the keys:
    `title`, `people`, `places`, `organizations` (each value an array of strings).
- writes the resulting array to `stories_with_entities_v2.json` by default (processes all stories unless --limit is set)

Important constraints enforced by this script and prompt:
- Return ONLY the JSON array and NOTHING ELSE (no explanation, no markdown).
- Do NOT use placeholder example names like "Jane Doe" or "John Doe".
"""

import argparse
import json
import time
from pathlib import Path
import llm


def _extract_last_json(s: str):
    """Find the last balanced JSON object or array in a string and return it, or None.

    This scans for balanced top-level '{...}' or '[...]' fragments and returns the last complete
    balanced fragment found. That lets us recover a trailing JSON array returned by the model.
    """
    if not s:
        return None
    last_fragment = None
    stack = 0
    start = None
    in_string = False
    escape = False
    for i, ch in enumerate(s):
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == '{' or ch == '[':
            if stack == 0:
                start = i
            stack += 1
        elif ch == '}' or ch == ']':
            if stack > 0:
                stack -= 1
                if stack == 0 and start is not None:
                    last_fragment = s[start:i+1]
                    start = None

    return last_fragment


def extract_entities_for_all_stories(model, stories: list, log_prefix: Path):
    """Call the model exactly once with the full list of stories and return parsed results.

    Expects the model to return a JSON array with one object per story. Each object must
    contain `title`, `people`, `places`, `organizations`.
    """
    # Build a concise but unambiguous prompt containing all stories
    prompt_lines = [
        "You will be given a list of Arts & Culture news stories. For each story, extract all PEOPLE, PLACES, and ORGANIZATIONS mentioned.",
        "VERY IMPORTANT:",
        "- Return EXACTLY one JSON ARRAY and NOTHING ELSE (no preface, no explanation, no markdown).",
        "- The array must contain one object per story in the same order as provided.",
        "- Each object must have exactly these keys: \"title\", \"people\", \"places\", \"organizations\".",
        "- Each value for people/places/organizations must be an array of strings. If none, return an empty array [].",
        "- Normalize entity strings: trim whitespace, remove surrounding punctuation, do not include titles (Mr., Ms., Dr.) or role labels — return only the name/place/organization string.",
        "- Prefer full names when available. Do NOT return placeholders like \"Jane Doe\" or \"John Doe\".",
        "",
        "Return only the JSON array. Example element format (for clarity only, do not include this example in output):",
        "[{\"title\": \"Some title\", \"people\": [\"Name A\"], \"places\": [\"Place X\"], \"organizations\": [\"Org Y\"]}, ...]",
        "",
        "Now process the following stories:",
        "",
    ]

    # Append each story with its title and text in a compact numbered list
    for idx, s in enumerate(stories, start=1):
        title = s.get('title', '')
        text = s.get('content') or s.get('summary') or s.get('text') or ''
        prompt_lines.append(f"{idx}. Title: {title}")
        prompt_lines.append("Article Text:")
        prompt_lines.append(text)
        prompt_lines.append("")

    prompt_lines.append("Return the JSON array now.")
    prompt = "\n".join(prompt_lines)

    # Call the model exactly once
    resp = model.prompt(prompt).text()

    # Save raw response for diagnostics
    try:
        log_prefix.parent.mkdir(parents=True, exist_ok=True)
        with open(log_prefix.with_suffix('.out.txt'), 'w') as f:
            f.write(resp)
    except Exception:
        pass

    # Try to parse the response as JSON array
    data = None
    try:
        data = json.loads(resp)
    except Exception:
        # Try to recover last balanced JSON fragment (object or array)
        candidate = _extract_last_json(resp)
        if candidate:
            try:
                data = json.loads(candidate)
            except Exception:
                data = None

    if data is None:
        # Write the raw response to an error log and raise so issues are visible
        err_log = log_prefix.with_suffix('.err.txt')
        try:
            with open(err_log, 'w') as f:
                f.write(resp)
        except Exception:
            pass
        raise ValueError(f"No valid JSON array found in model response. See {err_log}")

    # Validate and normalize results: expect a list of objects
    if not isinstance(data, list):
        raise ValueError("Model returned JSON that is not an array. Expected an array with one object per story.")

    results = []
    for item in data:
        if not isinstance(item, dict):
            # skip invalid entries but keep alignment by adding an empty record
            results.append({'title': '', 'people': [], 'places': [], 'organizations': []})
            continue

        title = item.get('title', '')
        people = item.get('people', []) if isinstance(item.get('people', []), list) else []
        places = item.get('places', []) if isinstance(item.get('places', []), list) else []
        organizations = item.get('organizations', []) if isinstance(item.get('organizations', []), list) else []

        results.append({'title': title, 'people': people, 'places': places, 'organizations': organizations})

    return results


def main():
    parser = argparse.ArgumentParser(description='Extract people/places/organizations from an Arts & Culture topic JSON')
    parser.add_argument('--model', default='groq/meta-llama/llama-4-maverick-17b-128e-instruct',
                        help='Model to use (default: groq/meta-llama/llama-4-maverick-17b-128e-instruct)')
    parser.add_argument('--input', default='arts_culture_stories.json',
                        help='Input topic JSON file (default: arts_culture_stories.json in current dir)')
    parser.add_argument('--output', default='stories_with_entities_v2.json',
                        help='Output simplified JSON file (default: stories_with_entities_v2.json in current dir)')
    # Default --limit 0 means process all stories in the input file
    parser.add_argument('--limit', type=int, default=0, help='Process only the first N stories (default 0 = all)')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}")
        return

    with open(input_path) as f:
        stories = json.load(f)

    # If --limit > 0, process that many stories; otherwise process all
    if args.limit and args.limit > 0:
        stories = stories[: args.limit]
    else:
        # process the full file
        stories = stories

    # Create model using the llm Python API
    model = llm.get_model(args.model)

    logs_dir = Path('opara/stardem_topic_entities/logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_prefix = logs_dir / 'all_stories'

    print(f"Calling model once to process {len(stories)} stories...")
    results = extract_entities_for_all_stories(model, stories, log_prefix)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Wrote {len(results)} simplified stories to {out_path}")


if __name__ == '__main__':
    main()
