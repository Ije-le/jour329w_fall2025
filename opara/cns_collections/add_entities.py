import json
import subprocess
import time
import argparse
import sys
import shutil
from pathlib import Path


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

    # Use the uv wrapper in this environment — keep a single, explicit
    # invocation pattern: `uv run llm chat --model <model>`.
    candidates = [
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
    parser.add_argument('--model', default='groq/moonshotai/kimi-k2-instruct-0905',
                        help='LLM model to use (default: groq/moonshotai/kimi-k2-instruct-0905)')
    parser.add_argument('--input', default='story_summaries_elections.json', help='Input JSON file with stories')
    
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

    # Define your schema prompt based on your beat - CUSTOMIZE THIS!
    schema_prompt = """
    {
      "people": ["Names of all persons mentioned, for example: Yvette Gordon, Tia Hamilton"],
      "geographic_focus": "Location the story is focused on, for example: Baltimore City",
      "key_institutions": ["Private or public organizations mentioned in the story, for example: Department of Justice, Department of Transportation"]
    }
    """
    # Process each story
    enhanced_stories = []
    for i, story in enumerate(stories):
        print(f"Processing {i+1}/{len(stories)}: {story['title']}")
        
        # Backwards-compat wrapper: some older call sites use extract_metadata
        # while the new extraction function is named extract_entities.
        try:
            metadata = extract_entities(story['title'], story['summary'], schema_prompt, args.model)
        except NameError:
            metadata = extract_metadata(story['title'], story['summary'], schema_prompt, args.model)
        
        # Add metadata fields as separate columns instead of nested object
        enhanced_story = story.copy()
        
        # If metadata extraction was successful, add each field separately
        if 'error' not in metadata:
            # Add each metadata field as a top-level column
            for key, value in metadata.items():
                # Convert arrays to JSON strings for storage
                if isinstance(value, list):
                    enhanced_story[f'metadata_{key}'] = json.dumps(value)
                else:
                    enhanced_story[f'metadata_{key}'] = value
        else:
            # If there was an error, add error information
            enhanced_story['metadata_error'] = metadata.get('error', 'Unknown error')
            
        enhanced_stories.append(enhanced_story)
        
        # Be respectful to the API
        time.sleep(1)

    # Save the enhanced collection
    with open('enhanced_beat_stories.json', 'w') as f:
        json.dump(enhanced_stories, f, indent=2)

    print(f"Processed {len(enhanced_stories)} stories with metadata")

if __name__ == "__main__":
    main()