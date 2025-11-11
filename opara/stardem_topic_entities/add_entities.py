import json
import re
import subprocess
import time
import argparse
import sys
import shutil
from pathlib import Path

def extract_entities(title, summary, fulltext, examples_text, model, timeout=60, retries=5, log_prefix=None):
    """Call the LLM to extract people, places, organizations as JSON arrays.
    Prefer `fulltext` when available; otherwise use `summary`.
    """
    prompt = f"""
Extract the entities mentioned in this news story. VERY IMPORTANT:

- Do NOT ask for more input. Use ONLY the provided Headline and Article Text (or Summary if no full text is present). Do not attempt to read external sources.
- Return EXACTLY one JSON object and NOTHING ELSE (no preface, no explanation, no markdown). The JSON must contain exactly these three keys in this order: "people", "places", "organizations".
- Each value must be an array of strings. If none, return an empty array [].
- Normalize entity strings: trim whitespace, remove surrounding punctuation, do not include titles (Mr., Ms., Dr.) or roles (mayor, governor) — return the name only.
- Prefer full names when available. Do not return duplicate entries.

Examples (input → expected output):
Headline: "Council honors Jane Doe for service"
Summary: "City council honored councilwoman Jane Doe on Monday for her long service."
Output: {{"people": ["Jane Doe"], "places": [], "organizations": ["City Council"]}}

Headline: "Local hospital expands" 
Summary: "St. Mary's Hospital in Annapolis announced a $10 million expansion to its emergency department."
Output: {{"people": [], "places": ["Annapolis"], "organizations": ["St. Mary's Hospital"]}}

Input (Headline and Article Text):
Headline: {title}
Article Text: {fulltext}

Return only the JSON object.
"""

    # Use the uv wrapper to call the llm plugin. We only need a single
    # invocation pattern here (uv run llm chat ...) — keep it simple and
    # explicit for the environment this repo uses.
    candidates = [
        ["uv", "run", "llm", "chat", "--model", model],
    ]

    last_err = None
    def _extract_last_json(s: str):
        """Find the last balanced JSON object in the string and return it (or None)."""
        if not s:
            return None
        # simple stack-based scan for the last balanced {...}
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
    for cmd in candidates:
        if shutil.which(cmd[0]) is None:
            continue
        attempt = 0
        while attempt < retries:
            try:
                proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
            except Exception as e:
                last_err = str(e)
                attempt += 1
                time.sleep(1 * attempt)
                continue

            # always write a diagnostic log if requested
            if log_prefix:
                try:
                    with open(f"{log_prefix}.out.txt", 'w') as lof:
                        lof.write((proc.stdout or '')[:10000])
                    with open(f"{log_prefix}.err.txt", 'w') as le:
                        le.write((proc.stderr or '')[:10000])
                except Exception:
                    pass

            out = (proc.stdout or '').strip()
            err = (proc.stderr or '').strip()
            # if the CLI returned success and there is output, try to parse
            if proc.returncode == 0 and out:
                # strip code fences
                if out.startswith('```'):
                    parts = out.split('\n')
                    if parts[0].startswith('```'):
                        out = '\n'.join(parts[1:])
                        if out.rstrip().endswith('```'):
                            out = out.rstrip()[:-3].rstrip()
                # The CLI may include conversation transcripts and fragments. Try to extract
                # the last balanced JSON object from the output if simple json.loads fails.
                data = None
                try:
                    data = json.loads(out)
                except Exception:
                    candidate = _extract_last_json(out)
                    if candidate:
                        try:
                            data = json.loads(candidate)
                        except Exception:
                            data = None
                if data is None:
                    raise ValueError('no valid JSON found in LLM output')
                    # ensure keys exist and are lists
                # ensure keys exist and are lists
                people = data.get('people', []) if isinstance(data.get('people', []), list) else []
                places = data.get('places', []) if isinstance(data.get('places', []), list) else []
                orgs = data.get('organizations', []) if isinstance(data.get('organizations', []), list) else []
                return {'people': people, 'places': places, 'organizations': orgs}
                # if we reach here, the except earlier would have handled invalid JSON
            # If the process failed with an error likely from the provider
            if proc.returncode != 0:
                last_err = err or out or f"returncode={proc.returncode}"
                # detect temporary provider errors and retry
                low = (err or out or '').lower()
                # handle common transient provider messages
                if ('over capacity' in low or '503' in low or 'internal_server_error' in low or 'try again' in low
                        or 'rate limit' in low or '429' in low):
                    # try to parse an explicit wait time from the message like 'Please try again in 1m26.4s'
                    m = re.search(r'please try again in\s*(?:(\d+)m)?\s*(?:(\d+(?:\.\d+)?)s)?', low)
                    sleep_secs = None
                    if m:
                        mins = int(m.group(1)) if m.group(1) else 0
                        secs = float(m.group(2)) if m.group(2) else 0.0
                        sleep_secs = mins * 60 + secs
                    # fallback exponential backoff if no explicit time provided
                    if sleep_secs is None:
                        attempt += 1
                        sleep_secs = 1 * (2 ** (attempt - 1))
                    # cap sleep to a reasonable max (5 minutes)
                    sleep_secs = min(sleep_secs, 300)
                    time.sleep(sleep_secs + 1)
                    attempt += 1
                    continue
                else:
                    # non-retryable error for this command
                    break
            # if we reach here without returning, break out of retry loop
            break

    return {'error': 'LLM failed', 'detail': last_err}


