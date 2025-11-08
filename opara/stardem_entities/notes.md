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
I figured it might have been from the way I asked codespaces to structure, so I asked it to recreate the structure.



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