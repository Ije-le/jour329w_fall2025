11-10-2025      Star-Dem Topic Entities
I chose the topic: Arts_Culture because I was interested in knowing what stories were eeventually classified under this topic, since I wasn't sure how to differentiate it from Community Events.
I initially meant to remove stories on ART AROUND THE WORLD because they are not local enough, but they didn;t seem that many, so I left them.

### NOTE: Since my code just refused to work no matter what I did, I totally dumped the initial add_entities.py script and created another: new_entities.py. I wrote the script afresh in it, tries it out with 10 stories and it worked. So I tried it out with the entire script.

```uv run python add_entities.py --model groq/meta-llama/llama-4-maverick-17b-128e-instruct --input arts_culture_stories.json```


 
 I used the groq/meta-llama/llama-4-maverick-17b-128e-instruct model for the first trial.
### Prompt
Rewrite the 'add_entities.py' script to extract metadata from the arts_culture_stories.json file, bearing in mind that all the stories in the json file are on the same topic. Let the script extract all the names of people, places and organizations into arrays. Let the json file have this structure:
title: Musuem of Eastern Shore Life to be open during QA Fair
people: Gabriela Montero, Jeniffer Pfeffer.
places: Maritime museum, Easton, Dorchester
Organizations: Bay Country Chorus, Kent Island Federation of Art
DO NOT USE EXAMPLES LIKE "JANE DOE","JOHN DOE"
Alter the script to test with ten stories first. Save the output to 
stories_with_entities_v1.json

Write me a new script 'new_entities.py' to extract metadata from the arts_culture_stories.json file, bearing in mind that all the stories in the json file are on the same topic. Let the script extract all the names of people, places and organizations into arrays. Let the json file have this structure:
title: Musuem of Eastern Shore Life to be open during QA Fair
people: Gabriela Montero, Jeniffer Pfeffer.
places: Maritime museum, Easton, Dorchester
Organizations: Bay Country Chorus, Kent Island Federation of Art
DO NOT USE EXAMPLES LIKE "JANE DOE","JOHN DOE"
Write the script to test with ten stories first. Set model to : groq/meta-llama/llama-4-maverick-17b-128e-instruct and call it using llm. You only need to do this once. Refer to this link to properly call in llm: https://llm.datasette.io/en/stable/usage.html Save the output to 
stories_with_entities_v1.json 
