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
The Executive Summary provided infromation which could help a new reporter understand what happens where and why. Examples of the themes commonly covered under this beat were provided and broken down to show frequency and relevance to the beat, but it also showed areas where such issues commonly occur.
But what I think was most helpful in understanding geography is the grographic analysis section. This section improved upon the executive summary to include distinctive issues relevant to the individual communities. It also frequesncy of multi-jurisdictional calls for these issues and areas.
One other thing I found quite informative is the thematic section. It pulls out examples of stories already reported by the Star Democrat on specific themes and locations. Other information provided in this section include the story headline and a quote from each story. I think it would have helped more if the quotes were replaced with links to the actual stories. Links would give a new reporter the option to explore the entire story and get more understanding of the topics than quotes can provide.
I also liked that most sections had key takeaways highlighted for reporters. The interconnected issues section also not only provides relevant information on how stories are related, but also gives guidance on how to explore them. I found the source directory to be a great addition, because there were not a lot of names throughout the book.
I think this draft would be very useful as a guide, but it could work better if:
-The "How to use" section could have been expanded a bit to include more tips;
-The document could have had a section dedicated to unresolved stories that reporters can follow up on. A few such stories were cited in the document, but there could be more emphasis on that;
-Links could have been included instead of quotes under thematic sections.

So in updating the prompt for my second beat book, I put these points into consideration.
While the format works fine, I opted for the narrative style for my second version, just because I personally would prefer a narrative beatbook. I like the source directory, so I asked Copilot to edit the beatbook_generator to retain that while changing the format.

The introduction to the second beat book was very conversational and seemed more engaging compared to the table that confronted me in the first draft, but that might just be my bias kicking in. The Executive Summary broke down topics covered in order of frequency and provided some context, which not only shows newsroom interests, but possible trends in communities.
This beat book was broadly broken down in two sections: thematic issues and geographic analysis. For each section [all the stories referenced were listed out with links? which i REALLY LIKED.]


Although focused on the themes covered, the thematic section still produced content that revolved around geography. For example, while highlighting violent crimes and homicide as a recurring theme in Star Democrat's coverage, a part of the beat book reads: "Cambridge, just a 15‑minute drive east, has become a flashpoint for the county’s homicide docket," showing a new reporter how this issue is connected to a location. The geographical analysis was more robudt that the frist draft, containing more information on locations meantioned, and including classifications like "rural Talbot."
It also included an unresolved stories section, which cited stories that had been published in these areas but initially did not come with links. After updating this version by generating another beat book that overwrote it, [links were included] 


[Compare How to sections. Which has  more releavant info beyond tone?]

What I could add should be added to third draft.





 $ uv run python beatbook_generator.py source_stories.json -m groq/openai/gpt-oss-120b -t "Talbot County Public Safety" -o talbot_beatbook.md

uv run python beatbook_generator.py source_stories.json -m groq/openai/gpt-oss-120b -t "Talbot County Public Safety"
