# From 200+ Stories to a Living Beat Book: An AI-Assisted Workflow
## Conference Presentation (10-15 minutes)

---

## SLIDE 1: The Problem We Solved

Imagine you're covering public safety in Talbot County, Maryland. You've written 200+ stories over the year. A new reporter joins your team tomorrow.

**The old way?** 
- "Here, read everything I've written"
- Hours of searching through archives
- Tribal knowledge that lives in veterans' heads
- New reporters spend weeks just getting oriented

**What if instead** you could hand them a comprehensive, personalized beat book—automatically generated from your existing coverage?

---

## SLIDE 2: What We Built

A **repeatable, AI-assisted pipeline** that transforms raw news stories into a journalism reference tool in about **90 minutes of mostly automated processing**.

**Input:** JSON file with 200-400 stories (title, content, date)

**Output:** A narrative beat book with:
- Geographic patterns and demographic context
- Who's who (key sources with contact details)
- Organizations that matter
- Story examples showing your range
- Potential follow-up angles
- All grounded in your actual coverage

---

## SLIDE 3: The Five-Step Process

Think of this like a **journalism assembly line**, where each stage adds value:

```
1️⃣ Classify by Topic
      ↓
2️⃣ Extract Entities (people, places, organizations)
      ↓
3️⃣ Analyze Metadata (who appears most often?)
      ↓
4️⃣ Generate Batch Summaries (find patterns)
      ↓
5️⃣ Synthesize Final Beat Book (narrative form)
```

Each step is **automated but overseen**—you're the editor, the AI is your research assistant.

---

## SLIDE 4: Step 1 – Topic Classification (10-15 minutes)

**The Challenge:** Not all stories belong on the public safety beat. We had education, sports, obituaries mixed in.

**The Solution:** A simple Python script that asks an LLM: *"Which topic does this story belong to?"*

```bash
uv run python classify_topics.py \
  --model anthropic/claude-sonnet-4-5
```

**What happens:**
- Script reads each story's headline + first 600 characters
- Sends to Claude with a fixed list of topics
- Gets back ONE topic per story: "Public Safety" / "Education" / "Other"
- Creates new JSON with a `topic` field

**Result:** We filtered from 400 stories down to 212 public safety stories.

**Key Learning:** The LLM is really good at this kind of categorization—95%+ accuracy in our testing.

---

## SLIDE 5: Step 2 – Entity Extraction (20-30 minutes)

**The Challenge:** Who appears in these stories? What places? Which organizations?

**The Solution:** Batch entity extraction using a carefully crafted prompt.

```bash
uv run python add_entities_clay.py \
  --model groq/meta-llama/llama-4-maverick-17b-128e-instruct \
  --input public_safety_stories.json \
  --output stories_with_entities.json
```

**The Prompt Magic:**
```
Extract ALL named entities from this PUBLIC SAFETY news story.

people: Array of ALL people mentioned (include rank, agency)
places: Array of ALL geographic locations (city, county, roads)
organizations: Array of ALL organizations (law enforcement, fire, courts)

Return ONLY valid JSON with the three arrays.
```

**Why batch?** Instead of one API call per story (expensive, slow), we send 30-50 stories per call.

**Result:** Each story now has structured metadata:
```json
{
  "title": "Sheriff's Office investigates downtown fire",
  "people": ["Sheriff Joe Gamble", "Fire Chief Alan Lowrey"],
  "places": ["Easton", "Main Street", "Talbot County"],
  "organizations": ["Talbot County Sheriff's Office", "Easton Fire Department"]
}
```

---

## SLIDE 6: Step 3 – Metadata Analysis (Instant)

**The Challenge:** 212 stories × average 5 people per story = 1,000+ mentions. Who matters most?

**The Solution:** Python's `Counter` does the math for us.

```python
from collections import Counter

all_people = [person for story in stories for person in story['people']]
top_people = Counter(all_people).most_common(15)
```

**Result:** Rankings that tell the story:
1. Sheriff Joe Gamble (34 mentions) ← Your primary source
2. Chief Alan Lowrey, Easton PD (27 mentions)
3. Brian LeCates, Emergency Services (18 mentions)

