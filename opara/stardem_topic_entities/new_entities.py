#!/usr/bin/env python3
"""
Extract people/places/organizations from the Arts & Culture topic file using the project's
`llm` Python API (as documented by https://llm.datasette.io/en/stable/usage.html).

This script:
- reads a topic JSON (default: `arts_culture_stories.json` in the same directory)
- calls the specified model once per story (default: groq/meta-llama/llama-4-maverick-17b-128e-instruct)
- expects the model to return EXACTLY one JSON object (keys: people, places, organizations)
- writes simplified story objects to `stories_with_entities_v2.json` by default (processes all stories unless --limit is set)

Do NOT use placeholder example names (Jane Doe / John Doe) in the prompt.
"""

import argparse
import json
import time
from pathlib import Path
import llm


def _extract_last_json(s: str):
    """Find the last balanced JSON object in a string and return it, or None."""
    if not s:
        return None
    last_obj = None
    stack = 0
    start = None
    for i, ch in enumerate(s):
        if ch == '{':
            if stack == 0:
                start = i
            stack += 1
        elif ch == '}':
            if stack > 0:
                stack -= 1
                if stack == 0 and start is not None:
                    last_obj = s[start:i+1]
                    start = None
    return last_obj


def extract_entities_for_story(model, title: str, text: str, log_prefix: Path):
    prompt_lines = [
        "Extract all people, places, and organizations mentioned in this Arts & Culture news story.",
        "VERY IMPORTANT:",
        "- Return EXACTLY one JSON object and NOTHING ELSE (no preface, no explanation, no markdown).",
        "- The JSON must contain exactly these three keys: \"people\", \"places\", \"organizations\".",
        "- Each value must be an array of strings. If none, return an empty array [].",
        "- Normalize entity strings: trim whitespace, remove surrounding punctuation, do not include titles (Mr., Ms., Dr.) or role labels — return only the name/place/organization string.",
        "- Prefer full names when available. Do NOT return placeholders like \"Jane Doe\" or \"John Doe\".",
        "",
        f"Title: {title}",
        "",
        "Article Text:",
        text,
        "",
        "Return only the JSON object with keys people, places, organizations.",
    ]
    prompt = "\n".join(prompt_lines)

    # Call the model once via the llm Python API
    resp = model.prompt(prompt).text()

    # Save raw response for diagnostics
    try:
        log_prefix.parent.mkdir(parents=True, exist_ok=True)
        with open(log_prefix.with_suffix('.out.txt'), 'w') as f:
            f.write(resp)
    except Exception:
        pass

    # Try to parse the response as JSON
    data = None
    try:
        data = json.loads(resp)
    except Exception:
        # If the model returned extra text, try to recover the last JSON object
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
        raise ValueError(f"No valid JSON found in model response for title: {title}. See {err_log}")

    # Normalize returned structures to lists
    people = data.get('people', []) if isinstance(data.get('people', []), list) else []
    places = data.get('places', []) if isinstance(data.get('places', []), list) else []
    organizations = data.get('organizations', []) if isinstance(data.get('organizations', []), list) else []

    return {'people': people, 'places': places, 'organizations': organizations}


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

    simplified = []
    logs_dir = Path('opara/stardem_topic_entities/logs')
    logs_dir.mkdir(parents=True, exist_ok=True)

    for i, story in enumerate(stories, start=1):
        title = story.get('title', '')
        text = story.get('content') or story.get('summary') or ''
        print(f"Processing {i}/{len(stories)}: {title}")
        log_prefix = logs_dir / f'story_{i:04d}'
        try:
            entities = extract_entities_for_story(model, title, text, log_prefix)
        except Exception as e:
            # Surface error and stop — per user request we don't hide errors
            print(f"Error extracting entities for story {i}: {e}")
            raise

        simplified.append({
            'title': title,
            'people': entities['people'],
            'places': entities['places'],
            'organizations': entities['organizations'],
        })

        # polite short pause
        time.sleep(0.8)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(simplified, f, indent=2)

    print(f"Wrote {len(simplified)} simplified stories to {out_path}")


if __name__ == '__main__':
    main()
