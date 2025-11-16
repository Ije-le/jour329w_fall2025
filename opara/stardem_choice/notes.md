## Stardem_choice     11/12/2025

# Note: The two useful json files here are stories_with_entities_v1.json, stories_with_entities_v2.json and stories_with_entities_v4.json. v3 was generated in error,

# Documentation:
I had started this exercise with stories_with_entities_v1.json, using the groq/meta-llama/llama-4-maverick-17b-128e-instruct for 926 stories, but that started to return a rate-limit error after 150 stories, so I ended it, thinking it was a thing with the script. Then I began the same process for stories_with_entities_v2.json with the same model. That was slow too, but it ended on its own because a notification popped up on my screen that I had to stop my codespaces and restart. Because I did not see any reasonable improvement in the speed, I decided to use the groq/moonshotai/kimi-k2-instruct-0905 for the next trial. I saved these stories to replace the incomplete data in stories_with_entities_v1.json (since I now had two versions with incomplete data). It was also at this point that I reduced the sample size to 300. The Kimi model was still very slow, but I let it run. Because of the rate-limt error, this took more than six hours, but the scripts eventually got processed.

While testing the output before running the entire input json, I noticed the model was ignoring my prompts requesting that it skips processing for stories with no geographical ties to Eastern Shore. It would say "Skipped processing ..." in the timeline, and still return values in the output json file. Since it insisted on returning values, I asked Copilot to do this:
    "Instead of returning any values  for names, places and organizations for the stories that have no geographical focus in Eastern Shore, update the prompt so that the the only values in the list for these stories says SKIPPED Remember to keep the prompt in a variable format."
This mostly worked. When it returned the output json, theere were two stories I saw that had values returned even though they were unconnected to Eastern Shore. But the model skipped about 23 stories out of 300.

For the next variation, I decided to use a different model to see how it would perform with skipping the stories I did not want.
Also, since I lost my progress at least twice for this task, I asked copilot what I could do about it and copilot suggsted that I update my prompt to include a command that saves each result to the otput json after they are processed, so that even if I have to start afresh, I wouldn't lose the progress I'd made. I updated my prommt to reflect this.
# promt here:

I tried using the glm-4.6:cloud, but it kept saying all stories had been processed. I tried switching to a new topic: Public Safety, but I still got the respomse that all the stories had been processed, so I used a new model: groq/openai/gpt-oss-120b. 
This worked, but. I noticed it updated the figures weirdly in the terminal. When I tried the first 10, I was getting responses that looked like this:
    Processing story 7/10: Never plug these into power strip...
      Skipped: Not focused on Eastern Shore
    Processing story 9/10: WHAT A NIGHT! - Storms cause damage, flooding in Mid-Shore r...
    Processing story 11/10: Police investigating Easton homicide...
    Processing story 13/10: Cambridge theater has another incident of smoke in theater...
    Processing story 15/10: Dispute over girlfriend led to shooting, police say - Suspec...
    Processing story 17/10: Fire group raising $5 million for training center...
    Processing story 19/10: St. Michaels reorganizes police, OKs raises...
For some weird reason, it was arranging the stories by odd numbers alone, and even returning values with numbers above ten. Copilot said this was because I had set my script to save responses as they are generated and only continue from where they stopped. When I compared the stories in the output file with those in the input one, they were accurate. So while the terminal showed the stories in odd numbers, they were being processed as: story 1, story 2, story 3...
When the model had process about a hundred stories, we began the rate limit crawl. Because it was a new day and rate limits would have been reset, I decided to test if the progress I had made was actually being saved by switching to a different model. I interrupted the process and swtiched to groq/meta-llama/llama-4-maverick-17b-128e-instruct
It did not start afresh. I had 114 stories processed at this time (what was showing in the terminal was 229/300 because it was skipping even numbers). When I started afresh with the new model, It told me just that:
    Found 114 already processed stories. Resuming...
    Randomly selected 300 stories from the total available
    Processing 186 remaining stories (out of 300 total) with model groq/meta-llama/llama-4-maverick-17b-128e-instruct...
    Processing story 115/300: Cambridge man found guilty of child abuse, assault...
    Processing story 117/300: Tilghman man sentenced to five years for sexual abuse of a c...
