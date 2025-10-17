Baltimore Beat  10/13/2025

My topic: Baltimore
No of stories: 64.

Metadata
**Required Fields (all beats should have these):**
- **people**: Array of key people mentioned (names only)
- **geographic_focus**: Primary location (county, city, region, or "statewide")
- **key_institutions**: Organizations, agencies, companies involved
- **race**: (black, white, hispanic etc)

1. Elijah Cummings is a name that appears most frequently.

2. "Baltimore City" got the most coverage.

3. The Department of Transportation appeared the most (16 times), followed by the Department of Justice (11 times). This was distantly followed by Fundación Janet Arce (2 times).

It does make sense that Baltimore City will appear more than any other area, given that I worked with the Baltimore beat.  Cummings is a U.S. Congressman from Baltiimore, so it is not surprising that he got more coverage than others. I dont really have much explanation for why the Department of Transportation appears that much, though I suspect it might have something to do with the Key Bridge.

One thing I would take out of the metadata.py script is the column for race. I added it because a few stories I clicked on in the Baltimore json file directed me to DEI coincidentally, so I thought there might be race-related coverage. But out of 64 rows returned, I only got back leass than 10 lists containing any race.
Most of the other rows returned empty lists, so I do not need the race data. There were also some empty lists under the key institutions , but not nearly as much as the race column.



BEAT BOOK EVALUATION
The result I got in the prototype.md document was quite scanty, compared to what I thought I would get back, considering that I was working with 64 stories. I think it might be something with my prompt. I am not sure what it is, but I think I might not have alluded to the json file correctly, I'm not sure, and I'm happy to go back and fix things up if this is the case.

However, I still think that the data Claude returned was reasonably useful for a reporter who is covering the Baltimore beat for the first time.
I liked that the city overview revealed the diversity of Baltimore's population and the economic disparities. A person new to this beat might want to know these. I also like the attempt to highlight recent significant events under the beat, because this can give a fresh reporter and angle to start sourcing for stories from, or what stories would be relevant. But the results could have been a little more recent. For example, one recent significant event listed in the prototype is the Francis Scott Key Bridge collapse, meanwhile there is sa more recent development: the Key Bridge rebuild.
I think something else this prototype could have done better is let the reporter know if the information it's giving is about Baltimore city or the county. I can tell this is about the city because it uses the word "city" in its descriptions, but I think it would have been nice to actually point that out.

Given more time, what I would have done better is to include in my prompt soecific information I wanted to see in the beat book. I realized almosst when I was done with the process that this could have been quite useful.


QUESTIION:
I thought that by taking the race metadata out of the add_metadata.py document, I would be able to remove it from datasette, but when I did this and ran datasette again, but I got the same thing I had before, what could be wrong?