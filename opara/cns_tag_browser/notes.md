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

                        BUILDLING WITH COPILOT
My first prompt asked for a user-friendly webpage that has a search bar and a list of tags showing the tag name and count. I asked for the pagination buttons below as well and different documents for CSS and Javascript. Copilot produced a pretty basic webpage with barely any colors. It looked more like a table of tags, so I followed up with a prompt directing Copilot to include colors, and a filter bar in which newsroom beats would be listed alphabetically. I also directed Copilot to include a preview of two stories for each tag. I wasnt sure how this would work, since we have no data for stories. But I wanted to see how Copilot would handle this. My thought was that I would have empty links that can be updated later under each tag, but Copilot produced previews using the summarization of the stories, where available (I didn't realize these existed at first because they are not available for all tags). Where there were no summarizations, it did not include anything other than the tag name and count. To make everything look more uniform, I asked Copilot to include "Preview to be added soon" under each tag. It did.
A quick look through the webpage showed that everything was working just fine, but the search bar for the tags was quite limiting because users had to know exactly what tags they were looking for and type that in before they could find anything, so I followed up with a prompt asking Copilot to return a search bar that doubled as a drop down option. That way, a user could simply scroll through the list of tags and decide which to choose.
I was not too impressed with the way the webpage looked because though it now had more colors, it still looked like a table. I asked for each tag to be put in its own container rather than a single container. I wanted different fonts for the previev message. I also wanted the tags to take up more space. At first, I ran this prompt and it didnt work. The next time, it did, but presented a distorted webpage, so I asked it to revert to what it was before.
                             REFLECTIONS