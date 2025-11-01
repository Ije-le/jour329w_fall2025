# Star-Democrat Metadata

In this assignment, we'll add important metadata to our collection of Star-Democrat stories, and then use them to separate the stories into topics. We'll start with extracting the section, page numbers and word count, then proceed to classifying different types of stories to properly label non-articles such as event calendars, obituaries and legal notices. We'll start with your sample of Star-Democrat stories and compare the results.

### Setup

Update from upstream: 

```{bash}
git fetch upstream
git merge upstream/main
```

### Getting Started

In your class repository, open a codespace and do the following:

1. In the Terminal, cd into the directory with your last name.
2. Create a directory called stardem_metadata using mkdir
3. cd into that new directory
4. Create a file called notes.md using touch. Keep that file open.
5. Open that document and put "CNS Metadata" and today's date at the top, then save it
6. Do cd .. twice to get back to the main directory (/workspaces/jour329w_fall2025)
7. In the Terminal, do the git add, commit, pull and push your changes as described in the `setup.md` file.

### Add Sections

Make sure you have the `llm-groq` plugin installed:

```bash
uv run llm install llm-groq
```

You must use one of the following groq models: 

groq/openai/gpt-oss-20b
groq/openai/gpt-oss-120b
groq/meta-llama/llama-4-maverick-17b-128e-instruct
groq/moonshotai/kimi-k2-instruct-0905


Let's use the `add_metadata.py` script you created for the CNS Collections assignment. Copy that:

```bash
cp ../cns_collections/add_metadata.py add_sections.py
```

Let's look at that file: it currently does more than we need. As with the CNS collections assignment, you'll modify the prompt to do what we want: in this case, extract the section title, page number and word count. To help the LLM, you'll add an example to your prompt in addition to providing the structure of the JSON output. Change the output file to `enhanced_stories.json`. Then run the script; it'll take a bit to process all 200 entries:

```bash
uv run python add_sections.py --model YOUR MODEL --input stardem_sample.json
```

### Repeat

Do the same steps as before, picking another model and change the schema_prompt so that it looks like this:

```python
 schema_prompt = """
    {
      "section2": "the section",
      "page2": "the page",
      "word_count2": word_count
    }
    """
```

Re-run the script using the `enhanced_stories.json` as input:

```bash
uv run python add_sections.py --model OTHER MODEL --input enhanced_stories.json
```

In your `notes.md` file, be sure to list which models you used.

### Evaluation 

Now explore your results using Datasette:

```bash
# Create a SQLite database from your classified stories
uv run sqlite-utils insert stardem_metadata.db stories enhanced_stories.json --pk docref

# Launch Datasette to explore
uv run datasette stardem_metadata.db
```

Use facets and filters to explore the new metadata and evaluate the results in your `notes.md` file. Do the results look accurate? Are there any records that don't have all three (or six) new attributes? Do the results from the two models agree?

When you are finished, add, commit and push your changes:

```{bash}
git add .
git commit -m "replace with your commit msg"
git pull origin main
git push origin main
```

Submit the link to your `notes.md` file in ELMS.