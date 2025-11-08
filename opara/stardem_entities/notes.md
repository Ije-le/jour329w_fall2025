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