Same for places (Easton dominates), organizations (Sheriff's Office is central).

**Why this matters:** These numbers become the "Who's Who" section—automatically prioritized by actual coverage frequency.

---

## SLIDE 7: Step 4 – Batch Summarization (30-40 minutes)

**The Challenge:** 212 stories is too much context for one LLM call (token limits).

**The Solution:** Split into batches of 30, ask the LLM to summarize each batch's patterns.

**The Prompt:**
```
You are analyzing news coverage to help onboard a new reporter.
From these 30 stories, extract:
1. Public safety themes and patterns
2. Geographic patterns
3. Key people and their roles
4. Important organizations
5. Significant incidents
6. Recurring issues

Stories: [JSON of 30 stories]
```

**What we get back:** 7-8 mini-summaries like:
> "Batch 1 (stories 1-30): Heavy focus on traffic safety in Easton. 
> Sheriff Gamble mentioned in 6 stories, mostly related to community policing initiatives.
> Three mentions of Vision Zero program..."

**Key Learning:** Breaking big problems into smaller chunks is AI 101. Each batch summary is **grounded in real stories**, not hallucinated.

---

## SLIDE 8: Step 5 – Final Synthesis (15-20 minutes)

**The Challenge:** Turn metadata + batch summaries into readable narrative.

**The Solution:** One final prompt that acts like a senior editor briefing a new hire.

```bash
uv run python beatbook_generator.py \
  stories_with_entities.json \
  -o talbot_beatbook_v6.md \
  -t "Talbot County Public Safety" \
  -m groq/openai/gpt-oss-120b
```

**The Prompt (simplified):**
```
You're helping onboard a new reporter covering public safety in Talbot County.
Write a practical, narrative-driven beat book that reads like a colleague briefing 
another colleague over coffee—not a formal report.

DATASET INFO:
- 212 stories from 2024-01-02 to 2024-10-03
- Top people: Sheriff Joe Gamble (34), Chief Alan Lowrey (27)...
- Top places: Easton (89), St. Michaels (23)...
- Demographics: Population 37,800, median income $62,000...

COVERAGE SUMMARIES:
[All 7 batch summaries pasted here]

Write: Introduction, What You're Covering, Geographic Notes, Who's Who, 
Organizations to Know, Story Examples, Potential Follow-Ups
```

**Result:** A 3,000-word narrative beat book in markdown format.

---

## SLIDE 9: What the Output Looks Like

[Demo teammate shows beatbook_v6.md on screen]

**Key sections:**
1. **Warm introduction** – "Welcome to Talbot County's public safety beat..."
2. **What You're Covering** – Narrative overview with real examples
3. **Geographic Notes** – "Easton sees the bulk of activity, but don't ignore the waterfront towns..."
4. **Who's Who** – Contact list prioritized by mention frequency
5. **Organizations** – Sheriff's Office, police departments, fire services
6. **Story Examples** – 4-5 representative pieces with explanations
7. **Potential Follow-Ups** – Story angles that emerged from the data

**Tone:** Conversational, practical, grounded in actual coverage.

---

## SLIDE 10: The "So What?" – Why This Matters

**For newsrooms:**
- **Onboarding time** cut from weeks to hours
- **Institutional knowledge** captured and transferable
- **Story gaps** become visible (if no one appears less than 3 times, maybe we're missing that angle?)
- **Repeatable** – run quarterly to keep beat books current

**For reporters:**
- **Less tribal knowledge hoarding** – everyone has access to the same base knowledge
- **Quick reference** – searchable markdown you can grep/Ctrl+F
- **Story ideas** – the "Potential Follow-Ups" section is gold

**For journalism education:**
- **Students can analyze professional coverage** patterns
- **Learn by example** – see how beats are structured
- **Replicable skill** – this workflow works for sports, education, any beat

---

## SLIDE 11: What We Learned (The Hard Way)

### ✅ What Worked

**1. Batch processing is essential**
- Single-story extraction = 400 API calls = expensive + slow
- Batch extraction = 15 calls = fast + cheap

**2. Strong prompts beat fancy models**
- We tried expensive models with vague prompts → hallucinations
- We tried cheaper models with strict prompts → clean output
- **"Return ONLY valid JSON with these exact keys"** is your friend

**3. Metadata first, narrative second**
- Don't ask the AI to "figure out who's important"
- Count it yourself with Python, then feed those numbers to the LLM
- Grounding in data prevents hallucination

### ❌ What We Struggled With

**1. Name normalization**
- "Sheriff Joe Gamble" vs "Joe Gamble" vs "Sheriff Gamble"
- Solution: Manual cleanup after extraction

**2. Rate limits**
- Hit Groq's limits around story 180
- Solution: Added exponential backoff and `--delay` flags

**3. Outdated follow-ups**
- AI suggested stories we'd already covered
- Solution: Added disclaimer + manual fact-checking step

---

## SLIDE 12: Cost & Time Breakdown

**For 212 stories:**

| Step | Time | Cost (with Groq/Claude mix) |
|------|------|---------------------------|
| Topic classification | 10 min | $0.50 |
| Entity extraction (batch) | 25 min | $2.00 |
| Batch summarization | 35 min | $1.50 |
| Final synthesis | 15 min | $0.30 |
| Manual fact-checking | 30 min | Free (your time) |
| **TOTAL** | **~2 hours** | **~$4.50** |

**The real cost:** Your time setting it up initially (3-4 hours). After that, it's **push-button journalism**.

---

## SLIDE 13: Beyond Traditional Beat Books

This workflow opened doors to **experimental formats**:

[Demo teammate shows mindmap on screen]

**Interactive Mind Map (talbot_mindmap_v2.html)**
- Visual, clickable network of topics, people, places
- Color-coded by category
- Search functionality
- Story angles connected to coverage areas

**Timeline Format (in progress)**
- Using Knight Lab's TimelineJS
- Chronological view of major incidents
- Good for showing evolution of issues

**Key insight:** Once you have structured data (people, places, orgs), you can render it ANY way you want.

---

## SLIDE 14: How to Start Tomorrow

**Minimum viable workflow:**

1. **Get your stories into JSON**
   - Export from your CMS
   - Just need: `title`, `content`, `date`

2. **Pick ONE script to start with**
   - `classify_topics.py` if you need to filter stories
   - `add_entities_clay.py` if you already have a filtered set

3. **Test with 20 stories first**
   ```bash
   jq '.[0:20]' all_stories.json > test_stories.json
   ```

4. **Verify output looks reasonable**
   - Check for hallucinated names ("John Doe")
   - Confirm places are real locations

5. **Scale up to full dataset**

**Time investment:** ~4 hours to understand the workflow, then 2 hours per beat book.

---

## SLIDE 15: Open Questions & Future Work

**What we're still figuring out:**

1. **How often to regenerate?**
   - Monthly? Quarterly? After major events?
   - Incremental updates vs full regeneration?

2. **Collaborative beat books?**
   - What if 3 reporters cover different aspects of the same beat?
   - Could we merge their coverage?

3. **Multimedia integration?**
   - Most of our stories are text-only
   - How do we incorporate photos, videos, data visualizations?

4. **Bias detection?**
   - Are we over-covering certain neighborhoods?
   - Under-representing certain voices?
   - Could metadata analysis help us spot these patterns?

---

## SLIDE 16: The Human Element

**Important reminder:** This is **AI-ASSISTED**, not AI-GENERATED journalism.

**The AI does:**
- ✅ Extract entities from text
- ✅ Count frequency
- ✅ Spot patterns across many stories
- ✅ Draft narrative structure

**You still do:**
- ❌ Verify all facts
- ❌ Check contact information
- ❌ Decide which follow-ups to pursue
- ❌ Add context the AI couldn't know
- ❌ Edit for tone and accuracy

**Think of it like spell-check:** helpful automation that still requires human judgment.

---

## SLIDE 17: Resources & Code

**All our scripts are open source:**
- GitHub: `dwillis/jour329w_fall2025/opara/`
- Key files:
  - `classify_topics.py` – Topic classification
  - `add_entities_clay.py` – Batch entity extraction
  - `beatbook_generator.py` – Final synthesis
  - `beatbook_guide.md` – Full documentation

**Models we used:**
- Claude Sonnet 4.5 (classification)
- Llama 4 Maverick 17B (entity extraction)
- GPT-OSS-120B (final synthesis)

**Dependencies:**
- `llm` CLI tool (Simon Willison's wrapper)
- `uv` for Python environment management
- `jq` for JSON manipulation

---

## SLIDE 18: Questions & Contact

**Key Takeaways:**

1. Structured data (people, places, orgs) is the foundation
2. Batch processing makes AI affordable and fast
3. Strong prompts > expensive models
4. Human fact-checking is non-negotiable
5. Once you have the data, you can create ANY format (narrative, mindmap, timeline)

**What questions do you have?**

---

## APPENDIX: Common Questions

**Q: What if my CMS doesn't export to JSON?**
**A:** CSV works too. Convert with: `jq -R -s -c 'split("\n") | map(split(","))'` or use a Python script.

**Q: Can I use free models?**
**A:** Yes! We used mostly free/cheap models (Llama, GPT-OSS). Total cost was under $5.

**Q: How accurate is the entity extraction?**
**A:** ~90-95% in our testing. You'll need to manually fix ~10 names out of 100.

**Q: What if I don't know Python?**
**A:** You don't need to! Just run the commands we provide. It's like running `git` commands.

**Q: Can this work for other beats?**
**A:** Yes! We've tested it on arts/culture, education, and sports. Same workflow, different content.

**Q: How do you prevent hallucinations?**
**A:** 
1. Ground prompts in actual story text (no "make up" instructions)
2. Use metadata counts to verify claims
3. Fact-check the final output
4. Use models good at following strict instructions

**Q: What about privacy/confidentiality?**
**A:** All our stories were already published. For sensitive data, use local models or on-premise hosting.

---

## SPEAKING NOTES

**Introduction (2 min):**
- Start with the relatable problem: new reporter, overwhelming archives
- Emphasize this is about augmenting journalism, not replacing it
- Set expectation: this is a process talk, demos happen alongside

**Process walkthrough (8-10 min):**
- Go through steps 1-5 linearly
- Use concrete numbers from our actual project
- When you say "At this point my teammate will show you...", pause for demos
- Connect each step to journalism values (accuracy, sourcing, context)

**Lessons learned (2-3 min):**
- Be honest about failures and iterations
- Emphasize the learning curve is real but manageable
- Highlight unexpected benefits (mindmap, timeline formats)

**Wrap-up (1-2 min):**
- Reiterate: AI-assisted, not AI-generated
- Practical next steps anyone can take
- Open for questions

**Timing tips:**
- If running short: expand on "What We Learned" section
- If running long: combine Steps 3+4 into one slide
- Save 3-4 minutes at end for Q&A
