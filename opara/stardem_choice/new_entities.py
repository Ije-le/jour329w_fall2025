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
import subprocess
from pathlib import Path


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


def extract_entities_for_one_story(model: str, story: dict, timeout: int = 300, retries: int = 3):
    """Call the model for a single story and return a JSON object with entities.

    Expects the model to return a JSON object with keys: `title`, `people`, `places`, `organizations`.
    """
    title = story.get('title', '')
    text = story.get('content') or story.get('summary') or story.get('text') or ''
    
    # Prompt template - edit this to customize the extraction instructions
    PROMPT_TEMPLATE = """Extract all PEOPLE, PLACES, and ORGANIZATIONS mentioned in the following news story.

VERY IMPORTANT:
- Return EXACTLY one JSON OBJECT and NOTHING ELSE (no preface, no explanation, no markdown).
- The object must have exactly these keys: "title", "people", "places", "organizations".
- Each value for people/places/organizations must be an array of strings. If none, return an empty array [].
- DO NOT PROCESS METADATA FOR ARTICLES WITH FOREIGN FOCUS
- Normalize entity strings: trim whitespace, remove surrounding punctuation, do not include titles (Mr., Ms., Dr.) or role labels — return only the name/place/organization string.
- Prefer full names when available. Do NOT return placeholders like "Jane Doe" or "John Doe".
- Exclude "Star Democrat", "Chesapeake Publishing Group", "Adams Publishing/APGMedia", "Invision/AP" from organizations
- If an article's main geographic focus or location is not on Maryland's Eastern Shore, SKIP processing that article. REMEMBER, DO NOT PROCESS METADATA FOR ARTICLES WITH FOCUS OUTSIDE MARYLAND'S EASTERN SHORE. Examples of articles to ignore are those whose focus are in: "Hong Kong", "London", "Indonesia"
- For geographic focus, ignore "Star Democrat, The (Easton, MD)" which always appears at the top of the story.
- REMEMBER: Examples of articles to ignore are those ehose focus are in: "Hong Kong", "London", "Indonesia", "Castle Fine Art"


Title: {title}
Article Text:
{text}

Return the JSON object now."""
    
    prompt = PROMPT_TEMPLATE.format(title=title, text=text)

    # Call llm via uv wrapper
    cmd = ["uv", "run", "llm", "--model", model]

    resp = None
    last_err = None
    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
        except Exception as e:
            last_err = str(e)
            # small backoff
            time.sleep(1 * attempt)
            continue

        out = (proc.stdout or '').strip()
        err = (proc.stderr or '').strip()

        if proc.returncode == 0 and out:
            # strip triple-backtick fences if present
            if out.startswith('```'):
                parts = out.split('\n')
                if parts[0].startswith('```'):
                    out = '\n'.join(parts[1:])
                    if out.rstrip().endswith('```'):
                        out = out.rstrip()[:-3].rstrip()
            resp = out
            break

        # detect transient provider messages and retry
        low = (err or out or '').lower()
        if ('over capacity' in low or '503' in low or 'rate limit' in low or '429' in low or 'try again' in low):
            sleep_secs = min(60 * attempt, 300)
            time.sleep(sleep_secs)
            last_err = err or out
            continue
        # non-retryable failure
        last_err = err or out or f"returncode={proc.returncode}"
        break

    if resp is None:
        raise ValueError(f"LLM CLI failed: {last_err or 'no response'}")

    # Try to parse the response as JSON object
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

    if data is None or not isinstance(data, dict):
        raise ValueError(f"No valid JSON object found in model response")

    # Extract and normalize entities
    people = data.get('people', []) if isinstance(data.get('people', []), list) else []
    places = data.get('places', []) if isinstance(data.get('places', []), list) else []
    organizations = data.get('organizations', []) if isinstance(data.get('organizations', []), list) else []

    return {'people': people, 'places': places, 'organizations': organizations}


def main():

    parser = argparse.ArgumentParser(description='Extract people/places/organizations from an Arts & Culture topic JSON')
    parser.add_argument('--model', default='anthropic/claude-sonnet-4-5',
                        help='Model to use (default: anthropic/claude-sonnet-4-5)')
    parser.add_argument('--input', default='arts_culture_stories.json',
                        help='Input topic JSON file (default: arts_culture_stories.json in current dir)')
    parser.add_argument('--output', default='stories_with_entities_v2.json',
                        help='Output simplified JSON file (default: stories_with_entities_v2.json in current dir)')
    # No --limit means process all stories; set a positive number to limit for testing
    parser.add_argument('--limit', type=int, default=None, help='Process only the first N stories (default: process all stories)')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout seconds for the LLM CLI call (default 300)')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}")
        return

    with open(input_path) as f:
        stories = json.load(f)

    # If --limit is provided and > 0, process that many stories; otherwise process all
    if args.limit is not None and args.limit > 0:
        stories = stories[:args.limit]
    # else: process all stories (no slicing needed)

    model = args.model

    print(f"Processing {len(stories)} stories one at a time with model {model}...")
    
    results = []
    for idx, story in enumerate(stories, start=1):
        print(f"Processing story {idx}/{len(stories)}: {story.get('title', 'Untitled')[:60]}...")
        try:
            entities = extract_entities_for_one_story(model, story, timeout=args.timeout)
            # Add entities to the original story
            result = dict(story)
            result['people'] = entities['people']
            result['places'] = entities['places']
            result['organizations'] = entities['organizations']
            results.append(result)
        except Exception as e:
            print(f"  Error processing story {idx}: {e}")
            # Add story with empty entities on error
            result = dict(story)
            result['people'] = []
            result['places'] = []
            result['organizations'] = []
            results.append(result)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Wrote {len(results)} stories with entity metadata to {out_path}")


if __name__ == '__main__':
    main()
