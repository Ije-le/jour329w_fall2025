### Star-Democrat Topic Classification  11/1/2025

I chose to select the topics myself, becauase the previous attempt at getting LLMs to choose topics was a much longer process.
Here is my topic list:
Education, Health, Police & Crime, Local Government, Judiciary, Public Safety, Election, Chesapeake, Food, Community Events & Culture, Movies & Shows, Sports, Religion, Obituaries, Other

### Github copilot conversation
# My prompt: 
Write me a python script called classify_topics.py that reads stardem_sample.json. For each story in the json file, add a single 'topic' field.The script should send a prompt to the LLM to assign exactly one topic from this list: [Education, Health, Police & Crime, Local government, Judiciary, Public Safety, Election, Chesapeake, Food, Community Events & Culture, Movies & Shows, Sports, Religion, Obituaries, Other ]. Then save the results to a new JSON file called stardem_topics_classified.json`. Use Python’s subprocess module to call the LLM. Let the script also use the Anthropic model Claude Sonnet 4.5 and print progress as it processes stories. Use this document as reference: ‘stardem_topics.md’

# Response: 
I'll add a short todo list for this task then create assignments/stardem_topics/classify_topics.py that calls the llm CLI (using Anthropic Claude Sonnet 4.5) via subprocess and writes stardem_topics_classified.json. The script will try both uv run llm and llm command forms and validate the returned topic against the allowed list. Expected outcome: the new script is created and ready to run in Codespaces.

Starting (1/3) Create classify_topics.py

Created
classify_topics.py

Done — I created classify_topics.py and added a todo list entry.

How to run it in Codespaces (from the new script's directory):

Open a terminal and change to the script directory:

Run the script (prefer using uv run if you use the uv wrapper, otherwise run directly):
v run python classify_topics.py
# or
python classify_topics.py

Notes and tips:

The script expects stardem_sample.json to be in the same directory.
It tries several llm CLI invocation patterns and targets the Anthropic model anthropic/claude-sonnet-4.5. If your llm CLI uses a slightly different model name or flags, adjust the LLM_CANDIDATES list near the top of the script.
The script will print progress for each story and save results to stardem_topics_classified.json.
If the llm command is not available in the environment, the script will raise an error telling you how to fix it.
If you want, I can:

Run the script here (if you want me to attempt it), or
Modify the script to use a direct HTTP API call (Anthropic/OpenAI) instead of the llm CLI (you'd need to provide API keys), or
Make the model name and CLI flags configurable via command-line arguments. Which would you prefer?
