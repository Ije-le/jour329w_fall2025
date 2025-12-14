# 12/14/2025
Before creating the guide book, I asked Copilot to generate a script with which I could create the book.
I ran into some issues because the combined.txt had too much information and was above the context window for the model I used: groq/openai/gpt-oss-120b
So I tried it with claude-3.5-sonnet. I also told Copilot to process it in batches, like we did for the main beatbook.

The first draft of the guide book I generated was modtly in a tabular form, which was not really bad, it just looked like there were too many tables.
It had language that I felt would be a tiny bit technical for someone trying to create a beatbook for the first time.
It also was quite repetitive: we had part 1, 2, 3 all about the same process, only a little differently.
There were at least four different sections talking about the beatbook creation process. Then there were two prompt libraries in the guide, and I was not sure what they were needed for, if for the finished beatbook or for the process. I asked Copilot and it said the repetition was because I asked the model to generate the guide in batches.  So I asked Copilot to clean the current version and save it to guide_notes_v2.md.
I also asked that the language be further simplified since we are making it for new users.

I liked this version better.
It was quite straightforward, more simplifed and had no unnecessary repetitions. It also wrote out some of the required scripts, which I think is really great for someone trying this out on their own.

Another thing I like about the guide is that toward the end, there was a troubleshooting section where responses like "API rate limit exceeded" were listed and explained. THis section provided possible solutions should a reader run into these problems.
There was also a version for creators who would like to update their beatbook regularly and how they could go about it and I find that section very useful.

I felt it could use some more details, but I reasoned that anything that seemed unclear could be understood using copilot, so I left this version as it is.




