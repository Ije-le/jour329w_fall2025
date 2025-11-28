# Beatbook draft II  
# 11/21/2025
In refining my first draft, I generated a prompt using copilot that included a brief introduction at the beginning. The prompt also updated the existing beatbook by including some sort of directory toward the end that had all the sources cited throughout the beatbook, their relevance /important stories they had featured in, and if possible contact information. The model returned contact information that mostly proved to be made up, especially the emails, since I couldn't trace any of them in the original public_safety_stories.json or in the first beatbook draft, so I refined the prompt to exclude contact information, and saved this version as prototype_v3
The most significant problem with the beatbook was the repeatition of issues throughout the document,
First I tried to address this by having copilot update the prompt to briefly summarize those same issues every time that thehy came up after the first mention.
This was not as effective as I had hoped in the first two tries. The summaries did not give enough information in sections under which they were summarized.
So I created a new section above the source directory and saved as prototype_v4.
I had the model label the new section 'Interconnected Issues' and list out all the repetitive issues in the beatbook.
I also asked the model to indicate the overlapping sections usder each issue, for better understanding.
Doing this helped, but I noticed that since there were different interconnected issues, a reporter might be unsure which of them to look at per time. for instance:
**Protest‑permit policy**, sparked by the “No Kings” demonstrations and the ensuing Easton town‑council debate over a three‑day advance permit requirement (see Interconnected Issues)
The directive above gives some information, but one might not be sure which interconnected issues to focus on. So we updated it agaian to this:
**Protest‑permit policy** – The “No Kings” protests (June 2025) sparked a town‑council debate in Easton and Cambridge about whether a formal permit is required for any large gathering (see Interconnected Issue #3).  
Numbering the interconnected issues helped with identification.

Though this took care of the redundancy in the initial draft and produced what I think is a better copy, I suspect that going back and forth between sections to read interconnected issues when necessary might also pose another issue. But I think this is a much betetr alternative to reading the same thing over and over.





## BEATBOOK DRAFT III           11/27/2025
## GEOGRAPHIC FOCUS
The beatbook_generator.py or the new API key or both made the beatbook generation very seemless.
I made Talbot as my geographical focus after giving copilot my previous beatbook draft and asking it to list possible geographical areas we could focus on with reasons. Copilot suggested a long list of reasons to focus on Talbot county, but the reason I found interesting was that there is a stronger concentration of public safety stories on the location.

The first beatbook, talbot_beatbook.md, was mostly structured in a tabular format.
The Executive Summary provided infromation which could help a new reporter understand what happens where and why. Examples of the themes commonly covered under this beat were provided and broken down to show frequency and relevance to the beat, and it also showed areas where such issues commonly occur.
But what I think was most helpful in understanding geography is the grographic analysis section. This section improved upon the executive summary to include distinctive issues relevant to the individual communities. It also frequesncy of multi-jurisdictional calls for these issues and areas.
One other thing I found quite informative is the thematic section. It pulls out examples of stories already reported by the Star Democrat on specific themes and locations. Other information provided in this section include the story headline and a quote from each story. I think it would have helped more if the quotes were replaced with links to the actual stories. Links would give a new reporter the option to explore the entire story and get more understanding of the topics than quotes can provide.
I also liked that most sections had key takeaways highlighted for reporters. The interconnected issues section also not only provides relevant information on how stories are related, but also gives guidance on how to explore them. AT first instance, I thought of the source directory as a great addition, because there were not a lot of names throughout the book. But the source directory functioned like a compilation of all the stoires mentioned rather than human sources.
I think this draft would be very useful as a guide, but it could work better if:
-The "How to use" section could have been expanded a bit to include more tips;
-The document could have had a section dedicated to unresolved stories that reporters can follow up on. A few such stories were cited in the document, but there could be more emphasis on that;
-Links could have been included instead of quotes under thematic sections.
-Human sources could have been included in source directory.
So in updating the prompt for my second beat book, I put these points into consideration.
While the format works fine, I opted for the narrative style for my second version, just because I personally would prefer a narrative beatbook. I like the source directory, so I asked Copilot to edit the beatbook_generator so that it retains the directory while changing the format.

The introduction to the second beat book was conversational and seemed more engaging compared to the tables that confronted me in the first draft, but that might just be my bias kicking in. The "How to Use" section came at the beginning, which I think works better for structure than the previous draft where it was located at the bottom. The Executive Summary broke down topics covered and provided some context that showed newsroom interests and possible trends of events in communities.
I particularly like this part of the intro:

Using the unresolved‑stories section
When you open a story that ties to an unresolved item, start with the brief in Section 6 to see what questions remain. Then pull the original article from the Source Directory, re‑read the quoted officials, and reach out to the contacts listed in the relevant thematic or geographic section. Most unresolved stories have at least two agencies still involved, so you’ll often have a “dual‑source” angle—perfect for an exclusive update.

The hitch here is that the unresolved stories section only had story headlines and not links, so it is not exactly possible for a reporter to pull the original article from the source directory. They have to go source for the links themsleves. Regardless, the guide shows how to optimally utilize the book in that regard, which I like.
This beat book was broadly broken down in two sections: thematic issues and geographic analysis. 
For each section and subsection, all the stories referenced were listed out with one-sentence descriptions of the story. The representative stories were captured in tables, which works even for a narrative document.
Although focused on the themes covered, the thematic section still produced content that revolved around geography. For example, while highlighting violent crimes and homicide as a recurring theme in Star Democrat's coverage, a part of the beat book reads:
    "Property crimes in Talbot County often surface in the quieter corners of the county—rural farmsteads, small‑town storefronts, and the ever‑busy US‑50 corridor," showing a new reporter how this issue is connected to certain locations. The geographical analysis was more robust than the frist draft, containing more information on locations meantioned, and including classifications like "Rural Areas & the Wilder Mid-Shore."
One thing I did not like about this book is that the source directory again had no names, only Date, Headline, Primary Location and Brief Description. I missed including this in my previous prompt which explains why it stayed the same across both versions. Also, there many instances where links to the stories could have been helpful, example: the representative stories and the unresolved stories sections.

In generating a third draft, I specifically highlighted the relevance of links in my prompt, but the links returned in this draft were not real links. The third Beat Book was very similar to Beat Book 2, and since the links did not work, I double checked to be sure that the links in my source json file are correct. Turns out the json file had no links at all, which explained the problem, so I wrote another prompt for version 4 asking it to take out the fake links. Here, I also decided to add my non-story information.
The information I felt could be useful in covering this beat outside stories is the census data, which can give information on the demographics of the county that may not ordinarily be deduced from the beatbook or be common knowledge, especially if the reporter is also new in the county or state. I decided to include this information to this draft, and asked Copilot to help me fetch the link for Talbot county from the census.gov website.
Copilot's link to the census website displayed a message suggesting that it is undergoing maintenance:
    QuickFacts is currently undergoing a maintenance cycle. Please check back later.
I checked manually to be sure this was accurate and it was, but only for the Quick Facts section of the website. There were other ways to get the information without using quick facts, so I copied the link to Talbot county's population and other information. I gave it to Copilot to generate a summary with key statistics, and include this in the script so that it can be used where necessary in generating the beatbook.

I like the fourth beatbook better.
In the introduction, it reflects that the county's aging population along with some other issues contribute to safety pressures that are present in the newsroom's coverage. It also included a functional link to the census website where reporters could check for some more information on population, community characteristics, etc. I liked that.
The Executive Summary showed the influence of the demographic information I included, emphasising issues like median age. Although this book seemed to have a similar tone with version 2, it was clear that its focus had shifted a bit. The Executive Summary in version_2 highlighted locations and their relevance to issues being discussed. The new book seemed to drift slightly from that, considering other factors like age which seemed to reduce its attention to location. Still, this beatbook was more detailed in describing issues. For instance the Thematic Section here highlights a gas station shooting that hadn't been mentioned in the previous three. There was also the mention of a wave of vacation-rental burglaries in Oxford and St. Michael's, and though one of the previous beat books mentioned a rise in burglaries, it does not point to it's relation to the summer vacations.
Another interesting influence of the census data on this beat book can be seen under violent crime and homicide.
The book points out that the county's demographic composition of older residents  means that many victims of gun-related incidents are older adults. I'm not sure how this information should be processed by a reporter, because this also should mean that many perpetrators of the incident would be older adults too, but it doesn't say that anywhere in the book.
The geograghical analysis was informative as with the other versions, though this included details like population density.
Finally this version had no fake links in the source directory, and one column was added to include key contacts on the beat.
I think this would be a helpful guide for a new reporter on this beat.



