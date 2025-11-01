#!/usr/bin/env python3
"""
classify_topics.py

Reads `stardem_sample.json` (expected in the same directory), asks the LLM to assign exactly one topic
from a fixed list for each story, and saves the results to `stardem_topics_classified.json`.

This script calls the `llm` CLI via subprocess. It prefers running via `uv run llm` if available,
falling back to `llm` directly. The script targets the Anthropic Claude Sonnet 4.5 model; you may need
to adapt the model name to match your `llm` installation.

Usage (from the `opara/stardem_topics` directory):

    uv run python classify_topics.py

or

    python classify_topics.py

Notes:
- Requires the `llm` CLI installed and configured (or run via `uv run llm ...`).
- If your `llm` CLI uses different subcommands/flags, adjust the `LLM_CANDIDATES` list below.
"""

import json
import subprocess
import shutil
import time
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_FILE = SCRIPT_DIR / 'stardem_sample.json'
OUTPUT_FILE = SCRIPT_DIR / 'stardem_topics_classified.json'

TOPICS = [
    "Education",
    "Health",
    "Police & Crime",
    "Local government",
    "Judiciary",
    "Public Safety",
    "Election",
    "Chesapeake",
    "Food",
    "Community Events & Culture",
    "Movies & Shows",
    "Sports",
    "Religion",
    "Obituaries",
    "Other"
]

# Candidate CLI invocations to try. Adjust if your 'llm' uses a different command layout.
LLM_CANDIDATES = [
    ["uv", "run", "llm", "query", "--model", "anthropic/claude-sonnet-4-5", "--input"],
    ["llm", "query", "--model", "anthropic/claude-sonnet-4-5", "--input"],
    ["uv", "run", "llm", "chat", "--model", "anthropic/claude-sonnet-4-5", "--input"],
    ["llm", "chat", "--model", "anthropic/claude-sonnet-4-5", "--input"]
]

# Delay between LLM calls, seconds
DELAY = 0.6


def call_llm(prompt, timeout=90):
    """Try to call the LLM CLI with a list of candidate commands. Returns stdout on success or
    raises RuntimeError if none of the candidates work.
    """
    for base in LLM_CANDIDATES:
        # check the CLI binary exists
        if shutil.which(base[0]) is None:
            continue
        cmd = list(base)
        cmd.append(prompt)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except Exception:
            continue
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
        # try next candidate
    raise RuntimeError("Unable to call LLM CLI with the configured command candidates.\n"
                       "Ensure `llm` is installed and accessible (or run via `uv run llm`).")


def choose_topic_from_response(resp):
    """Map model response to one of the canonical TOPICS.
    Tolerate extra whitespace, quotes, or short explanations.
    """
    s = resp.strip().strip('"\'')
    s_lower = s.lower()
    # Exact match first
    for t in TOPICS:
        if s_lower == t.lower():
            return t
    # Find a topic name inside the response
    for t in TOPICS:
        if t.lower() in s_lower:
            return t
    # Token-level fallback
    tokens = [tok.strip('.,"\'').lower() for tok in s.split()]
    for t in TOPICS:
        for word in t.lower().split():
            if word in tokens:
                return t
    return "Other"


def build_prompt(story):
    title = story.get('title') or story.get('headline') or ''
    content = story.get('content') or story.get('summary') or ''
    short_content = (content[:600] + '...') if len(content) > 600 else content
    prompt = (
        "Assign this news story to exactly ONE topic from the following list:\n"
        f"{', '.join(TOPICS)}\n\n"
        "Choose the topic that best represents what this story is primarily about.\n"
        "Return ONLY the topic name (no explanation, no punctuation).\n\n"
        f"Title: {title}\n\n"
        f"Content (short): {short_content}\n"
    )
    return prompt


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}\nPlease place `stardem_sample.json` in this directory.")
        sys.exit(2)

    with INPUT_FILE.open('r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("Expected input JSON to be a list of stories (top-level list).")
        sys.exit(2)

    enhanced = []
    total = len(data)
    print(f"Processing {total} stories...")

    for i, story in enumerate(data, start=1):
        try:
            prompt = build_prompt(story)
            resp = call_llm(prompt)
            topic = choose_topic_from_response(resp)
        except Exception as e:
            print(f"[#{i}/{total}] LLM call failed: {e}. Setting topic='Other'.")
            topic = "Other"
        story['topic'] = topic
        enhanced.append(story)
        print(f"[#{i}/{total}] -> {topic}")
        time.sleep(DELAY)

    with OUTPUT_FILE.open('w', encoding='utf-8') as f:
        json.dump(enhanced, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUTPUT_FILE} ({len(enhanced)} stories)")


if __name__ == '__main__':
    main()