So for v4, I used two models. If using two models for one task will not be a problem, I would like to include this to all my prompts going forward, so that I dont have to start afresh if something interrupts progress in the terminal.
The Llama model faster this time I guess because the limit had reset. At the end of the process, this model skipped just 13 stories, which I foound a little surprising, because the other one skipped 23.
Since stories_with_entities_v2.json did not have up to 300 stories, I decided to load only stories_with_entities_v1.json and stories_with_entities_v4.json to Datsette.



...

What prompt elements had the biggest impact on quality?
The skipped ome for the output but for the process, def the one where I said, save my work one after another.
- Did adding examples help? What kind of examples worked best?
yes: examples of stories to be skipped [Art around the world] and skipped.
- How specific should instructions be? Very much so, but more importantly, they are more effective if they are tailored to initial unfavourable results.
- What caused the LLM to make mistakes? 




Model used for v2: 
uv run python new_entities.py --model groq/meta-llama/llama-4-maverick-17b-128e-instruct --input arts_culture_stories.json --limit 5
[Llama is too slow. Had to leave.]

Model for v1:
uv run python new_entities.py --model groq/moonshotai/kimi-k2-instruct-0905 --input arts_culture_stories.json --limit 5



# Weird number but not missing stories.

### Next attempt, ask the LLM for stories a reporter can cover based on the metadata.

At some point, Mid-Shore Calendar stories refused to get processed. They would be on the queue for 10-15 mins before returning:
Error processing story 406: LLM CLI failed: Error: Error code: 429 - {'error': {'message': 'Rate limit reached for model `meta-llama/llama-4-maverick-17b-128e-instruct` in organization `org_01j97v25gpen6b0r150s7exhsm` service tier `on_demand` on tokens per day (TPD): Limit 500000, Used 498729, Requested 5289. Please try again in 11m34.3104s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

### Prompt 1
# My pormpt to copilot:
Rewrite the script so it saves output to stories_with_entities_v1.json and with the prompt still in a variable format, update it so that it skips processing for stories that are not situated in Eastern Shore. Examples of stories to skip are those like ART AROUND THE WORLD if they are not talking of Art in Eastern Shore.
Instead of returning any values  for names, places and organizations for the stories that have no geographical focus in Eastern Shore, update the prompt so that the the only values in the list for these stories says SKIPPED Remember to keep the prompt in a variable format.
Update the script to recall that stories outside Eastern Shore should only return a list that says [SKIPPED]

# Copilot's prompt in script:
PROMPT_TEMPLATE = """Extract all PEOPLE, PLACES, and ORGANIZATIONS mentioned in the following news story.

VERY IMPORTANT:
- FIRST, determine if this story's primary geographic focus is Maryland's Eastern Shore.
- If the story is primarily about events, people, or activities OUTSIDE the Eastern Shore (e.g., international news, national news, "Art Around the World" features not focused on Eastern Shore), return: {{"title": "{title}", "people": ["SKIPPED"], "places": ["SKIPPED"], "organizations": ["SKIPPED"]}}
- Only process stories that are primarily about Maryland's Eastern Shore communities, people, and organizations.
- Examples of stories to SKIP: international art features, national entertainment news, global cultural events unless they directly involve Eastern Shore residents or organizations.
- Ignore the "Star Democrat, The (Easton, MD)" publication credit - this does not mean the story is about the Eastern Shore.

If the story IS about the Eastern Shore:
- Return EXACTLY one JSON OBJECT and NOTHING ELSE (no preface, no explanation, no markdown).
- The object must have exactly these keys: "title", "people", "places", "organizations".
- Each value for people/places/organizations must be an array of strings. If none, return an empty array [].
- Normalize entity strings: trim whitespace, remove surrounding punctuation, do not include titles (Mr., Ms., Dr.) or role labels — return only the name/place/organization string.
- Prefer full names when available. Do NOT return placeholders like "Jane Doe" or "John Doe".
- Exclude "Star Democrat", "Chesapeake Publishing Group", "Adams Publishing/APGMedia", "Invision/AP" from organizations.

# Prompt 2
# My prompt to Copilot:


# Prompt 3
Update the script to save the output to stories_with_entities_v3.json and remember to return SKIPPED for stories with no geographical focus on Eastern Shore. Let the results be saved to the output json after each story is processed. Bear in mind that  I want to be able to:
Stop it anytime without losing progress
Resume from where it left off
Have a partial file even if it never completes
# Copilot's prompt in script:

[Copilot's prompt stayed the same in most cases. the change were more obvious in the rest of the code]