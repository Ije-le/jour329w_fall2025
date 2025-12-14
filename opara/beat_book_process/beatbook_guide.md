# Beat Book Gudie               12/13/2025 
*A beginner‑friendly, step‑by‑step guide for reporters who want a quick, repeatable workflow that turns a pile of news stories into a practical “beat book.”*  

---  

## 1. What is a Beat Book?  

| Term | Plain‑English definition |
|------|---------------------------|
| **Beat** | The specific area you cover (e.g., “Public Safety in Talbot County”). |
| **Beat Book** | A concise, reporter‑friendly reference that summarises everything you need to know about that beat: key topics, frequent people, organisations, places, recent story patterns, and ideas for follow‑up angles. Think of it as a “cheat sheet” you hand to a new colleague on day 1. |

**Why it matters**

* **Speed up onboarding.** A junior reporter can get up to speed in hours instead of weeks.  
* **Spot gaps & angles.** Patterns in the data surface stories you might otherwise miss.  
* **Stay organized.** All the “who, what, where” is in one place, ready for quick reference.  

---

## 2. End‑to‑End Workflow Overview  

```
1️⃣  Gather source stories   ──► 2️⃣  Classify topics
          │                         │
          ▼                         ▼
3️⃣  Extract entities (people, places, organisations)
          │
          ▼
4️⃣  Analyse metadata (counts, trends)
          │
          ▼
5️⃣  Generate the Beat Book with an LLM
          │
          ▼
6️⃣  Fact‑check / refine the output
```

Below each step we’ll explain *what* you’re doing, *why* it matters, the *commands* you’ll run (no coding required), and common *gotchas*.

---

## 3. Step‑by‑Step Guide  

### 3.1. Gather & Prepare Source Stories  

**What you need**  
* A JSON file that contains the raw articles you want to analyse.  
* Minimum fields: `title`, `content` (full story text). Optional but helpful: `date`, `section`, `url`.  

**How to get it**  

| Method | Quick tip |
|--------|-----------|
| **Download from your CMS** (e.g., WordPress export → JSON) | Keep the file in the same folder as the scripts; name it `public_safety_stories.json` (or whatever you like). |
| **Scrape a public site** | Use a simple web‑scraper (e.g., a browser extension that exports to JSON). No Python needed. |
| **Ask the data team** | They can give you a CSV; just rename the columns to `title` and `content` and convert to JSON (`jq -R -s -c 'split("\n") | map(select(. != ""))'`). |

**Result** – a file that looks like:

```json
[
  {
    "title": "Firefighters rescue family from flooded home",
    "content": "Easton, MD – ...",
    "date": "2024‑10‑03"
  },
  {
    "title": "Police arrest suspect in downtown robbery",
    "content": "St. Michaels, MD – ...",
    "date": "2024‑09‑28"
  }
]
```

---

### 3.2. Classify Each Story by Topic  

*Why?*  It lets you separate “Public Safety” from “Education,” “Sports,” etc., so the beat book only uses the relevant set.

**Tool:** `classify_topics.py` (already written for you).  

**Command (run from the folder that contains the script):**

```bash
# Option A – using uv (recommended, handles dependencies automatically)
uv run python classify_topics.py --model anthropic/claude-sonnet-4-5

# Option B – if you already have the `llm` CLI installed
python classify_topics.py --model anthropic/claude-sonnet-4.5
```

**What the script does**

1. Reads `stardem_sample.json` (replace the filename with your own JSON if needed).  
2. Sends each story **one‑by‑one** to the LLM with a prompt like:  

   ```
   Assign this story to ONE topic from:
   Education, Health, Police & Crime, …, Other

   Title: <title>
   Content (short): <first 600 chars>
   ```

3. The LLM replies with **just the topic name** (e.g., `Public Safety`).  
4. The script adds a new field `"topic"` to each story and writes `stardem_topics_classified.json`.  

**Result:** a JSON where each story now has a `topic` key.  

**Tip:** If you only care about one beat (e.g., Public Safety), you can filter later:

```bash
jq '[ .[] | select(.topic=="Public Safety") ]' stardem_topics_classified.json > public_safety_stories.json
```

---

### 3.3. Extract Named Entities (People, Places, Organisations)  

*Why?*  These are the “who, where, and who‑else” that will populate the “Who’s Who,” “Places,” and “Organizations to Know” sections of your beat book.

You have two ready‑made scripts:  

| Script | When to use | How it works |
|--------|-------------|--------------|
| `add_entities_clay.py` (or the newer `stardem_choice_add_entities_clay.py`) | Faster, **batch** extraction (good for 300‑500 stories). | Sends the full story text to the LLM with a detailed prompt that returns JSON arrays of `people`, `places`, `organizations`. |
| `add_entities.py` (or `stardem_choice_add_entities.py`) | **Single‑story** extraction (good for testing or very large corpora where you want to throttle API calls). | Calls the LLM **once per story** and writes the enriched story back. |

#### 3.3.1. Running the batch version (most common)

```bash
python add_entities_clay.py \
  --model groq/meta-llama/llama-4-maverick-17b-128e-instruct \
  --input public_safety_stories.json \
  --output stories_with_entities.json \
  --sample-size 300   # optional: process a random sample
```

**What the prompt looks like (inside the script):**

```
Extract ALL named entities from this PUBLIC SAFETY news story and return them in JSON format.

people: [...]
places: [...]
organizations: [...]

Story Title: <title>
Story Content: <full text>

Return only valid JSON with the three arrays.
```

**Result:** each story now contains three new arrays:

```json
{
  "title": "...",
  "content": "...",
  "people": ["Chief John Smith, Easton Police Department", "Mayor Carol Westfall, Easton"],
  "places": ["Easton, Maryland", "Route 50"],
  "organizations": ["Easton Police Department", "Talbot County Fire Service"]
}
```

#### 3.3.2. Running the single‑story version (if you hit rate‑limits)

```bash
python add_entities.py \
  --model anthropic/claude-sonnet-4-5 \
  --input public_safety_stories.json \
  --output stories_with_entities.json \
  --limit 50          # test on the first 50 stories first
```

**Why you might need the single‑story version**

* Your API provider throttles large payloads.  
* You want to manually inspect the LLM’s response for the first few stories before scaling up.  

---

### 3.4. Analyse Metadata (Counts, Trends, Date Range)  

**Goal:** Pull out the high‑level numbers the beat book will quote: most‑mentioned people, top towns, common topics, date range, etc.

**Tool:** `beatbook_generator.py` (the “metadata” part runs automatically).  

**Command (just to see the analysis, no final beat book yet):**

```bash
python beatbook_generator.py \
  stories_with_entities.json \
  --batch-size 30 \
  --debug                 # saves each batch’s raw LLM summary for you to peek at
```

The script does two things:

1. **Batch summarisation** – sends groups of 30 stories to the LLM with a prompt like:  

   ```
   From these 30 public‑safety stories, extract:
   1. Themes (law‑enforcement, fire‑EMS, etc.)
   2. Geographic patterns
   3. Key people & organisations
   4. Significant incidents
   ```

2. **Metadata aggregation** – counts how often each person, place, or organisation appears, and records the earliest & latest story dates.

**Result:** a Python dictionary (printed to the console) such as:

```json
{
  "total_stories": 312,
  "date_range": ["2024‑01‑02","2024‑10‑03"],
  "topics": [["Public Safety",212],["Health",45]],
  "top_people": [["Chief John Smith",34],["Mayor Carol Westfall",27]],
  "top_places": [["Easton, Maryland",98],["St. Michaels, Maryland",62]],
  "top_orgs":   [["Easton Police Department",78],["Talbot County Fire Service",55]]
}
```

**Tip:** If you only want the raw numbers (no LLM summarisation), you can skip the LLM step and use a tiny script that just counts the arrays. Example (run in a terminal with `jq`):

```bash
jq -r '
  .[] |
  (.people[]? // empty) as $p |
  ($p|sub(",.*";"")) as $name |
  {name:$name} |
  .name' stories_with_entities.json |
  sort | uniq -c | sort -nr | head -20
```

---

### 3.5. Generate the Beat Book  

Now the heavy lifting is done: we have a clean, enriched JSON. The final step is to ask the LLM to **write** the beat book in a reporter‑friendly tone.

**Command (the full pipeline):**

```bash
python beatbook_generator.py \
  stories_with_entities.json \
  -o Talbot_Public_Safety_Beatbook.md \
  -b 30 \
  -m anthropic/claude-sonnet-4-5 \
  --topic "Public Safety – Talbot County, MD"
```

**What happens under the hood**

1. **Select representative stories** – the script asks the LLM to pick 4‑6 diverse examples (breaking news, feature, profile, investigative).  
2. **Identify follow‑up angles** – another LLM prompt scans the newest 50 stories for unresolved investigations, policy changes, community concerns.  
3. **Consolidate batch summaries** – if you have many batches, the script hierarchically merges them so the final prompt stays under token limits.  
4. **Final prompt** – a long, structured request that includes:
   * The metadata you saw in step 4 (top people, places, orgs, date range).  
   * Demographic context (population, median age, etc.) – you can copy‑paste the “TALBOT COUNTY DEMOGRAPHIC CONTEXT” block from the script.  
   * Instructions for tone and sections (intro, “What you’re covering,” “Geographic notes,” “Who’s who,” “Organizations to know,” story examples, follow‑ups).  

**Result:** `Talbot_Public_Safety_Beatbook.md` – a markdown file you can hand to anyone. Example snippet:

```markdown
# Beat Book: Public Safety – Talbot County, MD  

Welcome to the Public Safety beat! Talbot County’s mix of historic waterfront towns and rural stretches means emergency responders are on call for everything from boat‑rescues on the Chesapeake to farm‑fire incidents…

## What You’re Covering  
- Law‑enforcement investigations and court outcomes  
- Fire & EMS response patterns  
- County‑level policy changes (e.g., new building‑code ordinances)  

## Geographic Notes  
- Easton (pop ≈ 16,800) sees 45 % of all police calls.  
- St. Michaels and Oxford generate the highest proportion of fire‑department activations per capita.  

## Who’s Who (Top contacts)  
- **Chief John Smith** – Easton Police Department (34 mentions)  
- **Mayor Carol Westfall** – Easton (27 mentions)  
…

## Story Examples  
### Breaking News: “Firefighters rescue family from flooded home” (2024‑10‑03)  
*Why it’s a good example:* Shows rapid inter‑agency response, includes multiple agencies…

## Potential Follow‑Ups  
1. **“Investigation into the 2024 Easton drug bust”** – angle: court‑case outcome; why: story left open in Oct 2024…
```

---

### 3.6. Fact‑Check & Refine  

Even the smartest LLM can hallucinate or mis‑interpret a name. Do a quick sanity check:

| What to verify | How |
|----------------|-----|
| **People names** | Search the newsroom’s contact list or Google the name. If the LLM produced “John Smith” × 30 but you only have one “John Smith,” confirm it’s the same person. |
| **Places** | Open a map (Google Maps) and confirm city‑state combos. |
| **Organisations** | Check the official website or your internal directory. |
| **Follow‑up angles** | Run a fresh search on your CMS for the suggested story title to see if it’s already been covered. |

**Quick command to spot outliers** (run from the folder with the enriched JSON):

```bash
jq '.[] | .people[]?' stories_with_entities.json |
  sort | uniq -c | sort -nr | head -10
```

If you see a name with an absurd count (e.g., “John Doe” 120 times), that’s a red flag – the model probably inserted a placeholder. Edit the beat book manually or re‑run the extraction with a tighter prompt.

---

## 4. Non‑Technical Walk‑Through (What the Commands Actually Do)  

| Step | Command | What it *actually* runs |
|------|---------|--------------------------|
| 1️⃣ Gather stories | `cp ~/Downloads/star_democrat_2024.json public_safety_stories.json` | Just copies a file – no code. |
| 2️⃣ Classify topics | `python classify_topics.py …` | A small Python script reads the JSON, builds a short text prompt for each story, sends it to the `llm` CLI, and writes a new JSON with a `topic` field. |
| 3️⃣ Extract entities | `python add_entities_clay.py …` | The script builds ONE big prompt that contains *all* selected stories, asks the LLM to return a **single** JSON array with three fields per story, then saves the result. |
| 4️⃣ Analyse metadata | `python beatbook_generator.py …` (first pass) | Splits the enriched JSON into batches (default 30), asks the LLM to summarise each batch, and aggregates counts with Python’s `Counter`. |
| 5️⃣ Generate beat book | `python beatbook_generator.py …` (full run) | Takes the batch summaries and metadata, asks the LLM to write a polished markdown guide, then writes `Beatbook.md`. |
| 6️⃣ Fact‑check | `jq …` or manual search | Simple command‑line filters to spot odd entries; otherwise you open the markdown and edit. |

**You never have to write Python** – you just run the supplied scripts with the arguments shown.

---

## 5. Practical Examples from the Scripts  

### 5.1. Prompt for Entity Extraction (batch version)

```text
Extract ALL named entities from this PUBLIC SAFETY news story and return them in JSON format.

people: Array of ALL people mentioned ... (include rank, agency, etc.)
places: Array of ALL geographic locations ... (city, county, road)
organizations: Array of ALL orgs ... (law‑enforcement, fire, courts)

Story Title: <title>
Story Content: <full article>

Return only valid JSON with the three arrays.
```

**What makes it work**  

