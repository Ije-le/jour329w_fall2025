import json
import subprocess
import time
import argparse
import sys
from pathlib import Path
import glob
import re
import random

def screen_eastern_shore_relevance(story_title, story_content, model):
    """Use LLM to screen whether a story is geographically focused on Maryland's Eastern Shore."""
    
    prompt = f"""
Evaluate whether this news story is GEOGRAPHICALLY FOCUSED on Maryland's Eastern Shore.

CONTEXT: We need to filter stories to only include those centered on events, people, and places in Maryland's Eastern Shore region. The Eastern Shore includes: Caroline, Dorchester, Kent, Queen Anne's, Somerset, Talbot, Wicomico, and Worcester counties.

CRITERIA FOR EASTERN SHORE STORIES:
A story IS geographically focused on the Eastern Shore if:
- The main events take place in Eastern Shore counties or towns (Easton, Cambridge, Salisbury, Ocean City, St. Michaels, Denton, Centreville, Chestertown, etc.)
- The story focuses on Eastern Shore residents, officials, or organizations
- The primary subject matter is rooted in the Eastern Shore community

SHOULD BE EXCLUDED:
- National news stories with no Eastern Shore connection
- Stories primarily about other Maryland regions (Baltimore, Annapolis, Western Maryland) even if briefly mentioning the Eastern Shore
- Wire service stories about other states or countries
- Stories where the only Eastern Shore connection is publication in a local newspaper

Story Title: {story_title}
Story Content (first 1500 chars): {story_content[:1500]}

INSTRUCTIONS: Respond with ONLY a JSON object in this exact format:
{{
  "is_eastern_shore_focused": true or false,
  "reasoning": "Brief explanation (1-2 sentences)"
}}

Respond with valid JSON only, no other text:
"""
    
    try:
        result = subprocess.run([
            'llm', '-m', model, prompt
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response_text = result.stdout.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1]
                response_text = response_text.rsplit('\n', 1)[0]
            
            screening_result = json.loads(response_text)
            return screening_result
        else:
            return {"is_eastern_shore_focused": False, "reasoning": "Screening model failed"}
    except subprocess.TimeoutExpired:
        return {"is_eastern_shore_focused": False, "reasoning": "Screening timed out"}
    except json.JSONDecodeError as e:
        return {"is_eastern_shore_focused": False, "reasoning": "JSON parse failed"}
    except Exception as e:
        return {"is_eastern_shore_focused": False, "reasoning": f"Error: {str(e)}"}

def extract_entities(story_title, story_content, model):
    """Use LLM to extract named entities (people, places, organizations) from public safety news stories."""
    
    prompt = f"""
Extract ALL named entities from this PUBLIC SAFETY news story and return them in JSON format.

CONTEXT: This story is from the Public Safety beat covering law enforcement, fire departments, emergency services, courts, crime, accidents, and public safety-related news from Maryland's Eastern Shore. Extract ALL people, places, and organizations mentioned.

Extract the following entities:

- people: Array of ALL people mentioned in the story. NO HONORIFICS (no Dr., Mr., Mrs., Ms.). Format as "FirstName LastName, Role, Agency/Organization" when role and agency are available:
  * Law enforcement: "Robert Kane, Fire Chief, St. Michaels Volunteer Fire Department"
  * Officers with rank: "Thomas Anderson, Sergeant, Maryland State Police"
  * Court officials: "Patricia Miller, Judge, Talbot County Circuit Court"
  * Suspects/defendants: "Michael Stevens, 35, suspect" or "Sarah Johnson, defendant"
  * Victims: "David Williams, victim" (only if named in story)
  * Public officials: "Carol Westfall, Mayor, Klamath Falls"
  * Citizens/residents: "Amanda Rodriguez, 28, of Easton" or "Kevin Brown, resident"
  Format: "FirstName LastName, Role, Organization" (NO Dr./Mr./Mrs./Ms./Rev. etc.)

- places: Array of ALL geographic locations and specific places mentioned:
  * Cities/Towns: Always include state - "Easton, Maryland", "St. Michaels, Maryland"
  * Counties: "Talbot County, Maryland", "Caroline County, Maryland"
  * States/Countries: "Maryland", "Oregon", "Nevada"
  * Specific locations: "Route 50", "Chesapeake Bay Bridge", "Talbot County Courthouse"
  * Facilities/Buildings: "Easton Police Department", "Sky Lakes Medical Center"
  Include ALL places mentioned, even outside Eastern Shore

- organizations: Array of ALL organizations, institutions, and agencies mentioned. DO NOT ABBREVIATE - use full official names:
  * Law enforcement: "Easton Police Department", "Maryland State Police", "Federal Bureau of Investigation"
  * Fire/EMS: "St. Michaels Volunteer Fire Department", "Talbot County Department of Emergency Services"
  * Courts: "Talbot County Circuit Court", "United States District Court"
  * Government: "Maryland State Fire Marshal", "United States Coast Guard"
  * Other agencies: Full names, no abbreviations (e.g., "Federal Bureau of Investigation" NOT "FBI")
  Use complete official names without abbreviations

IMPORTANT RULES:
- Extract ALL entities mentioned, regardless of location
- NO honorifics in people names (no Dr., Mr., Mrs., Ms., Rev., etc.)
- NO abbreviations in organization names - spell out completely
- Do NOT include news organizations, reporters, photographers, or story authors
- Do NOT include the byline author
- Be thorough - include every person, place, and organization

Example output:
{{
  "people": ["Chris Thomas, President, St. Michaels Volunteer Fire Department", "Robert Reynolds, Captain, Klamath Falls Police Department", "Carol Westfall, Mayor, Klamath Falls", "Negasi Zuberi, 29, suspect"],
  "places": ["St. Michaels, Maryland", "Talbot County, Maryland", "Klamath Falls, Oregon", "Reno, Nevada", "Route 50"],
  "organizations": ["St. Michaels Volunteer Fire Department", "Klamath Falls Police Department", "Federal Bureau of Investigation Portland Field Office", "Maryland State Police", "Nevada State Patrol"]
}}

Story Title: {story_title}
Story Content: {story_content}

Return only valid JSON with the three arrays. If a category has no entities, use an empty array []:
"""
    
    try:
        result = subprocess.run([
            'llm', '-m', model, prompt
        ], capture_output=True, text=True, timeout=60)  # Increased timeout to 60 seconds
        
        if result.returncode == 0:
            # Parse and validate the JSON response
            response_text = result.stdout.strip()
            # Remove any markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1]
                response_text = response_text.rsplit('\n', 1)[0]
            
            metadata = json.loads(response_text)
            return metadata
        else:
            # Return more detailed error information
            stderr_msg = result.stderr[:200] if result.stderr else "No error message"
            return {"error": "LLM failed", "stderr": stderr_msg, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "LLM request timed out after 60 seconds"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing failed: {str(e)}", "response": result.stdout[:200] if 'result' in locals() else "No response"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description='Add entity metadata (people, places, organizations) to public safety stories from Star-Democrat using LLM')
    parser.add_argument('--model', required=True, help='LLM model to use (e.g., groq/openai/gpt-oss-120b)')
    parser.add_argument('--input', default='public_safety_stories.json', help='Input JSON file with stories (default: public_safety_stories.json)')
    parser.add_argument('--output', default='stories_and_entities_v2.json', help='Output JSON file (default: stories_and_entities_v2.json)')
    parser.add_argument('--sample-size', type=int, default=300, help='Number of stories to randomly sample (default: 300)')
    parser.add_argument('--limit', type=int, help='Limit the number of stories to process (useful for testing)')
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Load Star-Democrat public safety stories
    try:
        with open(args.input) as f:
            all_stories = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input}'")
        print("Make sure the input file exists in the current directory!")
        return
    
    # Filter out unwanted story types
    stories = []
    filtered_out = []
    
    for story in all_stories:
        title = story.get('title', '')
        content = story.get('content', '')
        
        # Skip stories based on title patterns
        if 'TODAY IN HISTORY' in title.upper():
            filtered_out.append(f"{title} (TODAY IN HISTORY)")
            continue
        if 'RELIGION CALENDAR' in title.upper():
            filtered_out.append(f"{title} (RELIGION CALENDAR)")
            continue
        if 'MID-SHORE CALENDAR' in title.upper():
            filtered_out.append(f"{title} (MID-SHORE CALENDAR)")
            continue
        
        # Skip stories based on section
        if 'Section: Calendar' in content or 'Section: Columns' in content or 'Section: Letters' in content:
            filtered_out.append(f"{title} (Calendar/Columns/Letters section)")
            continue
        
        stories.append(story)
    
    print(f"\nLoaded {len(all_stories)} public safety stories from {args.input}")
    print(f"Filtered out {len(filtered_out)} stories (calendars, columns, history, letters)")
    print(f"Remaining stories after filtering: {len(stories)}")
    
    # Randomly sample stories
    sample_size = min(args.sample_size, len(stories))
    if sample_size < len(stories):
        print(f"Randomly sampling {sample_size} stories from {len(stories)} available stories")
        random.seed(42)  # Set seed for reproducibility
        stories = random.sample(stories, sample_size)
    else:
        print(f"Using all {len(stories)} stories (less than requested sample size of {args.sample_size})")
    
    # Apply limit if specified (for testing)
    if args.limit and args.limit < len(stories):
        print(f"Limiting processing to first {args.limit} stories (--limit argument)")
        stories = stories[:args.limit]
    
    print(f"Will process {len(stories)} stories\n")
    
    if filtered_out and len(filtered_out) <= 10:
        print("Filtered stories:")
        for item in filtered_out:
            print(f"  - {item}")
        print()

    # Use output filename from args
    output_filename = args.output
    
    # Initialize or load existing results
    if Path(output_filename).exists():
        print(f"Found existing output file {output_filename}, loading previous results...")
        with open(output_filename) as f:
            enhanced_stories = json.load(f)
        print(f"Loaded {len(enhanced_stories)} previously processed stories\n")
    else:
        enhanced_stories = []
        print(f"Starting fresh with new output file: {output_filename}\n")

    # Process each story
    errors = []
    screened_out = []
    starting_count = len(enhanced_stories)
    
    for i, story in enumerate(stories):
        # Skip if already processed (in case we're resuming)
        if i < starting_count:
            continue
            
        print(f"Processing {i+1}/{len(stories)}: {story.get('title', 'Untitled')[:60]}...")
        
        # Get story content
        story_content = story.get('content', '')
        
        if not story_content:
            print(f"  ⚠️  Warning: No content found for story")
            # Skip stories with no content
            continue
        
        # Screen for Eastern Shore geographic focus
        screening = screen_eastern_shore_relevance(story.get('title', ''), story_content, args.model)
        
        if not screening.get('is_eastern_shore_focused', False):
            print(f"  ⊘ Excluded: {screening.get('reasoning', 'Not Eastern Shore focused')}")
            screened_out.append({
                'title': story.get('title', 'Untitled'),
                'reasoning': screening.get('reasoning', 'Not Eastern Shore focused')
            })
            # DO NOT PROCESS - skip to next story
            continue
        
        print(f"  ✓ Eastern Shore story: {screening.get('reasoning', '')}")
        
        # Extract entities from the story
        entities = extract_entities(story.get('title', ''), story_content, args.model)
        
        # Add entity fields to the story (includes original story data)
        enhanced_story = story.copy()
        
        # Add screening info
        enhanced_story['eastern_shore_screening'] = screening
        
        # If entity extraction was successful, add each field
        if 'error' not in entities:
            enhanced_story['people'] = entities.get('people', [])
            enhanced_story['places'] = entities.get('places', [])
            enhanced_story['organizations'] = entities.get('organizations', [])
            print(f"  ✓ Found {len(enhanced_story['people'])} people, {len(enhanced_story['places'])} places, {len(enhanced_story['organizations'])} orgs")
        else:
            # If there was an error, add empty arrays and error information
            enhanced_story['people'] = []
            enhanced_story['places'] = []
            enhanced_story['organizations'] = []
            enhanced_story['entity_extraction_error'] = entities.get('error', 'Unknown error')
            errors.append(f"Story {i+1}: {entities.get('error', 'Unknown error')[:100]}")
            print(f"  ✗ Error: {entities.get('error', 'Unknown error')[:80]}")
            # Print stderr if available for debugging
            if 'stderr' in entities:
                print(f"     stderr: {entities['stderr'][:200]}")
            if 'returncode' in entities:
                print(f"     return code: {entities['returncode']}")
            
        enhanced_stories.append(enhanced_story)
        
        # Save after each story is processed (incremental save)
        with open(output_filename, 'w') as f:
            json.dump(enhanced_stories, f, indent=2)
        
        # Be respectful to the API
        time.sleep(1)

    # Final summary
    print(f"\n{'='*60}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total stories loaded: {len(all_stories)}")
    print(f"Filtered out (calendars, columns, etc.): {len(filtered_out)}")
    print(f"Randomly sampled: {sample_size} stories")
    print(f"Excluded (not Eastern Shore focused): {len(screened_out)}")
    if starting_count > 0:
        print(f"Previously processed: {starting_count}")
        print(f"Newly processed in this run: {len(enhanced_stories) - starting_count}")
    print(f"Total successfully processed with entities: {len(enhanced_stories)}")
    print(f"\nOutput saved to: {output_filename}")
    print(f"(File is saved incrementally after each story)")
    
    # Show sample of excluded stories
    if screened_out:
        print(f"\n⊘ Sample of {min(10, len(screened_out))} excluded stories (not Eastern Shore focused):")
        for item in screened_out[:10]:
            print(f"  - {item['title'][:70]}")
            print(f"    Reason: {item['reasoning']}")
        if len(screened_out) > 10:
            print(f"  ... and {len(screened_out) - 10} more excluded")
    
    # Print error summary if there were any
    if errors:
        print(f"\n⚠️  {len(errors)} stories had errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    # Count successful extractions
    successful = sum(1 for s in enhanced_stories if 'entity_extraction_error' not in s)
    print(f"\n✓ Successfully extracted entities from {successful}/{len(enhanced_stories)} stories")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()