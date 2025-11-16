
### NOTE FOR ASSIGNMENT
## Have copilot strip out everything in tags if you use qwen

Model used for first exercise: 
uv run python new_entities.py --model groq/meta-llama/llama-4-maverick-17b-128e-instruct --input arts_culture_stories.json --limit 5
[Llama is too slow. Had to leave.]

Model for second:
uv run python new_entities.py --model groq/moonshotai/kimi-k2-instruct-0905 --input arts_culture_stories.json --limit 5


Copilot began to return this in the terminal when I gave express examples of the kinds of stories to skip:
Processing 10 stories one at a time with model groq/meta-llama/llama-4-maverick-17b-128e-instruct...
Processing story 1/10: Festival attracts bluegrass faithful in Ridgely...
Processing story 2/10: Musuem of Eastern Shore Life to be open during QA Fair...
Processing story 3/10: ART AROUND THE WORLD...
  Skipped: Not focused on Eastern Shore
Processing story 4/10: JOHNNY DEPP SELF-PORTRAIT...
  Skipped: Not focused on Eastern Shore

But even when it said "Skipped" on the timeline, it often returned values for the stories. Since it insisted on returning values, I asked Copilot to update the prompt to return "SKIPPED" in the list. That worked finally. So sllllooowww!

### Next attempt, ask the LLM for stories a reporter can cover based on the metadata.

At some point, Mid-Shore Calendar stories refused to get processed. They would be on the queue for 10-15 mins before returning:
Error processing story 406: LLM CLI failed: Error: Error code: 429 - {'error': {'message': 'Rate limit reached for model `meta-llama/llama-4-maverick-17b-128e-instruct` in organization `org_01j97v25gpen6b0r150s7exhsm` service tier `on_demand` on tokens per day (TPD): Limit 500000, Used 498729, Requested 5289. Please try again in 11m34.3104s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}

### Script 1