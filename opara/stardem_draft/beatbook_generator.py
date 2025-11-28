#!/usr/bin/env python3
"""
Generate a reporter's guide from a large collection of news stories.
Two-pass approach: extract key information, then synthesize into narrative.
"""

import json
import llm
import sys
from pathlib import Path

def get_model(model_name=None):
    """Get the LLM model to use."""
    if model_name:
        return llm.get_model(model_name)
    # Use default model
    return llm.get_model()

def extract_from_batch(stories, batch_num, model):
    """First pass: extract key information from a batch of stories."""
    prompt = f"""You are analyzing news coverage to help onboard a new reporter. Your focus should be on public safety stories from Talbot County, Maryland. 

From these {len(stories)} news stories, extract:
1. Public safety themes and patterns (law enforcement, fire/EMS, violent crime, property crime, emergency response)
2. Geographic patterns (which communities: Easton, St. Michaels, Oxford, Trappe, rural areas)
3. Key people mentioned (local officials, law enforcement, emergency personnel - with their roles)
4. Important organizations (Talbot County Sheriff's Office, local police departments, fire departments, emergency services)
5. Significant incidents and multi-jurisdiction responses
6. Recurring issues that connect multiple stories

Be concise but capture location-specific details and patterns unique to Talbot County.

Stories:
{json.dumps(stories, indent=2)}

Provide a structured summary:"""
    
    print(f"Processing batch {batch_num}...", file=sys.stderr)
    response = model.prompt(prompt)
    return response.text()

def synthesize_intermediate(summaries, level, model):
    """Synthesize a group of summaries into a higher-level summary."""
    combined = "\n\n---\n\n".join(
        f"SECTION {i+1}:\n{summary}" 
        for i, summary in enumerate(summaries)
    )
    
    prompt = f"""Consolidate these {len(summaries)} coverage summaries into a single comprehensive summary.

Preserve all important:
- People and their roles
- Organizations and institutions
- Major themes and issues
- Significant events and developments
- Ongoing debates and conflicts

Be thorough but concise. This will be combined with other summaries later.

SUMMARIES TO CONSOLIDATE:
{combined}

CONSOLIDATED SUMMARY:"""
    
    print(f"Consolidating level {level} ({len(summaries)} summaries)...", file=sys.stderr)
    response = model.prompt(prompt)
    return response.text()

