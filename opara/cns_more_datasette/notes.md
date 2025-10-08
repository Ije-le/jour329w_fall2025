### CNS More Datasette  10/08/2025

I found some of the keywords to be quite relevant, for example, funding freeze made sense for the story "Lawmakers, environmental groups say Trump freezes threaten local water quality," but I would not choose "Indigenous History" as a keyword for this story: Senate panel passes bill making Chesapeake National Recreation Area a national park unit.

A pattern I noticed is that almost all the stories had Chesapeake Bay as a tag which is not so surprising. Most of the similar keywords either had to do with legislation or acquatic life/environmental issues.

I did not like that all rows in the table were returned in the search. For me, it makes it difficult to easily determine where the points of similarities end, especially because similarities are recorded in points rather than words like: "very similar, similar, not similar."


### Embeddings


I searched for "protests"

The first few lines returned stories about protests, rallies, activism, and as I scrolled down, the the similarities declined as expected. It all made sense at the beginning, but before I got half way through, I began to see stories that ordinarily had no business with the word "protests."
However, I should note that apart from the bottommost stories that were completely off, some of the stories in the middle of the table (especially those ranked between 0.185 and 0.22) seemed to almost always have something to do with groups, even if not directly related to protests.
Examples:   Hundreds gather in Annapolis to honor Michael Busch
            Legal aid, community groups begin outreach on free eviction counsel
            Many workers, volunteers help to make a successful inauguration for Governor Hogan
This is most likely because the exercise is based on embeddings and the numbers that add up to produce "protests" are probably 'neighbours' of other numbers or the floating points that produce "groups" or "community" or words like that.

As with the first exercise, I did not like getting all the rows back. At first, I assumed that the point where stories begin to be ranked 0.0... would be the ideal point to start seeing stories without similarities to "protests," but I could see that some stories with rankings above 0.1 did not have any connections at all to the word. It was not too difficult to decide how similar the stories are to each other becauase the datset is small in this case, but I imagine that this would be a bit difficult with larger datasets. I would prefer if datasette could provide just rows that are similar to the search term rather than the whole thing.