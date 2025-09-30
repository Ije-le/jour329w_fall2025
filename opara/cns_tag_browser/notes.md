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
                        BUILDING THE BROWSER
After my first prompt, I got a pretty basic interface. It looked like a table with a list of tags and the number of times they'd been used. It didnt have any filter buttons because I didnt include it initially, so I updated my prompt to incliude that.