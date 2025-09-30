CNS_tag_browser     9/29/2025

LESSONS LEARNED FROM QUERIES
The queries return information on the tag name and how many times it's been used. The tags are case sensitive, and some of the information returned are repetitive, because some are in upper case and others are in lower case. So while a tag might have a count of 10, there is the possibility it has been used more times than that. Example: "CNS TV" and "cnstv."

PLANNING TAG BROWSER
How would someone want to search through 1000+ tags?:
    A person would do this by typing the tag name they are searching for in a search bar.
What information should be displayed prominently?:
    After the search, the tag name should be displayed prominently, along with the count like it does in the terminal. This can be immediately followed by the first few stories in which these tags were used.
How should the tags be sorted by default?:
    The tags should be sorted alphabetically.
What filters might be useful?:
    Filtering by the beats covered by the newsroom might help. So if a user is searching for "Donald Trump" tag in connection to a health story, it might help to filter your search down to the health beat rather than looking through everything that has that tag in it.
                           FEATURE WISHLIST
A search bar
An option to filter by beats
Arrows below search results that let users skip to other pages, like with Google. Since results will be returned alphabetically, this will help with finding results further down.

                        Notes:
After my first prompt, I got a pretty basic interface. It had barely any colors and looked like a table with a list of tags and the number of times they'd been used. It didnt have any filter buttons because I didnt include it initially, so I updated my prompt to incliude that. It also had no colors. I sourced for hex codes closer to CNS colors, since I didnt have the hex codes for CNS readily available. Although I wanted the tags to have two story previews under each tag, I wasn't sure how this would work, since we do not have that data available. I decided to try and see what Copilot would do in this instance. My thought was that I would have empty links that can be updated later under each tag, but Copilot produces previews using the summarization of the stories, where available (I didn't realize existed at first).
I took a look at the webpage and though everything seemed to work just fine, the search bar for the tags was quite limiting because users had to know exactly what tags they were looking for to find anything, so I updated the prompt to return a search bar that doubled as a drop down option. That fixed the problem.