def synthesize_guide(batch_summaries, topic, model, max_summaries_per_level=5):
    """Hierarchically synthesize batch summaries into a coherent narrative guide."""
    
    # If we have few enough summaries, synthesize directly
    if len(batch_summaries) <= max_summaries_per_level:
        combined = "\n\n---\n\n".join(
            f"BATCH {i+1}:\n{summary}" 
            for i, summary in enumerate(batch_summaries)
        )
    else:
        # Hierarchical consolidation
        current_level = batch_summaries
        level = 1
        
        while len(current_level) > max_summaries_per_level:
            next_level = []
            for i in range(0, len(current_level), max_summaries_per_level):
                group = current_level[i:i+max_summaries_per_level]
                consolidated = synthesize_intermediate(group, level, model)
                next_level.append(consolidated)
            current_level = next_level
            level += 1
        
        # Final consolidation
        combined = "\n\n---\n\n".join(
            f"SECTION {i+1}:\n{summary}" 
            for i, summary in enumerate(current_level)
        )
    
    prompt = f"""You are analyzing public safety stories from Talbot County, Maryland, published in the Star Democrat newspaper. Create a comprehensive, narrative-driven geographic beat book that examines public safety patterns, trends, and interconnected issues across Talbot County communities including Easton (county seat), St. Michaels, Oxford, Trappe, and rural areas.

**TALBOT COUNTY DEMOGRAPHIC CONTEXT:**
Use this demographic information to provide context throughout your analysis where relevant:

**Population & Geography:**
- Population: Approximately 37,500 residents (2023 estimate)
- County seat: Easton (population ~16,800)
- Major towns: St. Michaels (~1,000), Oxford (~600), Trappe (~1,200)
- Land area: 269 square miles on Maryland's Eastern Shore
- Density: Mixed urban (Easton), historic waterfront towns, and rural areas

**Demographics:**
- Race/Ethnicity: 78.5% White, 14.5% Black/African American, 4.8% Hispanic/Latino, 2.2% other
- Median age: 48.5 years (significantly older than Maryland average of 39)
- 65 years and older: 24.8% (aging population)

**Economic Indicators:**
- Median household income: $72,300 (Maryland: $97,300)
- Per capita income: $43,800
- Poverty rate: 9.5% (below Maryland average of 9.8%)
- Unemployment rate: ~3.5%

**Education:**
- High school graduation rate: 92.3%
- Bachelor's degree or higher: 39.8%

**Housing & Community:**
- Homeownership rate: 73.8%
- Median home value: $365,000
- Significant seasonal tourism economy (St. Michaels, Oxford)
- Mix of working waterfront, agriculture, and service economy

**Relevance to Public Safety:**
Consider how these demographics might influence public safety patterns:
- Aging population may affect emergency medical service demands
- Economic disparities between waterfront towns and rural areas
- Seasonal population fluctuations from tourism
- Rural geography affecting response times and multi-jurisdiction coordination
- Lower poverty rate but income below state average

Use this demographic context naturally throughout your analysis to provide depth and understanding of public safety challenges and patterns specific to Talbot County.

Your beat book should include these sections in order:

**1. HOW TO USE THIS BEAT BOOK**
Write 4-5 paragraphs explaining:
- What this beat book contains and its purpose for reporters covering Talbot County public safety
- How the interconnected issues are numbered and cross-referenced throughout the document
- How to navigate between thematic sections, geographic analysis, and the source directory
- How to use the unresolved stories section for follow-up reporting
- Best practices for using this as an onboarding tool, reference guide, and story planning resource
- Include this demographic context resource: For additional context on Talbot County demographics, population, and community characteristics, see: https://data.census.gov/profile/Talbot_County,_Maryland?g=050XX00US24041#populations-and-people

**2. EXECUTIVE SUMMARY**
Provide a narrative overview (4-5 paragraphs) of the most significant public safety patterns in Talbot County. Write this as a cohesive story that flows naturally, not bullet points. Include specific geographic details about which communities are most affected by different issues. Make this compelling and informative.

**3. THEMATIC SECTIONS** (5-8 sections)
Organize stories into themes like law enforcement, fire/EMS, violent crime, property crime, emergency infrastructure. For each section:
- Write 4-5 narrative paragraphs that tell the story of this issue in Talbot County
- Weave in specific examples from stories naturally within the narrative flow
- Note geographic patterns and integrate quotes from local officials/residents seamlessly
- Reference numbered interconnected issues where relevant (e.g., "this reflects the pattern described in #2")
- After the narrative, list 8-12 representative stories with headlines, dates, locations, and 1-2 sentence descriptions
- IMPORTANT: Only include markdown links [Story Title](url) if a valid "docref" URL exists in the source JSON data for that story. If no docref URL exists, list the story title without a link. DO NOT create fake or placeholder links.

**4. GEOGRAPHIC ANALYSIS**
For each major area (Easton, St. Michaels, Oxford, Trappe, rural areas), write 3-4 narrative paragraphs that tell the story of public safety in that community. Use a storytelling approach that paints a picture of each place. Discuss types of incidents, unique challenges, emergency service responses, and community resources.

**5. INTERCONNECTED ISSUES**
Identify 4-6 major themes that connect multiple stories across categories and locations. Number each issue (#1, #2, etc.) and write 2-3 narrative paragraphs explaining:
- What the pattern is and why it matters
- How it manifests in different communities within Talbot County
- Which specific stories and incidents illustrate this pattern
- What it reveals about public safety challenges and opportunities in the county

**6. UNRESOLVED STORIES & FOLLOW-UP OPPORTUNITIES**
Identify 6-10 stories or issues that reporters should continue tracking:
- Pending investigations or court cases with unclear outcomes
- Ongoing policy debates at town councils or county government
- Emerging patterns that need deeper investigation
- Stories with unanswered questions or community concerns
For each, write 3-4 sentences explaining what's unresolved, why it matters to the community, and what questions reporters should pursue.
IMPORTANT: Only include markdown links [Story Title](url) if a valid "docref" URL exists in the source JSON data. If no docref URL exists, reference the story without a link. DO NOT create fake or placeholder links.

**7. SOURCE DIRECTORY**
List all stories cited throughout the beat book, organized chronologically. For each include:
- Headline/title (as a markdown link [Headline](url) ONLY if a valid "docref" URL exists in the source JSON data; otherwise list title without a link)
- Date published
- Primary location in Talbot County
- Brief 1-2 sentence description of the story
Do NOT include reporter contact information. 
CRITICAL: Only use actual docref URLs from the source data. DO NOT create fake links like example.com or placeholder URLs. If no docref exists for a story, simply list the title as plain text.

Write in a narrative, engaging journalistic style throughout. Use specific place names, weave in quotes naturally, tell stories rather than listing facts. Paint pictures with words. Make this read like a comprehensive narrative guide that brings Talbot County's public safety landscape to life, not a dry reference document.

COVERAGE SUMMARIES:
{combined}

TALBOT COUNTY PUBLIC SAFETY BEAT BOOK:"""
    
    print("Synthesizing final guide...", file=sys.stderr)
    response = model.prompt(prompt)
    return response.text()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate a reporter guide from news stories JSON'
    )
    parser.add_argument('input_file', help='Path to JSON file with news stories')
    parser.add_argument('-o', '--output', default='talbot_beatbook_v4.md',
                       help='Output file for the guide (default: talbot_beatbook_v4.md)')
    parser.add_argument('-b', '--batch-size', type=int, default=30,
                       help='Number of stories per batch (default: 30)')
    parser.add_argument('-m', '--model', 
                       help='LLM model to use (default: llm default model)')
    parser.add_argument('-t', '--topic', default='this beat',
                       help='Topic/beat name for the guide')
    parser.add_argument('--summaries-only', action='store_true',
                       help='Save batch summaries without final synthesis')
    parser.add_argument('--debug', action='store_true',
                       help='Save intermediate outputs for debugging')
    
    args = parser.parse_args()
    
    # Load stories
    print(f"Loading stories from {args.input_file}...", file=sys.stderr)
    with open(args.input_file, 'r') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if isinstance(data, list):
        stories = data
    elif isinstance(data, dict) and 'stories' in data:
        stories = data['stories']
    elif isinstance(data, dict) and 'articles' in data:
        stories = data['articles']
    else:
        print("Error: JSON structure not recognized. Expected a list or dict with 'stories' or 'articles' key.", 
              file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded {len(stories)} stories", file=sys.stderr)
    
    # Get model
    model = get_model(args.model)
    print(f"Using model: {model.model_id}", file=sys.stderr)
    
    # First pass: extract from batches
    batch_summaries = []
    num_batches = (len(stories) + args.batch_size - 1) // args.batch_size
    
    for i in range(0, len(stories), args.batch_size):
        batch = stories[i:i+args.batch_size]
        batch_num = i // args.batch_size + 1
        summary = extract_from_batch(batch, batch_num, model)
        batch_summaries.append(summary)
        
        # Debug: save each batch summary
        if args.debug:
            debug_file = f"debug_batch_{batch_num:03d}.md"
            with open(debug_file, 'w') as f:
                f.write(summary)
    
    # Debug: check total size of all summaries
    if args.debug:
        total_chars = sum(len(s) for s in batch_summaries)
        total_words = sum(len(s.split()) for s in batch_summaries)
        print(f"\nDEBUG: Total summaries size:", file=sys.stderr)
        print(f"  {total_chars:,} characters", file=sys.stderr)
        print(f"  {total_words:,} words", file=sys.stderr)
        print(f"  ~{total_words * 1.3:.0f} tokens (estimate)", file=sys.stderr)
    
    # Save batch summaries if requested
    if args.summaries_only:
        output_file = args.output.replace('.md', '_summaries.md')
        with open(output_file, 'w') as f:
            for i, summary in enumerate(batch_summaries, 1):
                f.write(f"\n\n## Batch {i}\n\n{summary}\n")
        print(f"Batch summaries saved to {output_file}", file=sys.stderr)
        return
    
    # Second pass: synthesize into guide
    guide = synthesize_guide(batch_summaries, args.topic, model)
    
    # Save final guide
    with open(args.output, 'w') as f:
        f.write(f"# Reporter's Guide: {args.topic.title()}\n\n")
        f.write(guide)
    
    print(f"\n✓ Guide saved to {args.output}", file=sys.stderr)
    print(f"  Processed {len(stories)} stories in {num_batches} batches", file=sys.stderr)

if __name__ == '__main__':
    main()