def main():
    parser = argparse.ArgumentParser(description='Extract people, places and organizations from Star-Democrat stories')
    parser.add_argument('--model', default='groq/meta-llama/llama-4-maverick-17b-128e-instruct',
                        help='LLM model to use (default: groq/meta-llama/llama-4-maverick-17b-128e-instruct)')
    parser.add_argument('--input', default='stardem_sample.json', help='Input JSON file with stories')
    parser.add_argument('--output', default='stories_with_entities_second.json', help='Output JSON file to write')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout seconds for each LLM call')

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    # Load your beat stories
    try:
        with open(args.input) as f:
            stories = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input}'")
        print("Make sure to update the --input parameter to match your topic file!")
        return

    # Define examples guidance for formatting
    examples_text = """
{"people": ["David Breimhurst", "Kristen Greenaway"], "places": ["Denton"], "organizations": ["Kennard African American Cultural Heritage"]}
{"people": [], "places": ["Dorchester County"], "organizations": ["Dorchester County Emergency Medical Services"]}
"""

    # Process each story and build simplified output
    simplified = []
    # ensure logs directory exists
    logs_dir = Path('opara/stardem_entities/logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    for i, story in enumerate(stories):
        print(f"Processing {i+1}/{len(stories)}: {story.get('title')}")

        log_prefix = str(logs_dir / f"story_{i+1:04d}")
        # Use full article text (`content`) when available for better entity extraction.
        full_text = story.get('content') or story.get('summary') or ''
        summary = story.get('summary') or ''
        entities = extract_entities(story.get('title', ''), summary, full_text, examples_text, args.model, timeout=args.timeout, log_prefix=log_prefix)

        if 'error' in entities:
            print(f"Warning: LLM failed for story {i+1}: {entities.get('detail')}")
            people = []
            places = []
            organizations = []
        else:
            people = entities.get('people', [])
            places = entities.get('places', [])
            organizations = entities.get('organizations', [])

        simplified.append({
            'story_number': story.get('story_number', i+1),
            'headline': story.get('title', ''),
            'people': people,
            'places': places,
            'organizations': organizations,
        })

        # polite pause
        time.sleep(1)

    # Save the simplified collection
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(simplified, f, indent=2)

    print(f"Wrote {len(simplified)} simplified stories to {out_path}")


if __name__ == "__main__":
    main()
