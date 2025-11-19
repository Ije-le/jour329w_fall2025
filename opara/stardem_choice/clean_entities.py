import json
import re
import argparse
from pathlib import Path

def extract_author_names(story):
    """Extract author names from the story's author field."""
    author_names = set()
    author_field = story.get('author', '')
    
    if not author_field:
        return author_names
    
    # Common patterns in bylines
    # "Mike Detmer; mdetmer@chespub.com"
    # "Molly O Brien; Herald & News"
    # "Staff Report"
    
    # Split on semicolons and extract names before email or organization
    parts = author_field.split(';')
    for part in parts:
        name = part.strip()
        # Skip email addresses
        if '@' in name:
            continue
        # Skip common non-name patterns
        if name.lower() in ['staff report', 'staff', 'contributed', 'special']:
            continue
        # Skip organization names
        if any(org in name.lower() for org in ['herald', 'news', 'democrat', 'star', 'publishing']):
            continue
        
        if name:
            author_names.add(name)
    
    return author_names

def normalize_name(name):
    """Normalize a name for comparison (lowercase, remove punctuation)."""
    # Extract just the name part before comma if present
    name_part = name.split(',')[0].strip()
    # Remove common punctuation and normalize
    normalized = re.sub(r'[^\w\s]', '', name_part.lower())
    return normalized

def extract_name_parts(name):
    """Extract first and last name from a full name."""
    # Get the name before any comma
    name_part = name.split(',')[0].strip()
    # Remove punctuation
    clean_name = re.sub(r'[^\w\s]', '', name_part)
    # Split into parts
    parts = clean_name.lower().split()
    return set(parts)

def is_news_organization(org_name):
    """Check if an organization is a news/publishing organization."""
    news_orgs = [
        'star democrat',
        'chesapeake publishing',
        'apgmedia',
        'adams publishing',
        'herald',
        'associated press',
        'ap news',
        'reuters',
        'usa today',
        'washington post',
        'baltimore sun',
        'capital gazette'
    ]
    
    org_lower = org_name.lower()
    return any(news_org in org_lower for news_org in news_orgs)

def clean_story_entities(story):
    """Remove authors and news organizations from a story's entities."""
    # Get author names
    author_names = extract_author_names(story)
    
    # Create sets of author name parts for better matching
    author_name_parts = []
    for author in author_names:
        parts = extract_name_parts(author)
        if len(parts) >= 2:  # Only consider if we have at least 2 name parts (first + last)
            author_name_parts.append(parts)
    
    # Clean people array
    original_people = story.get('people', [])
    cleaned_people = []
    removed_people = []
    
    for person in original_people:
        person_parts = extract_name_parts(person)
        
        # Check if this person matches an author
        # Match if at least 2 name parts overlap (e.g., "mike" and "detmer")
        is_author = False
        for author_parts in author_name_parts:
            overlap = person_parts.intersection(author_parts)
            if len(overlap) >= 2:  # Both first and last name match
                is_author = True
                break
        
        if is_author:
            removed_people.append(person)
        else:
            cleaned_people.append(person)
    
    # Clean organizations array
    original_orgs = story.get('organizations', [])
    cleaned_orgs = []
    removed_orgs = []
    
    for org in original_orgs:
        if is_news_organization(org):
            removed_orgs.append(org)
        else:
            cleaned_orgs.append(org)
    
    # Update the story
    story['people'] = cleaned_people
    story['organizations'] = cleaned_orgs
    
    return {
        'removed_people': removed_people,
        'removed_orgs': removed_orgs
    }

def main():
    parser = argparse.ArgumentParser(description='Clean author names and news organizations from entity extractions')
    parser.add_argument('--input', required=True, help='Input JSON file to clean')
    parser.add_argument('--output', help='Output JSON file (if not specified, will add _cleaned suffix)')
    parser.add_argument('--in-place', action='store_true', help='Update the input file in place')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed without making changes')
    
    args = parser.parse_args()
    
    # Load the data
    print(f"Loading {args.input}...")
    with open(args.input) as f:
        stories = json.load(f)
    
    print(f"Loaded {len(stories)} stories\n")
    
    # Track statistics
    total_people_removed = 0
    total_orgs_removed = 0
    all_removed_people = []
    all_removed_orgs = []
    
    # Clean each story
    for i, story in enumerate(stories):
        result = clean_story_entities(story)
        
        if result['removed_people']:
            total_people_removed += len(result['removed_people'])
            all_removed_people.extend(result['removed_people'])
        
        if result['removed_orgs']:
            total_orgs_removed += len(result['removed_orgs'])
            all_removed_orgs.extend(result['removed_orgs'])
    
    # Print summary
    print(f"{'='*60}")
    print(f"CLEANING SUMMARY")
    print(f"{'='*60}")
    print(f"Total people removed: {total_people_removed}")
    print(f"Total organizations removed: {total_orgs_removed}")
    
    if all_removed_people:
        print(f"\nSample of removed people (first 20):")
        unique_people = list(set(all_removed_people))[:20]
        for person in unique_people:
            print(f"  - {person}")
        if len(set(all_removed_people)) > 20:
            print(f"  ... and {len(set(all_removed_people)) - 20} more unique names")
    
    if all_removed_orgs:
        print(f"\nRemoved organizations:")
        unique_orgs = list(set(all_removed_orgs))
        for org in unique_orgs:
            print(f"  - {org}")
    
    # Save the cleaned data
    if not args.dry_run:
        if args.in_place:
            output_file = args.input
            print(f"\nUpdating {output_file} in place...")
        elif args.output:
            output_file = args.output
            print(f"\nSaving cleaned data to {output_file}...")
        else:
            # Add _cleaned suffix
            input_path = Path(args.input)
            output_file = str(input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}")
            print(f"\nSaving cleaned data to {output_file}...")
        
        with open(output_file, 'w') as f:
            json.dump(stories, f, indent=2)
        
        print(f"✓ Saved {len(stories)} cleaned stories")
    else:
        print(f"\n[DRY RUN] No changes made. Remove --dry-run to apply changes.")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
