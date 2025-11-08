import json
import subprocess
import time
import argparse
import sys
import shutil
from pathlib import Path

DEFAULT_MODEL = "groq/moonshotai/kimi-k2-instruct-0905"


def extract_entities(title, summary, examples_text, model, timeout=60):
    """Call the LLM to extract people, places, organizations as JSON arrays."""
    prompt = f"""
Extract the entities mentioned in this news story. Return ONLY valid JSON with keys: "people", "places", "organizations".
Each value must be an array of strings (may be empty). Do not include any other keys.

Examples to guide formatting (do not treat these as exhaustive):
{examples_text}

Story Headline: {title}
Story Summary: {summary}

Return only JSON. Example output format:
{{"people": ["Name A", "Name B"], "places": ["Place A"], "organizations": ["Org A"]}}
"""

    candidates = [
        ["llm", "chat", "--model", model],
        ["llm", "query", "--model", model],
        ["uv", "run", "llm", "chat", "--model", model],
    ]

    last_err = None
    for cmd in candidates:
        if shutil.which(cmd[0]) is None:
            continue
        try:
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
        except Exception as e:
            last_err = str(e)
            continue

        out = (proc.stdout or '').strip()
        err = (proc.stderr or '').strip()
        if proc.returncode == 0 and out:
            # strip code fences
            if out.startswith('```'):
                parts = out.split('\n')
                if parts[0].startswith('```'):
                    out = '\n'.join(parts[1:])
                    if out.rstrip().endswith('```'):
                        out = out.rstrip()[:-3].rstrip()
            try:
                data = json.loads(out)
                # ensure keys exist and are lists
                people = data.get('people', []) if isinstance(data.get('people', []), list) else []
                places = data.get('places', []) if isinstance(data.get('places', []), list) else []
                orgs = data.get('organizations', []) if isinstance(data.get('organizations', []), list) else []
                return {'people': people, 'places': places, 'organizations': orgs}
            except Exception as e:
                last_err = f"JSON parse error: {e}; output: {out[:200]}"
                continue
        last_err = err or out or f"returncode={proc.returncode}"

    return {'error': 'LLM failed', 'detail': last_err}


def main():
    parser = argparse.ArgumentParser(description='Add metadata to CNS beat stories using LLM')
    parser.add_argument('--model', required=True, help='LLM model to use (e.g., gpt-4o-mini, claude-3.5-haiku)')
    parser.add_argument('--input', default='story_summaries_elections.json', help='Input JSON file with stories')
    parser.add_argument('--output', default='stories_with_entities.json', help='Output JSON file to write')
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
    for i, story in enumerate(stories):
        print(f"Processing {i+1}/{len(stories)}: {story.get('title')}")

        entities = extract_entities(story.get('title', ''), story.get('summary', ''), examples_text, args.model, timeout=args.timeout)

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
