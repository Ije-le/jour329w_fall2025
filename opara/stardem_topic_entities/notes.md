11-10-2025      Star-Dem Topic Entities
I chose the topic: Arts_Culture because I was interested in knowing what stories were eeventually classified under this topic, since I wasn't sure how to differentiate it from Community Events.
I initially meant to remove stories on ART AROUND THE WORLD because they are not local enough, but I found there was only one story like that anyway, so I left it.

Modify the 'add_entities.py' script to extract metadata from the arts_culture_stories.json file, bearing in mind that all the stories in the json file are on the same topic. Let the script extract all the names of people, places and organizations into arrays. Let the json file have this structure:
title: Musuem of Eastern Shore Life to be open during QA Fair
people: Gabriela Montero, Jeniffer Pfeffer.
places: Maritime museum, Easton, Dorchester
Organizations: Bay Country Chorus, Kent Island Federation of Art
Alter the script to test with ten stories first. Save the output to 
stories_with_entities_v1.json
Use 
