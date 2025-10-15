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
