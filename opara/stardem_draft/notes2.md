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



## GEOGRAPHIC FOCUS
The beatbook_generator.py or the new API key or both made the beatbook generation very seemless.
I made Talbot as my geographical focus after giving copilot my previous beatbook draft and [asking copilot to list possible geographical areas we could focus on witih reasons.] Copilot suggested a long list of reasons to focus on Talbot county, but what I found interesting was that there was a strong concenttration of public safety stories on the location [more than anywhere else in the doc? verify]

The first beatbook, talbot_beatbook.md, began with a table, and as a reporter I do not think that I would like a table to be the first thing I come across in a beatbook. The entire document was mostly tabular, so I made a note to change the variation in my next draft.
But what I liked was the geographical focus section. The information there was such that a new beat reporter understabds what happens where and why.
The thematic section is also very informative, but I would have preferred if links were attached rather than just quotes. Links give the reporters the option to explore the entire story and get further information on the topics more than quotes can.
Given our focus on geography, I'd say the most useful part of this document is the geographic analysis.[The distinctive issues part makees it clear the type of stories the area generates/the newsroom is interested in]
Also providing interpretation for reporters in cases that might be complex to follow is great.
Interconnected issues also not only provides information but gives guidance on how to weave interconnected stories.
The source directory list is very good, because [names were not really listed above because of format?]
How to use, might be expanded a little more.
I love!
Only that I fee format can be changed.





Things to change in next draft:
More narrative
Less tables
Links in addtion/instead of quote in thematic sections




 $ uv run python beatbook_generator.py source_stories.json -m groq/openai/gpt-oss-120b -t "Talbot County Public Safety" -o talbot_beatbook.md