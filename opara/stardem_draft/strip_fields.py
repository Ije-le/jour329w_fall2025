import json
import re

def extract_summary_with_quotes(content):
    """Extract a summary that preserves direct quotes from the content."""
    if not content:
        return ""
    
    # Clean up metadata from content
    # Remove newspaper name (e.g., "| Star Democrat, The (Easton, MD)")
    content = re.sub(r' \| Star Democrat, The \(Easton, MD\)', '', content)
    
    # Remove Author/Byline lines (e.g., "Author/Byline: Natalie Jones |")
    content = re.sub(r'\n\n\s*Author/Byline: [^\n]+ \|', '', content)
    
    # Remove "Read News Document\n\n CITY —" patterns
    content = re.sub(r'Read News Document\n\n\s+[A-Z]+ —', '', content)
    content = re.sub(r'Read News Document\n\n\s+[A-Z]+\s*\u2014', '', content)
    
    # Find all direct quotes (text within quotation marks)
    quotes = re.findall(r'"([^"]+)"', content)
    
    # Get first ~700 characters as context
    first_part = content[:700].strip()
    
    # Build summary: context + quotes
    summary_parts = [first_part]
    
    if quotes:
        summary_parts.append("\n\nKey quotes:")
        for i, quote in enumerate(quotes[:7], 1):  # Keep first 7 quotes
            summary_parts.append(f'"{quote}"')
    
    summary = ' '.join(summary_parts)
    
    # If still too long, truncate but keep it coherent
    if len(summary) > 1500:
        summary = summary[:1497] + "..."
    
    return summary

# Load stories
with open('source_stories_subset.json') as f:
    stories = json.load(f)

# Strip unwanted fields and summarize content
cleaned_stories = []
for story in stories:
    content = story.get('content', '')
    summary = extract_summary_with_quotes(content)
    
    cleaned_story = {
        'title': story.get('title', ''),
        'date': story.get('date', ''),
        'author': story.get('author', ''),
        'content': summary,  # Summarized content with quotes
        'docref': story.get('docref', ''),
        'people': story.get('people', []),
        'places': story.get('places', []),
        'organizations': story.get('organizations', [])
    }
    cleaned_stories.append(cleaned_story)

# Save back to the same file
with open('source_stories_subset.json', 'w') as f:
    json.dump(cleaned_stories, f, indent=2)

print(f'Cleaned and summarized {len(cleaned_stories)} stories')
print('Removed: article_id, explanation, year, month, day, llm_classification_meta, model, llm_failed, eastern_shore_screening, reasoning, is_eastern_shore_focused, content_source')
print('Content: Summarized with quotes preserved')
print('Updated: source_stories_subset.json')
