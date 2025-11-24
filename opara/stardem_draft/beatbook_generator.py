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
    
    prompt = f"""You are creating an onboarding guide for a new reporter who will be covering {topic}.

Below are comprehensive summaries of previous news coverage. 
Synthesize this into a coherent, narrative guide that includes:

1. **Overview**: What is this beat about? What are the central issues?
2. **Key Players**: Who are the most important people to know? Include their roles and why they matter.
3. **Organizations & Institutions**: What entities are central to this coverage?
4. **Major Themes & Ongoing Stories**: What are the continuing storylines and debates?
5. **Context & Background**: Essential history or context a new reporter needs.

Write this as a narrative document, not a list. Make it readable and informative. This should be comprehensive - draw on ALL the information provided.

COVERAGE SUMMARIES:
{combined}

REPORTER'S GUIDE:"""
    
    print("Synthesizing final guide...", file=sys.stderr)
    response = model.prompt(prompt)
    return response.text()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate a reporter guide from news stories JSON'
    )
    parser.add_argument('input_file', help='Path to JSON file with news stories')
    parser.add_argument('-o', '--output', default='reporter_guide.md',
                       help='Output file for the guide (default: reporter_guide.md)')
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