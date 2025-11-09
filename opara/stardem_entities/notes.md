StarDem_Entities        11/5/2025

 ## Prompt:
 Using this groq model: groq/moonshotai/kimi-k2-instruct-0905 modify the add_entities.py script. From the stardem_sample.json file, let the script extract people, places and organizations into arrays.
People in this context means every person mention in the json file. Places means every place mentioned in the json file. Organization means every organization mentioned in the json file. Here are two examples each of people, places and organization are as follows:
people: David Breimhurst, Kristen Greenaway. places: Denton, Kennard African American Cultural Heritage. organizations: National Down Syndrome Society, Dorchester County Emergency Medical Services. Change the output file to 'stories_with_entities.json' and save it to the output file. The json output should have this structure:
[
    {
        "story_number": 1,
    "headline": "Band members selected for party",
    "people": ["David Breimhurst", "Jane Smith"],
    "places": ["Denton", "Easton"],
    "organizations": ["Medical Services", "County Emergency Medical Services"]
    }
]
Remember to change the model used to run the script to: groq/moonshotai/kimi-k2-instruct-0905

My first attempt at getting entities returned a json file with empty lists. The error I got back in the terminal said something like this: 
## File "/workspaces/jour329w_fall2025/opara/stardem_entities/add_entities.py", line 24, in extract_entities
 ##   Output: {"people": ["Jane Doe"], "places": [], "organizations": ["City Council"]}
 ##           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
## ValueError: Invalid format specifier ' ["Jane Doe"], "places": [], "organizations": ["City Council"]' for object of type 'str'
I figured it might have been from the way I asked codespaces to structure, so I asked it to recreate the structure. So I edited the prompt to this:
Using this groq model: groq/moonshotai/kimi-k2-instruct-0905 modify the add_entities.py script. From the stardem_sample.json file, let the script extract people, places and organizations into arrays.
People in this context means every person mention in the json file. Places means every place mentioned in the json file. Organization means every organization mentioned in the json file. Here are two examples each of people, places and organization are as follows:
people: David Breimhurst, Kristen Greenaway. places: Denton, Kennard African American Cultural Heritage. organizations: National Down Syndrome Society, Dorchester County Emergency Medical Services. Change the output file to 'stories_with_entities.json' and save it to the output file. The json output should have this structure:
story number:
  - 1
headline:
  - Jane Doe visits Biden
people:
  - Jane Doe, David Breimhurst
places:
  - Washington, Easton
organizations:
  - City Council, Medical Center
Remember to change the model used to run the script to: groq/moonshotai/kimi-k2-instruct-0905
Remove DEFAULT_MODEL from the script and call llm using uv run. Do this just once.

This returned values only for headlines, but after further trial, copilot created a new file: stories_with_entities_recovered.json. This one had some of the metadata I needed, but there were a good number of stories did not have any information. Some names also had weird values like  "1.5 million Gazans."

To get a third script, I changed the prompt and the model, asking only for names 'prominently featured in the stories:

Using this groq model: groq/meta-llama/llama-4-maverick-17b-128e-instruct modify the add_entities.py script. From the stardem_sample.json file, let the script extract people, places and organizations into arrays.
People in this context means every person mention in the json file. Places means every place mentioned in the json file. Organization means every organization mentioned in the json file. Only return values for people prominently featured in the stories. Here are two examples each of people, places and organization are as follows:
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
After two tries, it returned a single empty list. After a little bit of back and forth, it populated the stories_with_entities_second.json with metadata.

# stories_with_entities_recovered vs. stories_with_entities_second
Because I made the mistake of loading the empty json file to Datasette at first, the stories_with_entities_recovered document returned 400 instead of 200 rows in Datasette.
The json file did have some names of sources, places, organizations. But there were empty lists in so many columns. It also did not look accurate because most of the stories did not have ALL the entities in them. Maybe I should have said ALL in my prompt, but what seemed very concerning was that the metadata in some cases seemed like they were pulled out from somewhere other than the story. For instance, story 27 (227 in Datasette) had this headline: Two candidates run for Oxford commission seats. The metadata generated for it included no names, even though the names of the candidates were mentioned. It also listed places like Gaza Strip, Israel, and Rafah, and Israel Defence Forces as organizations, but when I read the story, I found no mention of these places.
The story on Matt Blanc had Jane Doe, John Smith as names which were very weird and totalaly did not appear in that story. other metadata it suggested which were not anywhere in the story are: New York and Berlin as places and United Nations and TechCorp as places.
The stories_with_entities_second was not much different. I traced the same stories in this json file using Datasette, and the results were the same. I suspect copilot copied one file into the other. While trying to generate the stories_with_entities_second json file, I saw that copilot had suggested doing this when it was takin too long to generate the file. I told it not to, but looking at both documents, I think it went ahead to do that.