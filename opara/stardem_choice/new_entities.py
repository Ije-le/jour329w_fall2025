#!/usr/bin/env python3
"""
Extract people/places/organizations from a topic file using the project's
`llm` Python API (as documented by https://llm.datasette.io/en/stable/usage.html).

This script:
- reads a topic JSON (default: `public_safety_stories.json` in the same directory)
- processes stories one at a time with the specified model
- randomly selects 300 stories from the input file (unless --limit is specified)
- expects the model to return a JSON object per story with keys:
    `title`, `people`, `places`, `organizations` (each value an array of strings).
- writes results to `stories_with_entities_v3.json` by default
- saves progress after each story (can resume if interrupted)
- returns ["SKIPPED"] for stories not focused on Maryland's Eastern Shore

Important constraints enforced by this script and prompt:
- Return ONLY JSON objects (no explanation, no markdown)
- Do NOT use placeholder example names like "Jane Doe" or "John Doe"
- Skip stories with no geographic focus on Eastern Shore
"""

import argparse
import json
import time
import subprocess
import random
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
- FIRST, determine if this story's primary geographic focus is Maryland's Eastern Shore.
- If the story is primarily about events, people, or activities OUTSIDE the Eastern Shore (e.g., international news, national news, "Art Around the World" features not focused on Eastern Shore), return: {{"title": "{title}", "people": ["SKIPPED"], "places": ["SKIPPED"], "organizations": ["SKIPPED"]}}
- Only process stories that are primarily about Maryland's Eastern Shore communities, people, and organizations.
- Examples of stories to SKIP: international art features, national entertainment news, global cultural events unless they directly involve Eastern Shore residents or organizations.
- Ignore the "Star Democrat, The (Easton, MD)" publication credit - this does not mean the story is about the Eastern Shore.

If the story IS about the Eastern Shore:
- Return EXACTLY one JSON OBJECT and NOTHING ELSE (no preface, no explanation, no markdown).
- The object must have exactly these keys: "title", "people", "places", "organizations".
- Each value for people/places/organizations must be an array of strings. If none, return an empty array [].
- Normalize entity strings: trim whitespace, remove surrounding punctuation, do not include titles (Mr., Ms., Dr.) or role labels — return only the name/place/organization string.
- Prefer full names when available. Do NOT return placeholders like "Jane Doe" or "John Doe".
- Exclude "Star Democrat", "Chesapeake Publishing Group", "Adams Publishing/APGMedia", "Invision/AP" from organizations.

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
    parser.add_argument('--input', default='public_safety_stories.json',
                        help='Input topic JSON file (default: public_safety_stories.json in current dir)')
    parser.add_argument('--output', default='stories_with_entities_v3.json',
                        help='Output simplified JSON file (default: stories_with_entities_v3.json in current dir)')
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
    
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if output file exists and load already processed stories
    already_processed = []
    processed_docrefs = set()
    if out_path.exists():
        try:
            with open(out_path) as f:
                already_processed = json.load(f)
                processed_docrefs = {s.get('docref') for s in already_processed if s.get('docref')}
                print(f"Found {len(already_processed)} already processed stories. Resuming...")
        except Exception as e:
            print(f"Warning: Could not load existing output file: {e}")
            already_processed = []

    # If --limit is provided and > 0, process that many stories; otherwise randomly select 300
    if args.limit is not None and args.limit > 0:
        stories = stories[:args.limit]
    else:
        # Randomly select 300 stories from the full set
        if len(stories) > 300:
            random.seed(42)  # Set seed for reproducibility
            stories = random.sample(stories, 300)
            print(f"Randomly selected 300 stories from the total available")
    
    # Filter out already processed stories
    stories_to_process = [s for s in stories if s.get('docref') not in processed_docrefs]
    
    if len(stories_to_process) == 0:
        print("All stories have already been processed!")
        return
    
    print(f"Processing {len(stories_to_process)} remaining stories (out of {len(stories)} total) with model {args.model}...")

    model = args.model
    
    results = already_processed  # Start with already processed stories
    skipped_count = sum(1 for s in already_processed 
                       if s.get('people') == ['SKIPPED'] and 
                          s.get('places') == ['SKIPPED'] and 
                          s.get('organizations') == ['SKIPPED'])
    
    for idx, story in enumerate(stories_to_process, start=1):
        print(f"Processing story {len(already_processed) + idx}/{len(stories)}: {story.get('title', 'Untitled')[:60]}...")
        try:
            entities = extract_entities_for_one_story(model, story, timeout=args.timeout)
            # Add entities to the original story
            result = dict(story)
            result['people'] = entities['people']
            result['places'] = entities['places']
            result['organizations'] = entities['organizations']
            
            # Track if story was skipped due to geographic focus
            if (entities['people'] == ['SKIPPED'] and 
                entities['places'] == ['SKIPPED'] and 
                entities['organizations'] == ['SKIPPED']):
                print(f"  Skipped: Not focused on Eastern Shore")
                skipped_count += 1
            
            results.append(result)
            
            # Save after each story (incremental save)
            with open(out_path, 'w') as f:
                json.dump(results, f, indent=2)
                
        except Exception as e:
            print(f"  Error processing story {len(already_processed) + idx}: {e}")
            # Add story with empty entities on error
            result = dict(story)
            result['people'] = []
            result['places'] = []
            result['organizations'] = []
            results.append(result)
            
            # Save even on error
            with open(out_path, 'w') as f:
                json.dump(results, f, indent=2)

    print(f"\nCompleted! Wrote {len(results)} stories with entity metadata to {out_path}")
    print(f"Skipped {skipped_count} stories not focused on Eastern Shore")


if __name__ == '__main__':
    main()
