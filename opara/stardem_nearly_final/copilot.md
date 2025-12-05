# Beatbook Generator Development - Conversation Summary

## December 1-4, 2025

### Initial Request: Updating the Beatbook Generator

The project began with a request to update `beatbook_generator.py` to create a more reporter-friendly beat book while preserving the Talbot County demographic context. The goal was to move away from a formal, executive-summary style toward something more practical and newsroom-friendly.

### Key Requirements

The user wanted several specific changes:

1. **No default filename**: Stop saving to `beatbook_v4.md` by default
2. **Use existing metadata**: Leverage pre-extracted data (people, places, organizations) from `source_stories.json` instead of re-extracting from text
3. **Business-casual tone**: Write like you're briefing a colleague, not writing an academic paper
4. **Concise sections**: Short, approachable introduction with no "executive summary" language
5. **Brief geography**: Only include truly important patterns; don't make demographic claims unless clearly supported
6. **Curated examples**: Select 4-6 representative stories (breaking news, feature, profile, in-depth) with explanations
7. **Limited follow-ups**: Max 5 potential follow-ups with a disclaimer that data may be outdated
8. **Preserve demographic context**: Keep all Talbot County demographic information intact

### First Iteration: Metadata-Focused Approach

I initially created a complete rewrite that:
- Added `analyze_metadata()` function to extract patterns from story metadata using Counter
- Created `select_representative_stories()` to pick diverse examples
- Added `identify_followups()` to find up to 5 potential follow-up angles
- Replaced the formal prompt with a more conversational one
- Changed default output to `beatbook.md` in the same directory as input

However, the user then asked to undo these changes, realizing they wanted to preserve more of the original structure.

### Second Iteration: Hybrid Approach

After restoring the original file, I made a more measured update that:
- **Kept the two-pass batch processing approach** from the original
- **Added metadata analysis** for efficiency (people, places, orgs frequency counts)
- **Enhanced with new functions**: `select_representative_stories()` and `identify_followups()`
- **Updated the main synthesis prompt** to be more reporter-friendly while preserving depth
- **Preserved all Talbot County demographic context** in the prompts
- **Changed default output** from `talbot_beatbook_v4.md` to `beatbook.md`
- **Added dedicated sections**: "Story Examples" and "Potential Follow-Ups" with appropriate disclaimers

The hybrid approach maintained the comprehensive analysis capabilities while adding practical, newsroom-friendly features.

### Working with the Script

Throughout the conversation, we addressed several practical issues:

- **File location confusion**: The script was in `stardem_draft` folder but the user was in `stardem_nearly_final`
- **API key errors**: Needed to configure LLM model keys (resolved by using `groq/openai/gpt-oss-120b`)
- **File management**: Copied `source_stories.json` and `beatbook_generator.py` to the working directory
- **Renaming files**: Helped rename outputs from `beatbook_v5.md` to `talbot_beatbook_v5.md`

### Third Iteration: Narrative Version (v6)

The final major update requested a more narrative-driven beat book that:
- Reads like a story, not just a reference document
- Uses flowing paragraphs instead of bullet points
- Employs storytelling techniques (setting scenes, connecting threads)
- Maintains business-casual tone while being more engaging
- Keeps sections concise but compelling
- Weaves demographic context naturally into the narrative

The updated prompt now instructs the LLM to:
- Write a warm, welcoming introduction (like sitting down with coffee)
- Create narrative sections that flow like feature writing
- Use specific examples to illustrate patterns
- Write brief narrative intros before reference lists
- Make it feel like colleague-to-colleague conversation

### Technical Details

**File locations:**
- Script: `/workspaces/jour329w_fall2025/opara/stardem_nearly_final/beatbook_generator.py`
- Data: `/workspaces/jour329w_fall2025/opara/stardem_nearly_final/source_stories.json`
- Outputs: `talbot_beatbook_v5.md`, `talbot_beatbook_v6.md`

**Command used:**
```bash
uv run beatbook_generator.py source_stories.json -o talbot_beatbook_v6.md -t "Talbot County Public Safety" -m groq/openai/gpt-oss-120b
```

**Key functions added:**
- `analyze_metadata()`: Extracts patterns from pre-existing metadata
- `select_representative_stories()`: Picks diverse examples with explanations
- `identify_followups()`: Finds up to 5 potential follow-up angles
- `generate_beatbook()`: Creates the final narrative beat book

### Outcome

The final script creates a beat book that:
- Preserves comprehensive Talbot County demographic context
- Uses existing metadata for efficiency
- Generates narrative-driven, engaging content
- Includes curated story examples with rationale
- Provides practical follow-up suggestions with disclaimers
- Maintains business-casual, newsroom-friendly tone
- Outputs to customizable filename (default: `beatbook.md`)

The evolution from formal reference document to narrative guide reflects the user's goal of creating a more usable, practical tool for reporters joining the public safety beat in Talbot County.