* **All‑caps “VERY IMPORTANT”** – tells the LLM to obey the format strictly.  
* **No extra text** – the script strips any stray markdown fences (` ``` `) before parsing.  

### 5.2. Prompt for Beat‑Book Generation (final step)

```text
You're helping onboard a new reporter covering public safety in Talbot County, Maryland. Write a practical, business‑casual beat book.

DATASET INFO:
- 312 stories from Star Democrat
- Date range: 2024‑01‑02 to 2024‑10‑03
- Top topics: Public Safety (212), Health (45), …

KEY PEOPLE (most frequently mentioned):
- Chief John Smith (34 mentions)
- Mayor Carol Westfall (27 mentions)
…

[...additional metadata...]

INSTRUCTIONS:
1. Write a short intro (2‑3 paragraphs).
2. Brief “What You’re Covering” section.
3. Concise “Geographic Notes”.
4. “Who’s Who” (key contacts).
5. “Organizations to Know”.
6. Keep it conversational, like briefing a colleague over coffee.

COVERAGE SUMMARIES:
<concatenated batch summaries>

REPORTER'S BEAT BOOK:
```

The LLM returns a clean markdown document that the script writes to `beatbook.md`.

---

## 6. Tips & Best Practices  

| Area | Recommendation | Why |
|------|----------------|-----|
| **Model choice** | Start with **Claude Sonnet 4.5** (or GPT‑4‑Turbo) for reliable JSON output. | These models respect “return ONLY JSON” instructions better than older, more creative models. |
| **Prompt clarity** | Use **ALL CAPS** for “VERY IMPORTANT” lines, list explicit format (e.g., `"people": []`). | Reduces hallucinations and stray explanations. |
| **Batch size** | 30‑50 stories per LLM call is a safe sweet spot. Larger batches risk hitting token limits; smaller batches increase API cost. |
| **Rate‑limit handling** | The scripts already retry on “over capacity” messages, but you can add a `--delay 1.5` flag to slow calls if you see many “429” errors. |
| **Incremental saving** | Both `add_entities_clay.py` and the public‑safety script write the output after each story. If the process crashes, you can resume without losing work. |
| **Testing** | Run each script on **15‑20** stories first (`--limit 15`). Inspect the JSON output before scaling up. |
| **Version control** | Keep the raw input JSON and each intermediate file (e.g., `stories_with_entities.json`) in a Git repo. It lets you roll back if a model change breaks the format. |
| **Human review** | Allocate **30‑45 minutes** after the beat book is generated to scan for: <br>• Placeholder names (“Jane Doe”) <br>• Misspelled organisations <br>• Out‑of‑date follow‑up suggestions. |
| **Reuse** | Save the final markdown as a template (`beatbook_template.md`). For a new beat, just replace the metadata block and re‑run steps 1‑5. |

---

## 7. Common Challenges & How to Solve Them  

| Problem | What you’ll see | Fix |
|---------|----------------|-----|
| **LLM returns extra text (explanations, markdown fences)** | Output starts with “Here’s the JSON you asked for:” or wrapped in ```` ```json ````. | The scripts strip fences automatically, but you can add `| tail -n +2` or edit the prompt to say “Return ONLY the JSON array and NOTHING ELSE”. |
| **JSON parsing error** | Script throws `json.JSONDecodeError`. | Check the raw `.out.txt` log in the `logs/` folder. Look for stray commas or missing brackets. If the issue is systematic, tighten the prompt: “Return EXACTLY one JSON ARRAY.” |
| **Rate‑limit / “over capacity”** | Script pauses, then fails after several retries. | Add a larger delay (`--delay 2`) or switch to a higher‑quota model/provider. |
| **Missing fields (people, places, orgs empty)** | Some stories have `[]` for everything. | Verify the story actually contains relevant entities. If it’s a short notice (e.g., a calendar entry), the script correctly returns empty arrays – you can filter them out later with `jq`. |
| **Wrong beat selected** | Many stories end up labelled “Other”. | The classification prompt may be too vague. Add a few example titles to the prompt (modify `classify_topics.py` → `build_prompt`) so the model learns the nuance of “Public Safety”. |
| **Duplicate names with slightly different spellings** | “John Smith” vs “John A. Smith”. | After extraction, run a simple fuzzy‑match script (e.g., `python -m pip install fuzzywuzzy`) to merge near‑duplicates before counting. |
| **Follow‑up angles already covered** | The beat book suggests a “potential follow‑up” that was published last week. | Always cross‑check with your CMS search before assigning a reporter. The script’s disclaimer (“dataset may be outdated”) is a reminder to do this. |

---

## 8. Quick Checklist (Copy‑Paste for Your Desk)  

```
[ ] 1️⃣ Gather raw stories → JSON (title, content, date)
[ ] 2️⃣ Run classification
    uv run python classify_topics.py --model anthropic/claude-sonnet-4-5
    jq '[ .[] | select(.topic=="Public Safety") ]' > public_safety_stories.json
[ ] 3️⃣ Extract entities (batch)
    python add_entities_clay.py \
      --model groq/meta-llama/llama-4-maverick-17b-128e-instruct \
      --input public_safety_stories.json \
      --output stories_with_entities.json
[ ] 4️⃣ Verify a handful of JSON entries (jq, or open file)
[ ] 5️⃣ Run beat‑book generator (full)
    python beatbook_generator.py \
      stories_with_entities.json \
      -o Talbot_Public_Safety_Beatbook.md \
      -b 30 \
      -m anthropic/claude-sonnet-4-5 \
      --topic "Public Safety – Talbot County, MD"
[ ] 6️⃣ Open the .md file, skim for placeholders or odd names
[ ] 7️⃣ Run quick jq checks for outliers
    jq '.[] | .people[]?' stories_with_entities.json | sort | uniq -c | sort -nr | head -10
[ ] 8️⃣ Publish / share the beat book with the team
```

---

## 9. Final Thoughts  

You now have a repeatable, **no‑coding** pipeline that turns a raw dump of news articles into a polished beat book:

* **Collect** → **Classify** → **Enrich** → **Summarise** → **Write** → **Fact‑check**  

Because each stage is a thin wrapper around an LLM prompt, you can swap in a different model, adjust the prompt language, or add new metadata (e.g., sentiment scores) without touching any code.  

Give it a try on a small slice of your archive, refine the prompts as needed, and soon you’ll have a “cheat sheet” for any beat in your newsroom – ready to hand to a new reporter over a cup of coffee.  

Happy reporting! 🚀  


---

## Part 2 – From Stories to a Polished Beat Book  
*The “how‑to” that picks up where Part 1 left off.  If you’ve already read the introduction, you can jump straight to the sections that matter most to you.*

---

### 1️⃣  Getting the Raw Material Ready  

| Goal | What you actually do | Why it matters |
|------|----------------------|----------------|
| **Collect every story that belongs to your beat** | • Grab the newsroom’s JSON export (or a CSV you can turn into JSON). <br>• Keep the file in a folder you’ll use for the whole workflow, e.g. `~/beat‑project/talbot/`. | The LLM can only work with what you give it.  A single, well‑structured file means you never lose a story and you can re‑run the whole process later. |
| **Make sure each record has at least a headline and the full text** | If you only have a short “summary”, add a `content` field that contains the summary – the extraction scripts will fall back to it. | The entity‑extraction prompts ask the model to read the **full article**; missing text leads to empty “people/places/orgs” arrays. |
| **Give each story a unique ID** (optional but handy) | Add a `story_number` or `id` field.  The scripts will copy it straight through to the output. | When you later spot a problem you can quickly locate the original story in your CMS. |

**Command‑line cheat sheet**  

```bash
# 1️⃣  Move into the project folder
cd ~/beat-project/talbot

# 2️⃣  Verify you have a JSON array called “stories.json”
ls -l stories.json
# (If you have a CSV, convert it first – see the “CSV → JSON” tip in the appendix)
```

---

### 2️⃣  Pulling Out People, Places & Organizations  

We already built a reusable script (`stardem_entities_add_entities.py`) that talks to the LLM and returns three clean arrays for every story.

#### 2.1  What the script does (plain English)

1. **Builds a strict prompt** – tells the model: “Give me ONLY a JSON object with keys `people`, `places`, `organizations`.”
2. **Runs the LLM via the `llm` CLI** – the same tool you use for ad‑hoc queries.
3. **Cleans the output** – strips code fences, grabs the *last* JSON block, validates the structure.
4. **Writes a tiny JSON file** (`stories_with_entities.json`) that looks like this:

```json
[
  {
    "story_number": 1,
    "headline": "Sheriff’s Office investigates downtown fire",
    "people": ["Sheriff Joe Gamble"],
    "places": ["Easton", "Main Street"],
    "organizations": ["Talbot County Sheriff’s Office"]
  },
  …
]
```

#### 2.2  Running it – step by step

```bash
# Install the helper if you haven’t already (once per machine)
pip install llm   # or “uv pip install llm” if you prefer uv

# Run the extractor (replace the model if you want something else)
uv run python stardem_entities_add_entities.py \
    --model groq/meta-llama/llama-4-maverick-17b-128e-instruct \
    --input stories.json \
    --output stories_with_entities.json
```

**What each flag means**

| Flag | Meaning |
|------|---------|
| `--model` | The exact model name the `llm` CLI should use.  The default in the repo is a solid, affordable 17‑B Llama‑4. |
| `--input` | Path to your raw story file. |
| `--output` | Where the cleaned‑up JSON will land.  Keep the name handy – you’ll feed it to later scripts. |
| `--timeout` (optional) | How long to wait for the LLM before giving up on a single story (default = 60 s). |
| `--help` | Prints the usage text – always good to glance at it. |

> **Tip:** The script writes a tiny log file for every story (`logs/story_0001.out.txt`, `logs/story_0001.err.txt`).  If a story repeatedly fails, open the `.out.txt` to see the raw LLM answer and decide whether you need a longer timeout or a different model.

---

### 3️⃣  Classifying Every Story by Topic  

A beat‑book works best when you can quickly scan “all the police‑related pieces” or “the handful of education stories”.  The `stardem_topics_classify_topics.py` script does exactly that.

#### 3.1  How it works (non‑technical)

1. **Creates a short prompt** that lists a fixed set of topics (e.g., *Education, Health, Police & Crime, …*).  
2. **Feeds each story’s headline + first 600 characters** to the LLM.  
3. **Parses the answer** and forces it into one of the canonical topic names.  
4. **Adds a new field `topic`** to each story record.

#### 3.2  Running it

```bash
uv run python stardem_topics_classify_topics.py \
    --model anthropic/claude-sonnet-4-5 \
    --dry-run   # remove this flag once you’re ready for real classifications
```

- **First pass with `--dry-run`**: you’ll see the script assign “Other” to everything – a quick sanity check that the JSON is being read correctly.  
- **Second pass (real run)**: drop `--dry-run`.  The script will pause `0.6 s` between calls (adjust with `--delay` if you hit rate limits).  

**Result** – a new file `stardem_topics_classified.json` that looks like:

```json
{
  "title": "Talbot County deputies respond to late‑night fire",
  "content": "...",
  "topic": "Public Safety"
}
```

> **Pitfall alert:** If you see a lot of “Other” after the real run, double‑check the **TOPICS** list at the top of the script – make sure it contains the category you actually need (e.g., “Public Safety”).  You can edit the list and re‑run.

---

### 4️⃣  Turning Metadata into Insight (the “analytics” layer)  

Both beat‑book generators (`stardem_draft_beatbook_generator.py` and the newer `stardem_nearly_final_beatbook_generator.py`) start by **summarizing the metadata**: most‑frequent people, places, organizations, and topics.

You *don’t* have to write any Python – the scripts do it for you.  What you need to understand is **what the output looks like** so you can verify it before you hand it to the LLM.

#### 4.1  The key numbers you’ll see

| Metric | Where it appears in the final beat book |
|--------|----------------------------------------|
| `total_stories` | Intro paragraph (“We looked at  … stories”). |
| Top 5 topics | Quick‑scan “What we covered”. |
| Top 15 people | “Who’s Who” list. |
| Top 12 places | “Geographic notes”. |
| Top 12 organizations | “Orgs to know”. |
| Date range | Gives you a sense of how current the data is. |

#### 4.2  Quick sanity‑check

After you have run the entity extractor **and** the topic classifier, run the draft generator **in “summaries‑only” mode** to see the raw batch‑summaries without the final narrative:

```bash
uv run python stardem_draft_beatbook_generator.py \
    stories_with_entities.json \
    -b 30 \
    --summaries-only \
    -o batch_summaries.md
```

Open `batch_summaries.md` and skim:

- Do you see *real* story details (names, towns) or just generic filler?  
- Are there any glaring gaps (e.g., “no people listed for a police story”)?

If something looks off, you probably need to re‑run the entity extraction with a **larger timeout** (`--timeout 120`) or a **different model** (e.g., `groq/openai/gpt-4o-mini` for speed, `anthropic/claude-3‑sonnet-20240229` for accuracy).

---

### 5️⃣  Generating the Beat Book – the “final pass”  

The final script (`stardem_nearly_final_beatbook_generator.py`) stitches everything together:

1. **Analyzes metadata** (people, places, orgs, topics).  
2. **Splits the story collection into batches** (default = 30).  
3. **Calls the LLM for a short coverage summary of each batch** (the “batch‑summaries”).  
4. **Optionally collapses those batch‑summaries hierarchically** if you have many batches.  
5. **Feeds the consolidated text plus the metadata into a big prompt** that tells the model: *“Write a coffee‑chat‑style beat book for a new reporter.”*  
6. **Adds two extra sections** – curated story examples and potential follow‑up angles.  

#### 5.1  Running the full generator  

```bash
uv run python stardem_nearly_final_beatbook_generator.py \
    stories_with_entities.json \
    -b 30 \
    -m groq/openai/gpt-4o-mini \
    -t "Talbot County Public Safety" \
    -o talbot_beatbook.md
```

| Flag | What you’re controlling |
|------|--------------------------|
| `-b` | Batch size – smaller batches = cheaper token usage, but more LLM calls.  30 works well for a few hundred stories. |
| `-m` | Model – pick a model that balances cost and quality for you.  `gpt‑4o‑mini` is fast and cheap; `claude‑3‑opus` is more thorough. |
| `-t` | The *topic* that appears in the title of the beat book (`Talbot County Public Safety`). |
| `-o` | Output file.  Keep the `.md` extension – the result is a ready‑to‑publish markdown file. |
| `--debug` | (Optional) writes each batch summary to `debug_batch_001.md` … `debug_batch_XXX.md`.  Useful when you need to trim a runaway token count. |

#### 5.2  What you’ll get (sample excerpt)

```markdown
# Beat Book: Talbot County Public Safety

**INTRO**  
Welcome to Talbot County’s public‑safety beat.  You’ll be covering everything from the sheriff’s office … (2‑3 short paragraphs)

**WHAT YOU’RE COVERING**  
The data show a steady stream of ... (3‑4 narrative paragraphs)

**GEOGRAPHIC NOTES**  
Easton sees the bulk of law‑enforcement activity, while the smaller waterfront towns … (2‑3 concise paragraphs)

**WHO’S WHO**  
You’ll hear a lot from Sheriff **Joe Gamble** (Sheriff, Talbot County) … (short intro + bullet‑style list)

**ORGANIZATIONS TO KNOW**  
- Talbot County Sheriff’s Office – primary law‑enforcement agency …  
- Easton Police Department – handles city‑level incidents …

## Story Examples
### Breaking News: “Sheriff’s Office investigates downtown fire”  
*June 12 2024* – … (why it’s a good example)

## Potential Follow‑Ups
1. **Complete Streets Study** – … (angle, why it matters)
```

> **Why this matters:** The LLM does the heavy lifting (writing narrative, weaving demographics, picking examples).  All you need to do afterward is **read, edit for any factual slip, and add any new contacts** that the model couldn’t know.

---

### 6️⃣  Fact‑Checking & Polishing  

Even the best LLM can hallucinate a phone number or attribute a quote to the wrong person.  A quick 3‑step review saves you embarrassment.

| Step | What to do | Tools & Tips |
|------|------------|--------------|
| **1️⃣ Verify the metadata** | Cross‑check the top‑people list with your newsroom’s contact database. | Search your internal “people” spreadsheet for “Joe Gamble” → confirm title and phone. |
| **2️⃣ Spot‑check the examples** | Open the original story (via the headline) and confirm the LLM’s description is accurate. | Use the story’s `story_number` in the JSON to pull up the full text in your CMS. |
| **3️⃣ Confirm follow‑up angles** | For each “Potential Follow‑Up” see whether the underlying story is still open (e.g., a 2022 investigation may already be resolved). | Google the story title + “2024 update” or ask a beats‑editor. |

**Quick command to pull a single story by number**

```bash
jq '.[] | select(.story_number == 42)' stories_with_entities.json
```

*(If you don’t have `jq`, just open the JSON in a code editor and search for `"story_number": 42`.)*

---

### 7️⃣  Practical Prompt Samples  

Below are the exact prompts the scripts feed to the LLM.  Knowing them helps you tweak the tone or add a new requirement.

#### 7.1  Entity‑Extraction Prompt (single story)

```
Extract the entities mentioned in this news story. VERY IMPORTANT:

- Do NOT ask for more input. Use ONLY the provided Headline and Article Text (or Summary if no full text is present). 
- Return EXACTLY one JSON object and NOTHING ELSE.
- Keys must appear in this order: "people", "places", "organizations".
- Each value = array of strings, no titles or honorifics.

Headline: {title}
Article Text: {fulltext}
```

*Key take‑away*: The “exactly one JSON object” instruction forces the model to stay on‑topic and makes downstream parsing reliable.

#### 7.2  Topic‑Classification Prompt (single story)

```
Assign this news story to EXACTLY ONE topic from the following list:
Education, Health, Police & Crime, Local government, Judiciary, Public Safety, Election, Chesapeake, Food, Community Events & Culture, Movies & Shows, Sports, Religion, Obituaries, Other

Title: {title}
Content (short): {first‑600‑chars}
```

*Key take‑away*: We ask for **ONE** topic only; the helper function `choose_topic_from_response` normalizes any extra punctuation.

#### 7.3  Batch‑Summary Prompt (30 stories)

```
You are analyzing news coverage to help onboard a new reporter. Your focus should be on public safety stories from Talbot County, Maryland.

From these {len(stories)} news stories, extract:
1. Public safety themes and patterns…
2. Geographic patterns…
3. Key people…
4. Important organizations…
5. Significant incidents…
6. Recurring issues…

Stories:
{json.dumps(stories, indent=2)}

Provide a structured summary:
```

*Key take‑away*: Because we give the whole batch as JSON, the LLM can see cross‑story patterns (e.g., “multiple fire‑department calls in Oxford”).

#### 7.4  Final Beat‑Book Prompt (after consolidation)

```
You're helping onboard a new reporter covering public safety in Talbot County, Maryland. Write a practical, narrative‑driven beat book that reads like a story, not a reference document.

DATASET INFO:
- {total_stories} stories …
- Top topics: …
- KEY PEOPLE: …
- KEY PLACES: …
- KEY ORGANIZATIONS: …

[TALBOT COUNTY DEMOGRAPHIC CONTEXT – paste verbatim]

INSTRUCTIONS:
1. Write a SHORT, friendly introduction (2‑3 paragraphs).
2. Brief "What You're Covering" (3‑4 paragraphs).
3. CONCISE "Geographic Notes".
4. "Who's Who" (narrative intro + short list).
5. "Organizations to Know" (same format).

COVERAGE SUMMARIES:
{combined batch summaries}
```

*Key take‑away*: The prompt tells the model **exactly** where to insert the demographic paragraph and the meta‑data lists, ensuring those never get omitted.

---

### 8️⃣  Tips & Best Practices  

| Situation | What to do | Why it helps |
|-----------|------------|--------------|
| **Running out of tokens** (LLM says “exceeded max tokens”) | Reduce the batch size (`-b 20`), or enable the hierarchical consolidation (`max_summaries_per_level=5`). | Fewer words per request = smaller token footprint. |
| **Entity list contains duplicates** | After extraction, run a quick Python one‑liner to dedupe: <br>`python -c "import json; d=json.load(open('stories_with_entities.json')); print(json.dumps([{'people':list(set(s['people']))} for s in d], indent=2))"` | LLM sometimes repeats a name when it appears twice in the same story. |
| **Model keeps hallucinating “John Doe (Mayor)” when the article only mentions “Mayor John Doe”** | Add the `--model` flag pointing to a *stronger* model (Claude‑3‑opus or GPT‑4‑turbo) **or** tighten the prompt by appending `“Do not invent titles; only return the plain name.”` | Higher‑capacity models better follow fine‑grained instructions. |
| **You need to add a new topic (e.g., “Climate”)** | Edit the `TOPICS` list in `stardem_topics_classify_topics.py` and re‑run the classifier. | The script only knows what you give it; any missing category ends up as “Other”. |
| **You want a quick “who‑appears‑most‑often” table** | Use the `analyze_metadata` function’s output: it already returns `top_people`, `top_places`, `top_orgs`.  Print it with a one‑liner: <br>`python -c "import json, sys; m=json.load(open('stories_with_entities.json')); from collections import Counter; c=Counter(p for s in m for p in s['people']); print(c.most_common(10))"` | No need to write a separate script – the same logic lives in the beat‑book generator. |
| **You need to share the beat book with non‑technical teammates** | Convert the markdown to PDF (pandoc) or to an HTML page (GitHub Pages).  Example: <br>`pandoc talbot_beatbook.md -o talbot_beatbook.pdf` | PDFs are universally viewable; HTML lets you add a clickable table of contents. |

---

### 9️⃣  Common Challenges & How We Solved Them  

| Problem | How we fixed it | Residual risk |
|---------|----------------|---------------|
| **LLM returns extra text before the JSON** (e.g., “Sure, here you go: …”) | The extraction script now scans for the *last* balanced `{ … }` block (`_extract_last_json`). | Occasionally the model emits two JSON blobs; the script still grabs the final one, which is usually the correct one. |
| **Rate‑limit errors (“429 Too Many Requests”)** | Built‑in exponential back‑off with a ceiling of 5 minutes. Also added `--delay` flag to the topic classifier. | If you run a massive dataset (10 k stories) you may need to spread the job over several hours. |
| **Inconsistent place names (“Easton” vs “Easton, MD”)** | Normalization step strips punctuation and trailing state abbreviations. | Still possible to have synonyms (e.g., “St. Michaels” vs “Saint Michaels”). Manual cleanup may be required for the final list. |
| **Missing demographic context in the final beat book** | The final prompt explicitly copies the whole demographic block into the LLM prompt. | If you edit the block later, you must re‑run the generator – the beat book does not auto‑pull from a separate file. |
| **Story‑example selection returns an empty JSON** (LLM confused) | Added a fallback that simply picks the first 4–6 stories and labels them “representative”. | The fallback examples may be less diverse; you can edit the “Story Examples” section manually after generation. |

---

### 10️⃣  When Human Judgment Beats the Machine  

| Area | What the LLM can do | Where you still need a human eye |
|------|---------------------|---------------------------------|
| **Entity extraction** | Pulls out names, places, orgs with ~90 % precision on clean text. | Verify spelling, resolve ambiguous names (“Smith” could be a person *or* a street). |
| **Topic classification** | Assigns a broad category. | Detect nuanced sub‑topics (e.g., “police‑body‑camera policy” might belong to both “Police & Crime” *and* “Local government”). |
| **Narrative writing** | Generates smooth, readable prose. | Add local color, quotes, and any embargoed information you already know. |
| **Follow‑up angles** | Suggests logical next steps based on the dataset. | Confirm that the angle is still “open” – a story from 2020 may already be closed. |

**Bottom line:**  Think of the LLM as a *drafting partner*.  The final beat book should always get a quick read‑through from a seasoned reporter or beats editor.

---

### 📚  Quick Reference Cheat Sheet  

| Action | Command (copy‑paste) |
|--------|----------------------|
| Convert CSV → JSON (one‑liner) | `python -c "import pandas as pd, json, sys; df=pd.read_csv('stories.csv'); json.dump(df.to_dict(orient='records'), open('stories.json','w'), indent=2)"` |
| Extract entities | `uv run python stardem_entities_add_entities.py --input stories.json --output stories_with_entities.json` |
| Classify topics (dry run) | `uv run python stardem_topics_classify_topics.py --dry-run` |
| Classify topics (real) | `uv run python stardem_topics_classify_topics.py --model anthropic/claude-sonnet-4-5` |
| Generate *only* batch summaries | `uv run python stardem_draft_beatbook_generator.py stories_with_entities.json -b 30 --summaries-only -o batch_summaries.md` |
| Generate final beat book | `uv run python stardem_nearly_final_beatbook_generator.py stories_with_entities.json -b 30 -m groq/openai/gpt-4o-mini -t "Talbot County Public Safety" -o talbot_beatbook.md` |
| Convert to PDF | `pandoc talbot_beatbook.md -o talbot_beatbook.pdf` |
| Spot‑check a story by ID | `jq '.[] | select(.story_number == 27)' stories_with_entities.json` |

---

### 🎉  What’s Next?  

- **Version 3** (Part 3 of 6) will show you how to **store the output in a shared newsroom drive, add version control, and automate the whole pipeline with a simple shell script**.  
- **Version 4** will dive into **visualising the beat book** (mind‑maps, interactive dashboards).  
- **Version 5** will cover **collaborative editing** (Google Docs, GitHub‑based markdown review).  
- **Version 6** will look at **ongoing maintenance** – how to keep the beat book fresh month after month.

Stay tuned, and happy beat‑building!  



--- 

**Appendix – Helpful One‑liners**

```bash
# Count how many stories mention a given person (e.g., "Joe Gamble")
jq '[.[] | select(.people[]? == "Joe Gamble")] | length' stories_with_entities.json
```

```bash
# List the top 10 most‑mentioned organizations
python - <<'PY'
import json, collections, sys
data=json.load(open('stories_with_entities.json'))
cnt=collections.Counter(o for s in data for o in s.get('organizations',[]))
for org, n in cnt.most_common(10):
    print(f"{org}: {n}")
PY
```

Feel free to copy these into a terminal; they’re safe, require only the `jq` utility (or Python) and give you instant insight.  


---

## Part 3 – From Raw Stories to a Structured Beat‑Book  
*(Continuing the “How‑to‑Create a Beat Book with AI & Data‑Journalism” series)*  

> *“If you can turn a spreadsheet into a narrative that a new reporter can skim in five minutes, you’ve already done the hard part.”* – Senior reporter, 2025  

Below we walk you through the **middle‑section** of the workflow – the bits that turn the articles you’ve collected into clean, searchable data and then into a polished beat‑book.  The steps are written for a newsroom that may have no Python experience; every command is a one‑liner you can paste into a terminal, and every concept is explained in plain English.  

---

### 1️⃣  Pulling Out the Who, What, When & Where (Entity & Metadata Extraction)

| Why it matters | What you’ll get | Quick‑look at the command |
|----------------|----------------|---------------------------|
| A beat‑book is *about* people, places and organisations.  Extracting them lets you see who shows up most often, which towns generate the most stories, and where the gaps are. | A JSON file that, for each story, lists **people**, **places**, **organisations**, **event types**, and a **short description**. | `uv run llm --model groq/openai/gpt-oss-120b --input public_safety_stories.json --output stories_with_entities_v1.json` |

#### 1.1 What the script actually does (no‑code version)

1. **Reads** every story in `public_safety_stories.json` (the file you created in Part 2).  
2. **Sends** the story text to a Large Language Model (LLM) with a *prompt* that asks the model to list the entities it sees.  
3. **Writes** the original story object **plus** a new field called `entities` that holds the extracted lists.  
4. **Saves** the result *as it goes* so you can stop the run at any time without losing work.  

#### 1.2 The prompt that makes the model behave (the secret sauce)

> *“Extract the names of people, organisations and places mentioned in the article.  Return a JSON object with four arrays: `people`, `organisations`, `places`, `events`.  If the story has no Eastern‑Shore focus, return the single word **SKIPPED** instead of any lists.”*  

The **SKIPPED** tag is the trick that saved the team hours (see the *Stardem_choice* notes).  Without it the model would return empty arrays for irrelevant stories, and you’d have to filter them later.

#### 1.3 What a good output looks like (real example)

```json
{
  "id": "2024-07-15-001",
  "headline": "Helene storm forces Oxford volunteers to ship gear to Tennessee",
  "date": "2024‑07‑15",
  "source": "Star Democrat",
  "text": "... (full article) ...",
  "entities": {
    "people": ["Chief Graham Norbury", "Chief Tim Kearns"],
    "organisations": ["Oxford Volunteer Fire Company", "Tennessee Emergency Management Agency"],
    "places": ["Oxford, MD", "Tennessee"],
    "events": ["Helene storm response"]
  }
}
```

If the article were about a concert in London, the output would simply be:

```json
{
  "id": "2025-01-12-054",
  "headline": "London‑based band plays at Wembley",
  ...
  "entities": "SKIPPED"
}
```

---

### 2️⃣  Cleaning & Consolidating the Entity Data

You now have a pile of JSON objects – each with its own little list of names.  The next step is to **merge** those lists so you can see, for example, that *Konner Metz* appears in 17 stories, or that *Easton, MD* appears in 54 stories.

#### 2.1 One‑liner to flatten the data

```bash
uv run python tools/flatten_entities.py \
  --input stories_with_entities_v1.json \
  --output flat_entities.csv
```

What the script does:

| Input | Output |
|-------|--------|
| `stories_with_entities_v1.json` (one story per line) | `flat_entities.csv` – a spreadsheet with columns **story_id**, **entity_type**, **entity_name** |

Open the CSV in Excel or Google Sheets and you’ll get a view like:

| story_id | entity_type | entity_name |
|----------|------------|-------------|
| 2024‑07‑15‑001 | person | Chief Graham Norbury |
| 2024‑07‑15‑001 | place | Oxford, MD |
| 2024‑07‑15‑001 | organisation | Oxford Volunteer Fire Company |
| … | … | … |

#### 2.2 Pivot to see “prominence”

In the spreadsheet, use **Pivot Tables** (or the free *Data > Pivot Table* feature in Google Sheets):

| Row | Values |
|-----|--------|
| **entity_name** (filtered to *people* or *places*) | **Count of story_id** (how many stories each appears in) |

The result is exactly what you see in the *entity_report.md* file – a list of “Prominently Featured Individuals” (≥ 4 stories) and “Prominently Featured Locations”.  You can copy‑paste that table directly into the “Key Sources” section of your beat‑book.

**Tip:** When you first run the pivot, set the filter to *≥ 2* stories; then raise the threshold to *≥ 4* once you’re comfortable with the numbers.  This prevents you from missing emerging beats that haven’t yet hit the 4‑story mark.

---

### 3️⃣  Shaping the Raw Data into Beat‑Book Sections

Now that you have tidy tables of people, places, organisations and events, you can decide **how** to organize the final document.  The team that produced *talbot_beatbook_v6.md* used **three** high‑level sections:

1. **Thematic Issues** (e.g., “Burn‑Ban Enforcement”, “K‑9 Program Restoration”)  
2. **Geographic Analysis** (e.g., “Oxford”, “Greensboro”, “Rural Talbot”)  
3. **Story‑Idea Toolbox** (unresolved angles you can chase)

You can follow that structure, or you can keep a **tabular** format if your newsroom prefers quick reference.  Below is a *template* you can paste into a Markdown file; the placeholders (`{{ }}`) will be filled by the LLM in the next step.

```markdown
# {{BEAT_NAME}} Beat Book – {{DATE_RANGE}}

## Executive Summary
*One‑paragraph overview of the beat’s size, key themes, and why it matters.*

## 1. Thematic Issues
| Theme | Representative Stories (headline + date) | Key Contacts |
|-------|------------------------------------------|--------------|
| Burn‑Ban Enforcement | “County extends burn‑ban to Aug 15 – 2024‑06‑30” | Chief Graham Norbury (Oxford) |
| K‑9 Program Restoration | “Talbot seeks new K‑9 dogs – 2024‑11‑12” | Sheriff Joe Gamble (Talbot) |
| Protest‑Permit Debate | “No Kings protests spark ordinance talks – 2025‑06‑08” | Chief Alan Lowrey (Easton) |

## 2. Geographic Analysis
### Oxford, MD
- **Stories:** 12  
- **Top People:** Chief Graham Norbury (5), Mayor Cheryl Lewis (3)  
- **Key Issues:** Burn‑ban, traffic‑safety vs. historic preservation  

### Easton, MD
- **Stories:** 54  
- **Top People:** Chief Alan Lowrey (7), Director Brian LeCates (6)  
- **Key Issues:** Complete Streets, protest‑permit ordinance, AED network  

*(repeat for each town/county you cover)*

## 3. Story‑Idea Toolbox
| Angle | Why it matters | Starting sources |
|-------|----------------|-----------------|
| Vision‑Zero impact | Test $1.2 M grant outcomes | Engineer Rick Van Emburgh, EMS data |
| Burn‑ban human lens | Follow a farmer through the ban | Chief Norbury, local farmer |
| K‑9 program restoration | Follow grant‑application cycle | Sheriff Gamble, Maryland Police K‑9 Foundation |
| Ridgely MOU after‑effects | One‑year audit of cost‑share | Commissioner Brad Sears, Sheriff Donald Baker |

## 4. Source Directory (quick‑look)
| Name | Role | Organisation | Primary Stories |
|------|------|--------------|-----------------|
| Graham Norbury | Fire Chief | Oxford VFC | 2024‑07‑15, 2024‑09‑02 |
| Joe Gamble | Sheriff | Talbot County | 2024‑11‑12, 2025‑02‑03 |
| … | … | … | … |
```

---

### 4️⃣  Letting an LLM Fill the Gaps (Generating the Narrative)

#### 4.1 Why use an LLM at this stage?

* You already have the raw data (people, places, events).  
* The LLM can **summarise** each theme, **weave** the tables into prose, and **add** a conversational tone that makes the beat‑book readable for a new reporter.  

#### 4.2 The “beat‑book generator” prompt (tested on the Groq *gpt‑oss‑120b* model)

```text
You are a senior beat reporter writing a public‑safety beat book for the Eastern Shore (MD).  

Using the data supplied in the attached CSV (columns: story_id, entity_type, entity_name, count), produce a Markdown beat book with the following sections:

1. Executive Summary – 3‑4 sentences summarising the overall volume, geographic focus and any big trends.
2. Thematic Issues – for each theme (Burn‑Ban, K‑9, Protest‑Permit, etc.) write a 2‑sentence description, list up to three representative headlines (date + title) and name the top two contacts.
3. Geographic Analysis – for each town/county with ≥ 5 stories, write a short paragraph that mentions story count, top people, and the most common issue(s).
4. Story‑Idea Toolbox – give at least five unresolved angles, each with a one‑sentence why‑it‑matters and a suggested first source (person or organisation).
5. Source Directory – a compact table of the 10 most‑quoted people with their role and the stories they appear in.

Do NOT fabricate email addresses or phone numbers.  If a contact appears in fewer than two stories, omit the contact details.  Use bullet points where appropriate.  Keep the tone conversational but professional.

[Insert the CSV data here]
```

**How to run it (one‑liner):**

```bash
uv run llm --model groq/openai/gpt-oss-120b \
  --input flat_entities.csv \
  --prompt @beatbook_prompt.txt \
  --output talbot_beatbook_v7.md
```

*`@beatbook_prompt.txt`* is a plain‑text file that contains the prompt above.  The `--input` flag tells the script to pipe the CSV into the prompt (the script automatically formats it as a table inside the prompt).

#### 4.3 What a good LLM output looks like (excerpt)

> **Executive Summary**  
> The Talbot County public‑safety beat generated 225 stories between November 2023 and October 2025.  Fire‑service coverage dominates the narrative (54 % of stories), while the “Burn‑Ban” policy and the renewed “K‑9” program are the two most‑repeated thematic threads.

> **Thematic Issue – Burn‑Ban Enforcement**  
> Every summer Talbot County enforces a 30‑day burn‑ban to curb wildfire risk.  The ban repeatedly pits fire‑chief data (12 % fewer brush‑fires) against farmers’ concerns about delayed planting (see stories “County extends burn‑ban – 2024‑06‑30”, “Fire chief warns of drought risk – 2024‑07‑15”).

> **Geographic Analysis – Easton, MD**  
> With 54 stories, Easton is the beat’s epicentre.  Chief Alan Lowrey and Director Brian LeCates appear most often; the city’s “Complete Streets” workshops and the new protest‑permit ordinance dominate coverage.

> *(…rest of sections omitted for brevity…)*

Notice the **absence** of made‑up contact details – a problem the team ran into in earlier drafts (see *prototype_v1.md* notes).  By explicitly telling the model *“Do NOT fabricate email addresses”* you avoid that pitfall.

---

### 5️⃣  Fact‑Checking & Polishing the Beat‑Book

| Step | What to do | Tools you can use |
|------|------------|-------------------|
| **5.1 Verify counts** | Compare the story counts in the beat‑book (e.g., “Easton – 54 stories”) with the pivot table you built in the spreadsheet. | Spreadsheet filter, `=COUNTIF()` formulas |
| **5.2 Confirm names** | Spot‑check the top 5 individuals (e.g., Konner Metz, Joe Gamble) by opening the original articles and confirming the bylines. | Star‑Democrat archive search (keyword + name) |
| **5.3 Validate dates** | Ensure every headline you quote has the correct publication date. | Article metadata (usually at the top of the HTML) |
| **5.4 Clean up “SKIPPED” rows** | Remove any stray “SKIPPED” entries that accidentally made it into the CSV before running the LLM. | Simple find‑replace (`SKIPPED` → blank) |
| **5.5 Add links** (optional) | If your newsroom’s CMS supports hyperlinks, replace the headline text with a Markdown link to the story. | Copy URL from the archive, format `[Headline](url)` |

#### 5.6 Quick sanity‑check script (optional)

```bash
uv run python tools/validate_beatbook.py \
  --beatbook talbot_beatbook_v7.md \
  --source public_safety_stories.json
```

The script scans every headline in the beat‑book, looks it up in the source JSON, and flags any mismatches.  It’s a **nice safety net** if you have a large beat with dozens of entries.

---

### 6️⃣  Tips & Best Practices (Lessons Learned from the Project)

| Area | What worked | What didn’t | Recommendation |
|------|-------------|--------------|----------------|
| **Model choice** | `gpt‑oss‑120b` was the fastest and most consistent; it respected the “no‑fabrication” clause. | `llama‑4‑maverick‑17b` hit rate‑limits after ~150 stories, causing long pauses. | **Start with `gpt‑oss‑120b`**. If you need a cheaper model, test on a 10‑story sample first. |
| **Prompt design** | Adding the **SKIPPED** rule filtered out off‑beat stories dramatically. | Forgetting to specify “Do NOT fabricate emails” produced a whole page of bogus contact info (prototype v1). | **Always include** (a) a “skip” rule for irrelevant stories, and (b) a “no‑fabrication” clause. |
| **Saving progress** | The `uv run` wrapper automatically writes each story’s result to the output file, so you can `Ctrl‑C` anytime and resume later. | Earlier ad‑hoc scripts overwrote the file on each run, losing half the work. | **Never delete** the output file between runs; let the script handle resumption. |
| **Entity consistency** | Using the same model for *people* and *organisations* kept abbreviations uniform (e.g., “SMFD” → “St. Michael’s Volunteer Fire Department”). | Mixing models (v1 vs. v4) introduced inconsistent naming (sometimes “SMFD”, sometimes the full name). | **Run one model per project**; if you need to switch, re‑process the whole batch. |
| **Human review** | Spot‑checking the top 10 individuals caught a few author‑byline leaks (e.g., “Reporter (Star Democrat)” showing up as a person). | Relying 100 % on the LLM produced a few *duplicate* entries (same person listed under two slightly different spellings). | **Run a deduplication pass** (`tools/dedupe_entities.py`) and always glance at the top‑ranked rows. |
| **Story‑idea generation** | The “Story‑Idea Toolbox” table is a **gold mine** for new reporters; each angle already has a suggested source. | Leaving the table empty made the beat‑book feel static. | **Never skip** the toolbox – it turns the beat‑book from a reference into a story‑pipeline. |

---

### 7️⃣  Common Pitfalls & How to Fix Them

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| The beat‑book lists *fake* email addresses (e.g., `john.doe@fake.com`). | Prompt didn’t forbid fabrication. | Add “**Do NOT fabricate email addresses or phone numbers**” to the prompt and regenerate. |
| You see a handful of stories with **SKIPPED** still in the final beat‑book. | The LLM treated “SKIPPED” as a literal word and included it in a table. | Filter the CSV for rows where `entities == "SKIPPED"` before feeding it to the generator, or add a post‑process step to drop those rows. |
| Rate‑limit error after ~150 stories (error message: *“429 Too Many Requests”*). | The model’s API quota was exceeded. | Switch to a higher‑quota key, or break the run into batches of 100 stories (`--limit 100`). |
| Duplicate names with slightly different spelling (e.g., “Konner Metz” vs. “Konner Metz (Star Democrat)”). | The model copied the byline together with the name. | After flattening, run `tools/clean_names.py` which strips parentheses and standardises case. |
| The “Geographic Analysis” section lists a town that never appears in your source data. | You manually typed a placeholder while drafting. | Use the *auto‑generated* list from the pivot table – never hand‑type town names. |

---

### 8️⃣  When Human Judgment Beats the Algorithm

| Situation | Why a human touch is essential |
|-----------|---------------------------------|
| **Conflicting counts** – the spreadsheet says “Easton – 54 stories” but the beat‑book says “52”. | Numbers can drift if you edited the CSV after the LLM ran. Double‑check the source file before publishing. |
| **Sensitive stories** – homicide or child‑exploitation coverage. | Verify that you’re not exposing victim identities; consider adding a “red‑action” flag. |
| **Emerging beats** – a new issue (e.g., a sudden surge in drone‑related incidents) appears after you’ve generated the beat‑book. | Add an “Update” section or a quick note for the newsroom to revisit the beat in two weeks. |
| **Community feedback** – a local activist points out that a key stakeholder is missing from the source directory. | Insert the missing person manually; the beat‑book is a living document, not a static dump. |

---

### 9️⃣  Quick‑Start Checklist (Copy‑Paste Into Your Notepad)

```
[ ] 1. Gather source stories → public_safety_stories.json (Part 2)
[ ] 2. Run entity extraction
    uv run llm --model groq/openai/gpt-oss-120b \
      --input public_safety_stories.json \
      --output stories_with_entities_v1.json
[ ] 3. Flatten to CSV
    uv run python tools/flatten_entities.py \
      --input stories_with_entities_v1.json \
      --output flat_entities.csv
[ ] 4. Clean duplicates (optional)
    uv run python tools/dedupe_entities.py \
      --input flat_entities.csv \
      --output clean_entities.csv
[ ] 5. Build pivot tables → identify top people, places, themes
[ ] 6. Write / paste beat‑book prompt (see Section 4.2) into beatbook_prompt.txt
[ ] 7. Generate narrative beat‑book
    uv run llm --model groq/openai/gpt-oss-120b \
      --input clean_entities.csv \
      --prompt @beatbook_prompt.txt \
      --output talbot_beatbook_v7.md
[ ] 8. Fact‑check counts, names, dates (Spreadsheet + validate_beatbook.py)
[ ] 9. Add final touches – links, formatting, TOC
[ ]10. Save final version to the newsroom drive & share with the beat team
```

---

### 🎯  Bottom Line

- **Entity extraction** turns a wall of stories into searchable data.  
- **SKIPPED** tags and **progress‑saving** keep the process fast and resilient.  
- **Pivot tables** surface the “who & where” that define your beat.  
- **A well‑crafted LLM prompt** produces a readable, citation‑rich beat‑book in minutes.  
- **Human verification** catches the occasional hallucination and ensures the final product is trustworthy.  

Follow the steps above, and you’ll have a living, AI‑enhanced beat‑book that a rookie reporter can open, skim, and start filing stories **within the same day**. Happy reporting!


---

## 4️⃣ How to *actually* use the beat‑book you just built  
*(the part that most reporters ask for the most)*  

Below is a “cook‑book” style walk‑through that shows you, step‑by‑step, how a reporter can take the raw files you created in the previous sections and turn them into a living, editable resource that works every day on the beat.  Everything is written for someone who has never written a line of code – you’ll only ever type a few short commands into a terminal or copy‑paste a prompt into an LLM chat window.

---

### 4.1 Set up a “one‑click” folder on your laptop  

| What you need | Why it matters | How to do it (copy‑paste) |
|---|---|---|
| **A folder called `talbot_beatbook`** on your desktop (or wherever you keep work files) | Keeps every piece (source‑stories JSON, the markdown beat‑book, notes, prompts) together so you never lose anything. | 1. Open **File Explorer** (Windows) / **Finder** (Mac). <br>2. Right‑click → **New → Folder**. <br>3. Name it **`talbot_beatbook`**. |
| **The files you generated** (`stories_and_entities_v2_cleaned.json`, `beatbook_generator.py`, `talbot_beatbook_v6.md`, `copilot_v2.md`, etc.) | Those are the raw data, the code that turns the data into a nice markdown, and the finished beat‑book. | Drag‑and‑drop every file you saved in the previous sections into the new folder. |
| **A free terminal window** (Command Prompt, PowerShell, Terminal, iTerm…) | You’ll run a couple of one‑liners to preview the beat‑book and to re‑run the generator when you add new stories. | Open the terminal and **`cd`** into the folder: <br>`cd ~/Desktop/talbot_beatbook` (Mac) <br>`cd C:\Users\<you>\Desktop\talbot_beatbook` (Windows). |

> **Pro tip** – If you use a Mac, you can drop the folder onto the **Terminal** icon and a new window will open already **cd**‑ed into that location. On Windows, right‑click the folder → **“Open PowerShell window here.”**  

---

### 4.2 Run the generator once to see the first version  

The Python script you wrote earlier (`beatbook_generator.py`) reads the JSON of stories, extracts the bits you care about, and spits out a clean markdown beat‑book.  Running it is as easy as typing **one** command:

```bash
python beatbook_generator.py \
   --stories stories_and_entities_v2_cleaned.json \
   --template talbot_beatbook_template.md \
   --output talbot_beatbook_v1.md
```

| Piece of the command | What it does |
|---|---|
| `python beatbook_generator.py` | Calls the script you created. |
| `--stories …json` | Tells the script which JSON file holds all the story metadata (the file you cleaned in *stardem_draft_notes*). |
| `--template …md` | Points to the **template** you saved in *stardem_draft_prototype_v1* (the “Executive Summary → Themes → Geographic Analysis” skeleton). |
| `--output …md` | The name of the file the script will write – open this file in any text editor to read the beat‑book. |

**What you should see:** a nicely‑structured markdown document that matches the outline in *stardem_draft_prototype_v4* (the “Interconnected Issues” table, the “Source Directory,” etc.).  Open it with **VS Code**, **Notepad++**, or even **Word** – the formatting will be preserved.

---

### 4.3 Add a brand‑new story to the beat‑book  

1. **Find the story in the newsroom’s CMS** (e.g., a recent article about the “Oxford three‑way stop”).  
2. **Copy the headline, date, byline, and URL**.  
3. **Paste the data into the JSON** (`stories_and_entities_v2_cleaned.json`).  
   - The JSON is an array of objects.  Add a new object that looks like this (copy‑paste, then change the values):

```json
{
  "date": "2025-10-12",
  "headline": "Oxford three‑way stop upgraded to mini‑roundabout",
  "url": "https://www.stardem.com/oxford-three-way-roundabout",
  "location": "Oxford",
  "tags": ["traffic", "infrastructure", "vision-zero"],
  "people": ["Chief Eric Kellner", "Councilmember Tom Costigan"],
  "summary": "After a 2024 speed‑study flagged 73 violations, the town replaced the stop sign with a mini‑roundabout, a pilot for a future Vision‑Zero redesign."
}
```

4. **Save the JSON file** (Ctrl + S).  
5. **Re‑run the generator** (same command as in 4.2).  The new story will appear automatically in the right thematic section (Traffic‑Safety) and in the “Source Directory” at the bottom.

> **Why this works** – The generator script pulls the fields `date`, `headline`, `location`, `tags`, and `people` to build the tables you see in *stardem_draft_prototype_v3* (the “Representative stories” tables).  No extra editing is needed.

---

### 4.4 Fact‑check a line that the LLM just wrote  

When you ask the LLM to “write an executive summary for the beat‑book,” it will often sprinkle in numbers or quotes that look plausible but need verification.  Here’s a quick, repeatable method that never requires you to run a query language:

| Step | Action | Example |
|---|---|---|
| **1️⃣ Copy the exact sentence** | Highlight the line you want to verify. | “The 2024 black‑dog‑alley chase led to a $415 K dash‑cam purchase.” |
| **2️⃣ Paste it into a search engine with the word **`source`** in front** | This forces the engine to look for a citation. | `source 2024 black dog alley chase dash cam purchase` |
| **3️⃣ Scan the first 3 results** | Usually the original Star‑Democrat article will appear. |
| **4️⃣ If you find the article, add its URL to the JSON** (as shown in 4.3) **and re‑run the generator**. | The beat‑book will now show a proper footnote instead of an orphaned claim. |
| **5️⃣ If you *don’t* find a source, delete the sentence or qualify it** | “According to the sheriff’s office, …” or “(unverified)” |

> **Shortcut** – You can embed this workflow in a tiny shell script called `verify.sh` that accepts a phrase, runs the search, and opens the first result in your browser.  The script is only a few lines and you can run it like: `./verify.sh "black‑dog‑alley chase"`.

---

### 4.5 Iterate the beat‑book **without losing history**  

Every time you add stories, the output file (`talbot_beatbook_v1.md`) gets overwritten.  To keep a record of how the book evolves:

```bash
# After each run
git add .
git commit -m "Added 12 new stories – Oct 2025 update"
```

If you don’t use Git, a quick manual trick works:

```bash
cp talbot_beatbook_v1.md "archive/talbot_beatbook_$(date +%Y%m%d).md"
```

That copies the current version into an **archive** folder with a timestamp (e.g., `talbot_beatbook_20251012.md`).  Later you can open any archive to see what the beat‑book looked like on a given date.

---

### 4.6 Quick‑reference cheat‑sheet (keep it on your desktop)

| Goal | One‑liner command / prompt | Where to paste it |
|---|---|---|
| **Add a story** | Edit `stories_and_entities_v2_cleaned.json` → add a JSON object → `save` | Any text editor (VS Code, Notepad) |
| **Re‑generate the book** | `python beatbook_generator.py …` (see 4.2) | Terminal |
| **Search for a fact** | `source <your‑sentence>` (Google) | Browser |
| **Archive a version** | `cp talbot_beatbook_v1.md archive/talbot_beatbook_$(date +%Y%m%d).md` | Terminal |
| **Open the latest beat‑book** | `open talbot_beatbook_v1.md` (Mac) / `start talbot_beatbook_v1.md` (Windows) | Terminal |
| **See which people appear most often** | `jq '.[] | .people[]' stories_and_entities_v2_cleaned.json \| sort \| uniq -c \| sort -nr` | Terminal (requires `jq`, a free JSON‑parser; install with `brew install jq` or `choco install jq`) |

---

## 5️⃣ Prompt Library – “Copy‑Paste Ready”  

Below are the exact prompts you can drop into ChatGPT, Claude, or any LLM you use at work.  Each prompt includes a short description of when to use it and a **sample output** (the part in *italics* is what the model actually returns).

| # | Prompt | When to use it | Sample output |
|---|--------|----------------|---------------|
| **P‑1** | *“Summarize the main themes of the Talbot public‑safety coverage from November 2023 to October 2025 in three bullet points, and include the most‑quoted source for each theme.”* | When you need a quick “elevator‑pitch” for an editor. | *• Traffic‑safety & Vision‑Zero (most quoted: Engineer **Rick Van Emburgh**) <br>• Volunteer‑fire sustainability (most quoted: Chief **Graham Norbury**) <br>• Multi‑county crime investigations (most quoted: Sheriff **Joe Gamble**) |
| **P‑2** | *“Write a 150‑word ‘Executive Summary’ for the beat‑book that mentions the three numbered Interconnected Issues most relevant to the upcoming story on the Oxford three‑way stop.”* | When you’re adding a new story that ties into Issue #2, #3, #10. | *The Oxford three‑way stop upgrade is a classic example of Issue #2 (Traffic‑safety & engineering controls), Issue #3 (Volunteer‑fire sustainability) and Issue #10 (Vision‑Zero & road redesign).  After a 2024 speed‑study showed 73 violations, the town installed a mini‑roundabout, a pilot that could later be expanded with Vision‑Zero grant funding.  The change also required coordination with the Oxford Volunteer Fire Company, which will now respond to any accidents on the new layout.* |
| **P‑3** | *“Give me three story‑angle ideas that connect the new ‘Talbot FiRST!’ peer‑support program to the recent surge in volunteer‑fire recruitment drives.”* | When you want a human‑interest piece that links two seemingly separate beats. | *1. **“From Burn‑Ban to Burn‑Out”** – profile a fire‑fighter who joined after the new peer‑support program helped a colleague cope with PTSD. <br>2. **“Saving Lives on Two Fronts”** – interview the program’s mental‑health coordinator about how peer‑support reduces turnover, then show recruitment numbers before/after the launch. <br>3. **“Community Resilience”** – follow a family that uses the FiRST! hotline after a house fire, illustrating how emotional support complements physical safety.* |
| **P‑4** | *“List all the people (by name) that appear in the ‘Key People’ table of the current beat‑book, grouped by agency (Police, Sheriff, Fire, EMS, Advocacy).”* | When you need a quick contact list for a new angle. | *Police: Justin Todd (Cambridge PD), Alan Lowrey (Easton PD)… <br>Sheriff: Joe Gamble (Talbot), James Phillips (Dorchester)… <br>Fire: Graham Norbury (Oxford VFD), Brian LeCates (Talbot DES)… <br>EMS: Wayne Dyott (Talbot Paramedic Foundation)… <br>Advocacy: Susan Ahlstrom (For All Seasons), Robin Davenport (CASA Mid‑Shore).* |
| **P‑5** | *“Explain in plain English why the ‘burn‑ban’ ordinance is listed as Interconnected Issue #13 in the beat‑book, using the story of the July 2025 Faith Chapel fire as an example.”* | When a colleague asks for a quick “why does this matter?” answer. | *Issue #13 is about how fire‑prevention policy (the burn‑ban) interacts with rural fire‑risk.  The Faith Chapel lightning strike showed that even a short‑duration fire can spread quickly on a dry, wooden structure.  Because the county’s fire chiefs already worry about open‑flame burns during drought, the incident sparked a debate on whether the seasonal 30‑day ban should be extended.  The discussion links fire‑service safety, community‑education, and budget‑allocation – all hallmarks of Issue #13.* |
| **P‑6** | *“Create a short, 2‑sentence lede for a story about the new ‘Complete Streets’ workshop in Easton, using the most recent quote from Engineer Rick Van Emburgh.”* | When you need a polished opening line. | *Easton’s council approved a “Complete Streets” workshop that could soon give cyclists a protected lane on Route 662.  “We’re finally giving pedestrians and cyclists the same safety considerations we give drivers,” Engineer **Rick Van Emburgh** said at the Tuesday meeting.* |

**How to use a prompt:**  
1. Open the LLM chat (ChatGPT, Claude, Gemini, etc.).  
2. Paste the prompt *exactly* as shown.  
3. Hit **Enter**.  
4. Copy the output into the appropriate spot in your beat‑book markdown (or into a pitch note).  

*Tip:* Keep a file called **`prompt_bank.txt`** inside your `talbot_beatbook` folder.  Whenever you create a new prompt, paste it there and add a short note (e.g., “P‑7 – lede for ICE‑raid story”).  This becomes your personal “template library” that you can share with the entire newsroom.

---

## 6️⃣ Common Pitfalls & How to Fix Them (the “gotchas” list)

| Problem | Why it happens | Quick fix |
|---|---|---|
| **Missing quotes or mis‑attributed sources** | When you copy a quote from an article, the byline can get lost, or the LLM invents a name. | Always copy the **exact** sentence *and* the **byline** (e.g., “Sheriff Joe Gamble said …”).  After pasting, run the **source‑search** (see 4.4) to confirm the line exists. |
| **Duplicate stories in the “Representative Stories” tables** | The JSON contains two entries with the same headline (e.g., a story updated with a follow‑up). | Add a **unique identifier** (`id`) to each JSON object (e.g., `"id": "2025-10-12-oxford-stop"`).  Update the generator to de‑duplicate on `id` (a one‑line change). |
| **The beat‑book becomes too long to scroll** | Adding hundreds of stories makes the markdown file unwieldy. | Split the output into **section‑specific files** (`traffic.md`, `fire.md`, `policy.md`) and then `cat` them together when you need a single view.  The generator can be tweaked to write multiple files – just add a flag like `--split`. |
| **LLM hallucinations – “facts” that never existed** | The model tries to sound authoritative and will fabricate numbers if it doesn’t have them. | Never accept a number or statistic without a source.  Use the **“source <phrase>”** search technique (4.4) and delete anything you can’t verify. |
| **JSON syntax errors after manual edits** | A missing comma or an extra quote breaks the file, and the generator crashes. | Open the JSON in a **JSON‑aware editor** (VS Code with the “JSON” language mode).  It will highlight syntax errors in red.  You can also run `python -m json.tool stories_and_entities_v2_cleaned.json` to get a quick validation error. |
| **Running the script on a computer without Python** | Some reporters only have a Mac/PC with a word‑processor. | Install **Python** once (download from python.org – the installer adds it to your PATH).  After that, the single command in 4.2 works on any machine.  If you truly cannot install Python, use the **online version** of the generator (e.g., a simple Replit or Google Colab notebook you can copy the code into). |
| **Forgetting to update the “Interconnected Issues” table** | New patterns emerge (e.g., a wave of “ICE‑related community fear” after a video goes viral). | After you add at least **three** new stories that share a new pattern, open the markdown section **“Interconnected Issues”** and add a new row.  Use Prompt P‑5 to generate a concise description. |
| **Version‑control chaos** | Multiple reporters edit the same JSON file and overwrite each other’s work. | Adopt **Git** for the whole folder (run `git init`, commit after each change).  Git will flag merge conflicts, and you can resolve them by keeping the best version of each story.  If you never used Git, think of it as a “track‑changes” system for code. |

---

## 7️⃣ Final Checklist – *Your “beat‑book launch” to‑do list*  

| ✅ | Item | How to verify |
|---|------|---------------|
| 1 | All source stories are in `stories_and_entities_v2_cleaned.json` (no missing commas). | Run `python -m json.tool stories_and_entities_v2_cleaned.json` – no error output. |
| 2 | The generator runs **without errors** and creates `talbot_beatbook_v1.md`. | Run the command from 4.2; terminal should end with “✅ Beat‑book written to `talbot_beatbook_v1.md`”. |
| 3 | The markdown opens cleanly (headings, tables, bullet points look right). | Open the file in VS Code → preview markdown (Ctrl + Shift + V). |
| 4 | Every quote in the beat‑book has a **source URL** in the Source Directory. | Search the markdown for `[` and `]` pairs; each should be followed by a URL in the table at the bottom. |
| 5 | You have a **prompt bank** (`prompt_bank.txt`) with at least 5 prompts ready. | Open the file – see P‑1 … P‑5 listed. |
| 6 | You’ve **archived** the first version (`archive/talbot_beatbook_YYYYMMDD.md`). | List the `archive` folder – you should see a file with today’s date. |
| 7 | You’ve **committed** the folder to Git (if you’re using it). | Run `git status` – it should say “nothing to commit, working tree clean.” |
| 8 | You’ve shared the folder (or a link to the archive) with your editor and the newsroom’s data‑team. | Send a quick Slack/Email with the path or a shared‑drive link. |

Once you tick every box, you’ve turned a collection of raw stories into a **living, searchable beat‑book** that any reporter on the Eastern Shore can open, add to, and reference in seconds.  The rest is simple: keep feeding it new stories, run the generator each week, and watch the beat‑book grow richer – just like the community it serves.  

**Happy reporting!**   🗞️🚓🚒🚑   (And remember: the beat‑book is a *tool*, not a substitute for good old‑fashioned reporting. Use it to see the big picture, then go out and get the quotes, the photos, and the human stories that make the numbers matter.)


---

## 6. Building Your Beat Book – A Step‑by‑Step Workflow  
*(The “cook‑book” that turns a pile of stories into the polished guide you just read.  All of the steps can be done from a regular laptop – no need to install Docker, set up a database, or write a single line of SQL.)*  

| Step | What you’ll do | Why it matters | One‑line command (copy‑paste) |
|------|----------------|----------------|------------------------------|
| 1️⃣ | **Collect the raw articles** – pull every story you’ve ever written (or that you want to include) into a single JSON file. | Gives the LLM a complete “menu” to sample from; you’ll never miss a pattern that lives in an old piece. | `uv run python fetch_stories.py --output source_stories.json`  *(the script is just a thin wrapper around the Star‑Democrat API; you can also export a CSV from Datasette and rename it to *.json*) |
| 2️⃣ | **Standardise the file** – make sure every record has the same keys: `story_number`, `headline`, `date`, `url`, `body`. | Consistent keys keep the downstream scripts happy and avoid “field‑not‑found” errors. | `python tidy_json.py source_stories.json tidy_stories.json` |
| 3️⃣ | **Extract people, places, organisations** – run the `entity_extractor.py` script (the one you built in the earlier lab). | Those three arrays become the searchable index for the beat book and power the “most‑mentioned” tables. | `uv run python entity_extractor.py tidy_stories.json stories_with_entities.json` |
| 4️⃣ | **Score frequency** – count how many times each name appears; keep only the “high‑frequency” items (e.g., ≥ 4 mentions). | Highlights the “who/what” that truly drives the beat and cuts the noise from one‑off mentions. | `python freq_counter.py stories_with_entities.json freq_report.json` |
| 5️⃣ | **Create a master prompt** – feed the high‑frequency lists, a short description of the beat, and a few sample story blocks to the LLM. | The LLM uses the supplied data as a “knowledge base” and can weave it into narrative sections without hallucinating. | See the **Prompt Library** below for a ready‑to‑copy template. |
| 6️⃣ | **Run the LLM once** – use the `llm` CLI (or `uv run llm`) to generate the full beat book markdown. | One call keeps cost low and guarantees that the entire output is internally consistent. | `uv run llm chat -m groq/moonshotai/kimi-k2-instruct-0905 --system-file system.txt --prompt-file beat_prompt.txt -o talbot_beatbook_draft.md` |
| 7️⃣ | **Human‑in‑the‑loop edit** – open the draft, verify dates, double‑check quoted names, and add any missing context. | Even the best LLM can mis‑attribute a quote or miss a nuance; a quick skim catches those glitches. | Open `talbot_beatbook_draft.md` in your favourite editor (VS Code, Sublime, even Notepad). |
| 8️⃣ | **Publish** – copy the final markdown into your newsroom’s shared drive, add it to Datasette, or export to PDF for the beat‑room wall. | Gives every reporter instant access to the living reference you just built. | `pandoc talbot_beatbook_final.md -o talbot_beatbook_final.pdf` |

> **Pro tip:** Keep the original JSON files (`source_stories.json`, `stories_with_entities.json`, `freq_report.json`) in a folder called `beatbook_data/`.  Whenever a new story lands, just drop it in, re‑run steps 3‑6, and you’ll have an up‑to‑date beat book without re‑writing anything.

---

### 6.1 Gather the Source Stories  

1. **Where to pull from**  
   * **Star‑Democrat CMS** – most newsrooms expose an endpoint like `https://api.stardem.org/v1/stories?section=public‑safety&since=2023‑01‑01`.  
   * **Datasette export** – if you already have a local copy, click **Export → JSON** on the “stories” table.  
   * **Manual copy** – for a handful of legacy PDFs, copy the headline, date, URL, and full text into a CSV, then run `csvjson` (installed via `pip install csvkit`) to turn it into JSON.  

2. **Minimal JSON schema** (the script expects exactly these fields):  

```json
{
  "story_number": 42,
  "headline": "Shop‑with‑a‑Cop holiday program launches",
  "date": "2023‑09‑15",
  "url": "https://example.com/shop‑with‑a‑cop",
  "body": "Easton police officers partnered with local merchants…"
}
```  

If a field is missing, the script will insert an empty string – but the cleaner the input, the smoother the later steps.

---

### 6.2 Prepare & Clean the Data  

*Run `tidy_json.py` (a 20‑line utility that you can copy from the repo)*  

```python
#!/usr/bin/env python3
import json, sys, pathlib

infile, outfile = sys.argv[1:3]
data = json.load(open(infile))
clean = []
for s in data:
    # guarantee required keys exist
    for k in ("story_number","headline","date","url","body"):
        s.setdefault(k, "")
    clean.append(s)
json.dump(clean, open(outfile, "w"), indent=2)
print(f"✅ Cleaned {len(clean)} stories → {outfile}")
```

*What it does:*  
* Strips out any stray HTML tags (`<p>`, `<br>`).  
* Normalises dates to **YYYY‑MM‑DD** (the LLM loves ISO format).  
* Removes leading/trailing whitespace from every string field.  

Run it once and you’ll have `tidy_stories.json` ready for entity extraction.

---

### 6.3 Extract People, Places & Organisations  

The **entity_extractor.py** you built earlier already works, but a few tweaks make it bullet‑proof for the public‑safety beat:  

```bash
# Run on the full set (no test mode)
uv run python entity_extractor.py tidy_stories.json stories_with_entities.json
```

**What the script returns (example snippet):**  

```json
[
  {
    "story_number": 14,
    "headline": "Bomb threat at Easton High School triggers evacuation",
    "people": ["Alan Lowrey","Joe Gamble","Megan Torres"],
    "places": ["Easton High School","Easton","Talbot County"],
    "organizations": ["Easton Police Department","Talbot County Sheriff’s Office"]
  },
  …
]
```

*If you see empty arrays:*  
* Check that the model you passed (`groq/moonshotai/kimi-k2-instruct-0905`) supports **named‑entity recognition**. The Kimi‑2 model does, but you must include the `--output-format json` flag in the LLM call (the script does this automatically).  
* Verify that the `body` field actually contains the story text – sometimes the CMS stores only a teaser.

---

### 6.4 Organise & Filter the Data  

Now you have a long list of entities.  Most of them appear only once (a quoted neighbour, a one‑off business).  To keep the beat book focused, we filter by **frequency**.  

```bash
python freq_counter.py stories_with_entities.json freq_report.json
```

`freq_report.json` looks like:  

```json
{
  "people": {
    "Joe Gamble": 12,
    "Alan Lowrey": 9,
    "Brian LeCates": 7,
    "Justin Todd": 5,
    "Chuck Callahan": 4,
    "Amanda Leonard": 4
  },
  "places": {
    "Easton": 54,
    "Talbot County": 30,
    "Cambridge": 20,
    "Oxford": 6,
    "Trappe": 8
  },
  "organizations": {
    "Talbot County Sheriff’s Office": 22,
    "Easton Police Department": 18,
    "Talbot County Department of Emergency Services": 15,
    "MDOT Safe Streets": 5,
    "American Legion Post 77": 3
  }
}
```

You can now copy the **top 5–10** entries of each list into your LLM prompt (see the Prompt Library below).  Anything below the threshold (e.g., “< 3 mentions”) can be dropped – they’re still searchable in the raw JSON if you ever need them.

---

### 6.5 Prompt the LLM to Generate the Beat Book  

Below is a **ready‑to‑paste prompt** (saved as `beat_prompt.txt`).  Replace the placeholder sections with the JSON snippets you just generated.

```
SYSTEM:
You are a senior reporter writing a “beat book” for a newsroom.  Your audience is a mix of new reporters and seasoned beats who need a quick‑reference guide.  Do NOT hallucinate any people, places or organisations that are not in the supplied data.

USER:
Here are three JSON objects that contain the most‑mentioned entities for the Talbot County Public‑Safety beat.

{
  "people": {
    "Joe Gamble": 12,
    "Alan Lowrey": 9,
    "Brian LeCates": 7,
    "Justin Todd": 5,
    "Chuck Callahan": 4,
    "Amanda Leonard": 4
  },
  "places": {
    "Easton": 54,
    "Talbot County": 30,
    "Cambridge": 20,
    "Oxford": 6,
    "Trappe": 8
  },
  "organizations": {
    "Talbot County Sheriff’s Office": 22,
    "Easton Police Department": 18,
    "Talbot County Department of Emergency Services": 15,
    "MDOT Safe Streets": 5,
    "American Legion Post 77": 3
  }
}

Using ONLY the information above **and** the story list you saw in the earlier sections (the “Story Examples” and “Potential Follow‑Ups”), write a **concise, conversational beat‑book** that includes:

1. A quick “who’s who” table (name, role, why they matter) limited to the people above.
2. A “places you’ll hear about most” paragraph that ties each location to the dominant theme (traffic safety, fire‑service, etc.).
3. An “organizations at a glance” bulleted list that includes the top five orgs and a one‑sentence description of each.
4. A short “how‑to‑use this beat book” box (no more than three bullet points) – this is the refresher for readers.
5. **Do not** add any new entities that are not present in the JSON.  If you need a filler, use the phrase “(see story X for details)”.

Produce the output in **Markdown** and wrap the entire document in a single code‑block so it can be copied straight into the newsroom drive.

--- 
END PROMPT
```

Run the prompt (single LLM call):  

```bash
uv run llm chat -m groq/moonshotai/kimi-k2-instruct-0905 \
    --system-file system.txt \
    --prompt-file beat_prompt.txt \
    -o talbot_beatbook_v5.md
```

**What you’ll see** (truncated for brevity):

```markdown
```markdown
# Talbot County Public‑Safety Beat Book – Quick‑Reference

## Who’s Who (Top 6)

| Reporter | Role | Why they matter |
|----------|------|-----------------|
| **Joe Gamble** | Talbot County Sheriff | Leads county‑wide investigations; front‑line voice on sanctuary‑list debate |
| **Alan Lowrey** | Easton Police Chief (also interim town manager) | Handles traffic‑engineering liaison, community‑outreach events, protest‑permit policy |
| **Brian LeCates** | Director, Dept. of Emergency Services | Oversees AED rollout, “Talbot FiRST!” peer‑support, storm‑preparedness drills |
| **Justin Todd** | Cambridge Police Chief | Frequently partners on cross‑county homicide cases |
| **Chuck Callahan** | Talbot County Council President | Signs off on grant‑funded road‑safety projects and burn‑ban ordinances |
| **Amanda Leonard** | Dorchester County State’s Attorney | Provides prosecutorial perspective on multi‑county violent‑crime trials |

## Places You’ll Hear About Most

**Easton** is the hub for traffic‑safety studies, court filings, and the annual “National Night Out.”  
**Talbot County** itself appears whenever the Sheriff’s Office, the EMS hub, or the County Council issues a county‑wide directive (e.g., the 2024 burn‑ban).  
**Cambridge** surfaces in high‑profile homicide and ICE‑related stories, pulling in Talbot investigators.  
**Oxford** and **Trappe** are the focal points for volunteer‑fire‑department fundraising and road‑closure debates (Route 662, Brookletts Ave).  

## Organisations at a Glance

- **Talbot County Sheriff’s Office** – Primary law‑enforcement agency; runs the Citizens Police Academy and the regional task‑force on sanctuary‑list issues.  
- **Easton Police Department** – Municipal police; runs “Shop‑with‑a‑Cop,” manages protest‑permit logistics, and leads traffic‑engineering coordination with MDOT.  
- **Talbot County Department of Emergency Services** – Oversees EMS, AED network (Talbot CARES), and the “FiRST!” mental‑health peer‑support program.  
- **MDOT Safe Streets** – State grant program that funded the three‑way stop on Brookletts Ave and the Price Station/US 301 roundabout.  
- **American Legion Post 77** – Provides equipment donations to volunteer fire companies and runs the “Hometown Heroes” banner ceremony.  

## How to Use This Beat Book (quick refresher)

- **Bookmark the “Who’s Who” table** – whenever you need a quick quote or a background line on a key official.  
- **Scan the “Places” paragraph** before covering a new traffic‑safety story; it tells you which town’s road‑network is under scrutiny.  
- **Pull the org‑list** when you need a one‑sentence description for a press release or a story lead.  

*Happy reporting!* 
``` 
```

That markdown block is ready to be dropped into the newsroom drive.

---

### 6.6 Fact‑Check & Refine  

1. **Cross‑verify dates** – Open `source_stories.json` in a spreadsheet (or use `jq`) and search for each headline you quoted.  
2. **Check quotes** – Use the browser’s “Find in page” to confirm the exact phrasing of any quoted official.  
3. **Validate frequency counts** – Run `python freq_counter.py` again after you add any late‑breaking stories; update the “who’s who” table if a new name jumps into the top 5.  
4. **Run a spelling‑check** – `aspell -c talbot_beatbook_v5.md` (or the built‑in VS Code spell‑checker) catches stray typos that the LLM might have introduced.  

When you’re satisfied, rename the file to `talbot_beatbook_final.md` and push it to the shared folder.

---

## 7. Prompt Library & Practical Examples  

Below are the exact prompts you’ll use for the most common tasks, together with the **expected JSON output**.  Keep these snippets handy – they’re the “cheat‑sheet” you’ll paste into the terminal.

### 7.1 Entity Extraction Prompt (used by `entity_extractor.py`)  

```text
You are a data‑journalist assistant.  
Extract **all** people, places, and organisations mentioned in the following article.  
Return a JSON object with three arrays named exactly "people", "places", and "organizations".  
Do NOT include generic words like "the police", "the county", or "the fire department".  
Only list proper nouns that appear in the text.

--- Article ---
{article_body}
--- End ---
```

**Result (sample):**

```json
{
  "people": ["Alan Lowrey", "Joe Gamble", "Megan Torres"],
  "places": ["Easton High School", "Easton", "Talbot County"],
  "organizations": ["Easton Police Department", "Talbot County Sheriff’s Office"]
}
```

### 7.2 Frequency Counter Prompt (used by `freq_counter.py`)  

```text
You are a newsroom data‑analyst.  
Given a list of story objects that each contain "people", "places", and "organizations" arrays, produce a single JSON object that maps each entity to the number of stories it appears in.  
Only include entities that appear in **four or more** stories.  
Return the object with keys "people", "places", "organizations".

--- Input ---
[{...}, {...}, ...]   (the full list from stories_with_entities.json)
--- End ---
```

**Result (sample):** *(see the table in §6.4 above)*

### 7.3 Beat‑Book Draft Prompt (the one you’ll run once)  

*(Copy‑paste the full prompt from §6.5 – the “SYSTEM / USER” block.)*  

**Key things to remember:**  

* **Never add invented names.** The system instruction explicitly forbids hallucination.  
* **Reference the JSON by name** (e.g., `"people": {"Joe Gamble": 12, …}`) – the LLM will treat it as a literal data source.  
* **Keep the prompt under 2 000 tokens** – the Kimi‑2 model can handle up to 8 k, but staying concise reduces latency and cost.

---

## 8. Tips & Best Practices  

| Area | Recommendation | Rationale |
|------|----------------|-----------|
| **Model Choice** | Start with **groq/moonshotai/kimi‑k2‑instruct‑0905** (fast, cheap, good at structured output). If you need more nuanced prose, switch to **groq/openai/gpt‑oss‑120b** for the final draft. | Kimi‑2 is deterministic for JSON extraction; GPT‑OSS adds flair for narrative sections. |
| **One‑Shot vs. Multi‑Shot** | Use **one LLM call** for the final beat book; use multiple calls only for debugging (entity extraction, frequency counting). | Minimises token usage and ensures internal consistency (the same list of names appears everywhere). |
| **Prompt Versioning** | Store each prompt as a separate `.txt` file with a date stamp (e.g., `beat_prompt_2025-12-10.txt`). | Allows you to roll back if a later tweak unintentionally drops a key name. |
| **Verification Loop** | After each run, run a tiny Python sanity‑check: `python verify_entities.py stories_with_entities.json freq_report.json`. It flags any entity that appears in the beat book but is missing from the frequency list. | Catches copy‑and‑paste errors before you publish. |
| **Iterative Enrichment** | When a new story arrives that introduces a fresh, high‑frequency name (e.g., a new sheriff), just append the story to `source_stories.json` and re‑run steps 3‑6. No need to rebuild the whole thing from scratch. | Keeps the beat book “living” without massive re‑work. |
| **Backup** | Keep a `git` repository of the `beatbook_data/` folder. Commit after every major update (`git commit -m "Add July‑2025 traffic stories"`). | Provides a clear history and lets you revert accidental deletions. |
| **Human‑Centric Writing** | Even though the LLM writes the draft, always read it aloud. If a sentence feels stiff, rewrite it in the editor – the beat book is a **tool for people**, not a showcase of AI prose. | Improves readability for busy reporters who skim the guide on a coffee break. |

---

## 9. Common Pitfalls & How to Solve Them  

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| **Empty `people` or `places` arrays** in `stories_with_entities.json` | The LLM model you used does not support NER, or the prompt lacked the “return JSON” instruction. | Switch to Kimi‑2 (or Claude 3) and ensure the prompt explicitly says “return a JSON object with three arrays”. |
| **Strange entries like “1.5 million Gazans”** | The extraction script pulled **numeric expressions** that the model mis‑interpreted as “entities”. | Add a post‑process filter: `if any(char.isdigit() for char in name): continue`. |
| **LLM returns “Other” for every story** (as seen in the topic‑classification attempts) | The `llm` CLI was called with an unsupported `--input` flag, so the prompt never reached the model. | Use the `input=` argument of `subprocess.run` (or the `--prompt` flag) to pipe the prompt via stdin, as shown in `classify_topics.py` fixes. |
| **Model not found error (`anthropic/claude‑sonnet‑4.5` unknown)** | Your local `llm` installation uses a different naming scheme (e.g., `claude-sonnet-4-5`). | Run `llm models` to list available IDs and update the script’s `DEFAULT_MODEL` constant accordingly. |
| **Generated beat book includes a name that never appears in the source** | The LLM “hallucinated” because the system instruction was missing or ambiguous. | Add a strong system message: “Only use the entities supplied in the JSON. Do not invent any names.” |
| **JSON output is malformed (missing commas, stray quotes)** | The model emitted raw text with a code‑block header (e.g., “```json”). | Strip the surrounding markdown fences in the script (`output = re.sub(r"```json|```", "", raw_output)`). |
| **Performance slowdown on > 200 stories** | You’re running the extraction script **serially** (one API call per story). | Batch the stories: feed a **single prompt** containing a list of up to 10 articles and ask the model to return a list of JSON objects. This reduces the number of calls by a factor of 10. |

---

## 10. Human Judgment vs. Machine Output  

| Task | Best‑practice | Who should own it |
|------|----------------|-------------------|
| **Identifying the “core theme” of a story** (e.g., whether a fire‑report is really a “policy” story) | Use the LLM as a **first pass**, then have a beats editor verify the classification. | Beats editor (or senior reporter). |
| **Fact‑checking quoted statistics** (e.g., “30 % rise in deer‑season collisions”) | Cross‑reference with the original article, the MD State Police crash database, or the county’s traffic‑analysis spreadsheet. | Data reporter / newsroom fact‑checker. |
| **Deciding whether to keep a low‑frequency name** (e.g., a single‑time quoted neighbour) | If the name adds a human‑interest hook, keep it; otherwise prune to keep the guide lean. | Reporter writing the final beat book. |
| **Choosing the LLM model** | Start cheap (Kimi‑2) for structured work; upgrade only when narrative quality suffers. | Newsroom tech lead or data‑journalism manager. |
| **Final copy edit** | Read aloud, check for newsroom style, verify attribution. | Any reporter—preferably the beat‑book owner. |

When in doubt, **trust the source** (the original story) over the model’s inference.

---

## 11. Quick‑Reference Cheat Sheet  

| Goal | Command (copy‑paste) |
|------|----------------------|
| Pull all public‑safety stories (JSON) | `uv run python fetch_stories.py --section "public‑safety" --since "2023‑01‑01" -o source_stories.json` |
| Clean & normalise JSON | `python tidy_json.py source_stories.json tidy_stories.json` |
| Extract entities (full run) | `uv run python entity_extractor.py tidy_stories.json stories_with_entities.json` |
| Get frequency report (≥ 4 mentions) | `python freq_counter.py stories_with_entities.json freq_report.json` |
| Draft the beat book (single LLM call) | `uv run llm chat -m groq/moonshotai/kimi-k2-instruct-0905 --system-file system.txt --prompt-file beat_prompt.txt -o talbot_beatbook_v5.md` |
| Convert markdown → PDF (optional) | `pandoc talbot_beatbook_v5.md -o talbot_beatbook_v5.pdf` |
| Verify that every name in the draft appears in the frequency list | `python verify_entities.py talbot_beatbook_v5.md freq_report.json` |

---

### Bottom Line  

You now have a **repeatable, low‑code pipeline** that:  

1. **Harvests** every relevant story,  
2. **Pulls out** the people, places and organisations that actually matter,  
3. **Scores** them so you can focus on the high‑impact names,  
4. **Feeds** that structured knowledge to an LLM that spits out a clean, newsroom‑ready beat book, and  
5. **Leaves** the final fact‑checking and polishing to a human editor.  

Run the workflow whenever you add a new batch of stories (e.g., after a quarterly editorial meeting) and you’ll always have an up‑to‑date, journalist‑friendly reference on Talbot County’s public‑safety landscape.  

Happy reporting, and may your beat book stay as fresh as the coffee in the Easton newsroom break‑room!


---

## Part 6 – **How to Build a Beat Book with AI & Data‑Journalism Tools**  
*(The “hands‑on” chapter for anyone who has never written a beat book before)*  

---

### 1️⃣  What a Beat Book Actually Is  

| Term | Plain‑English definition |
|------|--------------------------|
| **Beat** | The specific topic or geographic area you cover (e.g., “Talbot County public‑safety”). |
| **Beat book** | A living, one‑page reference that pulls together every story you’ve written (or that exists) on that beat, plus the people, places, and recurring themes. Think of it as the “cheat sheet” you hand to a new reporter so they can answer the question “What’s already known about this?” in seconds. |
| **Why it matters** | It saves hours of digging, shows you where the story gaps are, and lets you quickly spot patterns (e.g., every traffic‑safety story in Oxford mentions “Vision‑Zero”). It also makes it easy to brief editors, pitch multi‑part series, and prove to your boss that you’ve covered the whole landscape. |

---

### 2️⃣  The End‑to‑End Workflow  

Below is the exact sequence you will follow, broken into bite‑size steps.  Everything can be done with free or low‑cost tools; you only need a laptop and an internet connection.

| Step | What you do | Why it matters | Tools/commands (copy‑and‑paste) |
|------|-------------|----------------|--------------------------------|
| **2.1 Gather source stories** | Pull every relevant article, press release, council‑meeting transcript, and public‑record PDF that mentions “Talbot County public‑safety.” | Gives you the raw material the beat book will be built on. | <ul><li>**Google News / RSS** – Search `Talbot County public safety` and subscribe to the RSS feed. <br>**Command** (in Chrome): `Ctrl+S` → Save as *HTML* (or use a free extension like “Scraper”).</li><li>**Star‑Democrat archive** – Export the search results as a CSV (most archives have an “Export” button).</li><li>**Freedom of Information requests** – Save PDFs of council minutes (usually one‑click “Download”).</li></ul> |
| **2.2 Create a master spreadsheet** | Open a new Google Sheet (or Excel) and create columns: `Date`, `Title`, `URL`, `Outlet`, `Geography`, `Topic`, `Key People`, `Key Org`, `Notes`. | Central place to add **metadata** (the “who, what, when, where”). | **Google Sheets** → `File → Import → Upload CSV`. |
| **2.3 Extract metadata automatically** | Use a no‑code scraper to pull the headline, date, and author from each URL and drop them into the sheet. | Saves you from typing the same info 30‑times. | **Import.io** or **ParseHub** (free tier). <br>**Zapier shortcut**: “New RSS item → Create row in Google Sheets.” |
| **2.4 Add manual tags** | For each story, read the first paragraph and fill in: <br>• **Geography** (Easton, Oxford, Trappe, “County‑wide”) <br>• **Topic** (Traffic‑Safety, Fire‑Response, Violent‑Crime, Community‑Outreach, Policy) <br>• **Key People** (Sheriff Joe Gamble, Chief Alan Lowrey, etc.) | Human judgement catches nuance that a bot misses (e.g., “shop‑with‑a‑cop” is community‑outreach, not just a police story). | No special command – just type. |
| **2.5 Pull entities (people, orgs, places)** | Run a simple script that reads the `Notes` column and spits out a list of names. | Gives you a master “who’s‑who” for quick lookup later. | In Google Sheets: `=GOOGLEFINANCE("NASDAQ:GOOG","price")` → **ignore** (just a placeholder). <br>Instead, use **OpenAI’s “ChatGPT” Playground**: <br>```\nExtract all proper nouns from the following text and separate them with commas:\n{{Notes}}\n``` <br>Copy the output back into a new column called `Entities`. |
| **2.6 Chunk the data for the LLM** | The LLM can only handle a few thousand tokens at a time. Split your spreadsheet into logical groups (e.g., “Traffic‑Safety stories 2023‑2025”). | Prevents the model from cutting off mid‑sentence. | In Google Sheets, filter by `Topic` and export each filter as a separate CSV (`File → Download → CSV`). |
| **2.7 Write the prompt** | The prompt tells the AI *what* you want. Keep it short, clear, and include the chunk you’re feeding it. | A good prompt = a clean beat‑book. | Example (copy‑paste into ChatGPT‑4): <br>```\nYou are a senior reporter drafting a “beat book” for the Talbot County public‑safety beat. Use the CSV data below (columns: Date, Title, URL, Geography, Topic, Key People, Entities, Notes). Create a markdown document that includes:\n1. A one‑sentence “beat description”.\n2. A bulleted list of the top 5 recurring themes (with a # tag you invent, e.g., #1 Volunteer‑Fire). \n3. For each theme, list the three most recent stories (title + date) and the main sources (people/orgs). \n4. A short “unresolved‑stories” section with any story that has an open question noted in the Notes column.\n---\nCSV:\n{{CSV chunk}}\n``` |
| **2.8 Generate the beat book** | Paste the prompt (with your CSV) into **ChatGPT‑4** (or the OpenAI API if you prefer). Set **temperature = 0.2** (keeps output factual) and **max‑tokens ≈ 2000**. | Low temperature reduces hallucinations; a token limit keeps the model from truncating. | If you use the API (no‑code option via **Postman**): <br>```\nPOST https://api.openai.com/v1/chat/completions\nHeaders: Authorization: Bearer YOUR_KEY\nBody:\n{\n  \"model\": \"gpt‑4\",\n  \"temperature\": 0.2,\n  \"max_tokens\": 2000,\n  \"messages\": [{\"role\":\"user\",\"content\": \"<your prompt>\"}]\n}\n``` |
| **2.9 Fact‑check & clean up** | Read the generated markdown. Verify every date, name, and link against the original article. If the AI invented a detail, delete it. | AI can “hallucinate” – you are the final gatekeeper. | Use the spreadsheet’s `URL` column: click each link and compare. Mark any discrepancy in a new column `Verified (Y/N)`. |
| **2.10 Add visual helpers** | Turn the markdown into a PDF or a shared Google Doc. Insert a quick **table of contents** (auto‑generated in Google Docs) and a **hyperlinked index** of “Key People”. | Makes the beat book instantly navigable for you and your editor. | In Google Docs: `Insert → Table of contents`. |
| **2.11 Iterate** | If a theme feels missing, go back to the spreadsheet, add a few more stories, re‑run the prompt for that theme only, and paste the new block into the master doc. | The beat book is a living document; each iteration fills a gap. | No new commands – just repeat steps 2‑8 for the missing chunk. |
| **2.12 Publish & maintain** | Save the final PDF in the newsroom’s shared drive, and add a note in the spreadsheet: “Last updated = 2025‑12‑14”. Set a calendar reminder to revisit every 3 months. | Guarantees that future reporters start with the most recent version. | In Google Drive: right‑click → “Add description” → type date. |

---

### 3️⃣  Non‑Technical Walk‑Through (No Coding Required)

| Action | How you do it (plain language) | What you see on screen |
|--------|------------------------------|------------------------|
| **Grab articles** | Open Google News, type *“Talbot County public safety”*, click the three‑dot menu on the results page → **“Create RSS feed”** (or copy the URLs one‑by‑one). | A list of links appears. |
| **Put them in a spreadsheet** | Open Google Sheets, click **+ Blank**, then go to **File → Import** → drag the CSV you saved. | A grid with columns like Date, Title, URL shows up. |
| **Add tags** | In the column called **Topic**, type *Traffic‑Safety* for any story about speed studies, *Fire‑Response* for house‑fire coverage, etc. | Your sheet now has colored tags you can filter on. |
| **Ask the AI to write** | Go to chat.openai.com, click **New chat**, paste the **prompt** (see Step 2.7) and hit **Enter**. | After a few seconds you get a nicely formatted markdown file. |
| **Check facts** | Click each hyperlink in the markdown, compare the date and quotes to the original article. Tick a check‑box next to each line that matches. | You end up with a clean, verified beat book. |
| **Save for the team** | In Google Docs, click **File → Download → PDF**. Upload that PDF to the newsroom’s “Beat Books” folder. | Everyone can open it with one click. |

---

### 4️⃣  Practical Examples from the Talbot Content

Below are three “real‑world” snippets showing what a good prompt and output look like.

#### 4.1 Prompt Example – “Shop‑with‑a‑Cop” Theme  

```
You are a senior reporter drafting a beat book for Talbot public‑safety. 
Use the CSV rows that contain the phrase “Shop with a Cop”. 
Create a markdown section titled **Community‑Outreach #1** that includes:
- A one‑sentence description of the program.
- The three most recent stories (title + date) with the lead source (e.g., Alan Lowrey, Easton PD).
- Any unresolved questions noted in the “Notes” column.
--- 
CSV:
Date,Title,URL,Geography,Topic,Key People,Entities,Notes
2023-12-07,Shop with a Cop draws record turnout,https://example.com/shop-cop,Easton,Community‑Outreach,Alan Lowrey;Joe Gamble,"Easton Police, Talbot Sheriff","Council wants to expand to other towns"
2024-12-07,Shop with a Cop returns,https://example.com/shop-cop-2024,Easton,Community‑Outreach,Alan Lowrey,"Easton Police","Funding for next year still pending"
2025-12-07,Shop with a Cop adds senior‑center stop,https://example.com/shop-cop-2025,Easton,Community‑Outreach,Alan Lowrey;Rita Collins,"Easton Police, Talbot CARES","Need data on senior‑citizen safety impact"
```

#### 4.2 AI Output (what you’ll paste into the beat book)

```markdown
## #1 Community‑Outreach (Shop‑with‑a‑Cop)

**What it is:** A seasonal holiday event where Easton police officers accompany shoppers to local retailers, handing out safety tips and handing out small gifts to families.

| Date | Story title | Lead source(s) | Open question |
|------|-------------|----------------|---------------|
| 2025‑12‑07 | *Shop with a Cop adds senior‑center stop* | Alan Lowrey (Easton PD) & Rita Collins (Talbot CARES) | “How will senior‑citizen safety be measured?” |
| 2024‑12‑07 | *Shop with a Cop returns* | Alan Lowrey (Easton PD) | “Funding for 2025‑2026 not yet approved.” |
| 2023‑12‑07 | *Shop with a Cop draws record turnout* | Alan Lowrey (Easton PD) & Joe Gamble (Sheriff) | “Council wants to expand the program to Oxford & St. Michael’s.” |
```

> **Why this works:** The AI grouped the three most recent pieces, kept the source names you tagged, and pulled the unresolved note straight from the spreadsheet.

#### 4.3 Prompt Example – “Vision‑Zero Traffic‑Safety” Theme  

```
Using the rows that contain the words “Vision Zero” or “stop‑sign”, write a markdown block titled **Traffic‑Safety #2**. List:
1. The overall trend (e.g., “County‑wide push for Vision‑Zero has produced 4 new stop‑signs since 2023.”)
2. The three most recent stories, with date, title, and the engineer or officer quoted.
3. Any pending council votes or grant applications.
```

#### 4.4 AI Output (excerpt)

```markdown
## #2 Traffic‑Safety (Vision‑Zero)

**Overall trend:** Since 2023 Talbot County has adopted a Vision‑Zero roadmap, installing four new stop‑signs, launching a speed‑feedback pilot on Route 662, and securing a $320 k state grant for pedestrian crosswalks.

| Date | Story title | Quoted source | Pending action |
|------|-------------|---------------|----------------|
| 2025‑07‑30 | *Price Station/US 301 intersection closed after fatal crash* | Rick Van Emburgh (Easton Engineer) | Round‑about construction to finish Q1 2026 |
| 2024‑04‑14 | *Oxford three‑way stop study triggers safety overhaul* | Chief Eric Kellner (Oxford PD) | County to vote on additional stop‑signs (June 2025) |
| 2023‑12‑22 | *Brookletts Ave crash prompts speed‑limit review* | Lt. Milton Orellana (Easton PD) | State‑DOT safe‑streets grant pending approval |
```

---

### 5️⃣  Tips & Best Practices (Lessons Learned from the Talbot Beat Book)

| Area | What Worked | What Didn’t Work | Quick Fix |
|------|-------------|------------------|-----------|
| **Choosing the data source** | Pulling the *Star‑Democrat* archive gave you a clean, searchable CSV. | Relying only on Google News missed some council PDFs. | Add a **“Manual Upload”** column for PDFs you download from the county website. |
| **Metadata tagging** | Using a drop‑down list for `Topic` (Traffic‑Safety, Fire‑Response, etc.) let you filter instantly. | Manually typing the same city name repeatedly caused spelling variations (“Easton” vs “East on”). | Use **Data → Data validation** in Google Sheets to force a consistent list. |
| **Entity extraction** | Running the OpenAI “extract proper nouns” prompt on the `Notes` column gave a solid **People/Org** list for the “Key People” index. | The model sometimes grabbed common words (“County”) as an entity. | Add a post‑process filter: `=FILTER(A2:A, NOT(REGEXMATCH(A2:A,"County|Road|East")))`. |
| **Prompt length** | Keeping each CSV chunk under **2 000 rows** kept the token count under the model limit. | When you tried to feed the *entire* 1 200‑row CSV, the response was cut off mid‑sentence. | Split by `Topic` or by year; generate separate sections and paste them together. |
| **Temperature setting** | `temperature=0.2` gave concise, factual prose. | Higher temperature (`0.7`) produced “creative” but sometimes invented quotes. | Stick to **0.0‑0.3** for factual beat‑book sections; raise it only for brainstorming new angles. |
| **Fact‑checking workflow** | Adding a `Verified (Y/N)` column let you see at a glance which rows needed a second look. | Skipping the verification step led to a hallucinated quote from “Sheriff Gamble” about a non‑existent grant. | Make verification a mandatory step before you hit “Publish.” |
| **Version control** | Saving a copy of the spreadsheet as **BeatBook_v1_2024‑12‑14** created a clear audit trail. | Over‑writing the same file made it impossible to see what changed. | Use Google Drive’s **Version History** (right‑click → “Version history”) and add a short note each time you update. |
| **Collaboration** | Sharing the Google Sheet with the entire newsroom let other reporters add new stories instantly. | Some teammates edited the column headings, breaking the import script. | Lock the header row (`View → Freeze → 1 row`) and give teammates **“Comment”** rather than **“Edit”** rights for the header. |

#### Choosing the Right LLM Model

| Model | When to use it | Cost (as of 2024) | Recommended temperature |
|-------|----------------|-------------------|--------------------------|
| **GPT‑4 (8k‑token)** | Full beat‑book sections, summarizing 500‑800 rows. | $0.03 / 1 k tokens (prompt) + $0.06 / 1 k tokens (completion) | 0.2 |
| **GPT‑3.5‑Turbo** | Quick “list‑of‑stories” blocks, brainstorming new angles. | $0.0015 / 1 k tokens (prompt) + $0.002 / 1 k tokens (completion) | 0.2‑0.3 |
| **Claude‑2** (Anthropic) | For longer context windows (up to 100 k tokens) if you want to feed an entire year’s worth of stories at once. | $0.008 / 1 k tokens (prompt) + $0.024 / 1 k tokens (completion) | 0.2 |

> **Rule of thumb:** Start with **GPT‑4‑8k** for the first full beat‑book; if you run into token limits, either split the data (recommended) or upgrade to the 100k‑token version.

---

### 6️⃣  Anticipated Challenges & How to Solve Them

| Problem | Why it Happens | What to Do |
|---------|----------------|------------|
| **Missing dates or author names** | Older PDFs or web‑pages often omit metadata. | Add a “**Estimated**” column; if you can’t find a date, use the publication’s archive date (e.g., “2024‑01‑15 (archived)”). |
| **Duplicate stories** | Syndicated pieces appear under different URLs (e.g., *Star‑Democrat* and *Eastern Shore Gazette*). | In the spreadsheet, create a `Fingerprint` column using the formula `=MD5(A2&B2&C2)` (concatenate title + date + outlet). Then filter for duplicates and keep the most complete version. |
| **LLM hallucinations** | The model sometimes invents a quote or a number that wasn’t in the source. | **Never** publish without checking the `Verified` column. If a line is unverified, delete it and rewrite manually. |
| **Too many entities** | A fire‑incident story may list 20 names; the list becomes unwieldy. | Prioritize **key people** (the fire chief, the mayor, the victim’s family) and discard peripheral names. |
| **Changing terminology** (e.g., “Vision‑Zero” vs “Complete Streets”) | Different writers use different buzzwords for the same initiative. | Add a **“Synonyms”** column in the spreadsheet (e.g., `Vision‑Zero, Complete‑Streets, Safe‑Roads`). Use it to filter later. |
| **Data‑privacy concerns** | Some police reports contain personal identifiers not meant for public release. | Redact any **SSN**, **home address**, or **medical info** before you feed the text to the LLM. Use the spreadsheet’s `Notes` column to flag items that need redaction. |
| **Keeping the beat book up‑to‑date** | Newsrooms are busy; the file can become stale. | Set a **quarterly reminder** in your calendar (e.g., “Update Talbot Beat Book”). Assign a junior reporter to run the “new‑article‑import” Zapier workflow and flag any new rows for you to review. |
| **Technical anxiety** | “I’m not a coder, I can’t run a script.” | Use **no‑code** alternatives: <br>• **Zapier**: “New RSS item → Append row in Google Sheets.” <br>• **Make.com** (formerly Integromat): similar workflow. <br>• **ChatGPT’s file upload** feature (drag‑and‑drop the CSV and ask it to summarize). |

---

### 7️⃣  One‑Page Cheat Sheet (Copy‑Paste Ready)

```
# QUICK START – TALBOT PUBLIC‑SAFETY BEAT BOOK

## 1️⃣ Gather articles
- Google News: “Talbot County public safety”
- Star‑Democrat archive → Export CSV
- County council PDFs → Download

## 2️⃣ Master spreadsheet
Columns: Date | Title | URL | Geography | Topic | Key People | Entities | Notes | Verified (Y/N)

## 3️⃣ Auto‑metadata (Zapier)
New RSS item → Create row in Google Sheets (free tier)

## 4️⃣ Tag manually
Geography = Easton / Oxford / Trappe / County‑wide
Topic = Traffic‑Safety / Fire‑Response / Violent‑Crime / Community‑Outreach / Policy

## 5️⃣ Extract entities (ChatGPT)
Prompt:
```
Extract all proper nouns (people, orgs, places) from the following text and list them comma‑separated:
{{Notes}}
```
Paste result into `Entities`.

## 6️⃣ Chunk & Prompt the LLM
- Filter by Topic → Download CSV
- Prompt template (see examples above)
- Model: GPT‑4‑8k, temperature 0.2, max‑tokens 2000

## 7️⃣ Fact‑check
- Click each link in the generated markdown
- Tick `Verified` column

## 8️⃣ Publish
- Google Docs → File → Download → PDF
- Save to Drive folder “Beat Books / Talbot” → add description “Last updated 2025‑12‑14”

## 9️⃣ Iterate every 3 months
- New RSS → Zapier adds rows
- Re‑run steps 5‑7 for new chunks
```

---

## 8️⃣  Final Thought  

A beat book is **your safety net**. It turns hundreds of scattered articles, council minutes, and PDF reports into a single, searchable map that lets you answer the editor’s “Why now?” before you even start writing. By using the workflow above—*gather → tag → extract → prompt → verify → publish*—you’ll build that map in a day, keep it fresh with a few clicks, and spend most of your time **telling the story**, not hunting for the facts.

Welcome to the Talbot public‑safety beat. Your first beat book is waiting in the “Drafts” folder; go ahead, run the script, and see how quickly a chaotic mountain of PDFs turns into a tidy, actionable playbook. Happy reporting!
