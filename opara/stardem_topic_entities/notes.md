11-10-2025      Star-Dem Topic Entities
I chose the topic: Arts_Culture because I was interested in knowing what stories were eeventually classified under this topic, since I wasn't sure how to differentiate it from Community Events.
I initially meant to remove stories on ART AROUND THE WORLD because they are not local enough, but they didn;t seem that many, so I left them.

Since my code just refused to work no matter what I did, I totally dumped the initial add_entities.py script and created another: new_entities.py. I wrote the script afresh in it, tries it out with 10 stories and it worked. So I tried it out with the entire script.

```uv run python add_entities.py --model groq/meta-llama/llama-4-maverick-17b-128e-instruct --input arts_culture_stories.json```


 
 I used the groq/meta-llama/llama-4-maverick-17b-128e-instruct model for the first trial.
Since my code just refused to work no matter what I did, I totally dumped the initial add_entities.py script and created another: new_entities.py. I wrote the script afresh in it, tries it out with 10 stories and it worked. So I tried it out with the entire script. First version cut off at the 257th story due to what I suspect to be issues with my internet. I'm not sure why that got saved to logs rather than a json file. I also couldnt load it to Datasette, so I started the process again.




### Prompt
Rewrite the 'add_entities.py' script to extract metadata from the arts_culture_stories.json file, bearing in mind that all the stories in the json file are on the same topic. Let the script extract all the names of people, places and organizations into arrays. Let the json file have this structure:
title: Musuem of Eastern Shore Life to be open during QA Fair
people: Gabriela Montero, Jeniffer Pfeffer.
places: Maritime museum, Easton, Dorchester
Organizations: Bay Country Chorus, Kent Island Federation of Art
DO NOT USE EXAMPLES LIKE "JANE DOE","JOHN DOE"
Alter the script to test with ten stories first. Save the output to 
stories_with_entities_v1.json

### Second prompt
Write me a new script 'new_entities.py' to extract metadata from the arts_culture_stories.json file, bearing in mind that all the stories in the json file are on the same topic. Let the script extract all the names of people, places and organizations into arrays. Let the json file have this structure:
title: Musuem of Eastern Shore Life to be open during QA Fair
people: Gabriela Montero, Jeniffer Pfeffer.
places: Maritime museum, Easton, Dorchester
Organizations: Bay Country Chorus, Kent Island Federation of Art
DO NOT USE EXAMPLES LIKE "JANE DOE","JOHN DOE"
Write the script to test with ten stories first. Set model to : groq/meta-llama/llama-4-maverick-17b-128e-instruct and call it using llm. You only need to do this once. Refer to this link to properly call in llm: https://llm.datasette.io/en/stable/usage.html Save the output to 
stories_with_entities_v1.json 

### Third
Update the new_entities.py to meet these requirements:
Extracts data from the arts_culture_stories.json file, extracts all names of people, places and organizations into arrays, allows the output json file have this structure: the json file have this structure:
title: Musuem of Eastern Shore Life to be open during QA Fair
people: Gabriela Montero, Jeniffer Pfeffer.
places: Maritime museum, Easton, Dorchester
Organizations: Bay Country Chorus, Kent Island Federation of Art, DOES NOT USE EXAMPLES LIKE "JANE DOE","JOHN DOE", DOES NOT TEST STORIES FIRST. LET IT RUN THE FULL FILE, sets model to : groq/meta-llama/llama-4-maverick-17b-128e-instruct and calls it using llm, only calls llm once, refers to this link to properly call in llm: https://llm.datasette.io/en/stable/usage.html and saves the output to 
stories_with_entities_v2.json 

### Chat with Copilot

Using this groq model: groq/meta-llama/llama-4-maverick-17b-128e-instruct modify the add_entities.py script. From the stardem_sample.json file, let the script extract people, places and organizations into arrays.
People in this context means every person mention in the json file. Places means every place mentioned in the json file. Organization means every organization mentioned in the json file. Here are two examples each of people, places and organization are as follows:
people: David Breimhurst, Kristen Greenaway. places: Denton, Kennard African American Cultural Heritage. organizations: National Down Syndrome Society, Dorchester County Emergency Medical Services. Change the output file to 'stories_with_entities_second.json' and save it to the output file. The json output should have this structure:
story number:
  - 1
headline:
  - Jane Doe visits Biden
people:
  - David Breimhurst, Kristen Greenaway
places:
  - Denton, Kennard African American Cultural Heritage
organizations:
  - National Down Syndrome Society, Dorchester County Emergency Medical Services
Remember to change the model used to run the script to: groq/meta-llama/llama-4-maverick-17b-128e-instruct
Remove DEFAULT_MODEL from the script and call llm using uv run. Do this just once.


