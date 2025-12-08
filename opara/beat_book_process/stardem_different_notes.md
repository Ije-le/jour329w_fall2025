## BEAT BOOK DIFFERENT     12/5/2025

In creating this beat book I thought of producing a mind map like the one NotebookLM generates. I asked Copilot to recreate talbot_beatbook_v6.md as a html document and it did. At first, I had a hard time locating the map, but I find it every time I run this cd /workspaces/jour329w_fall2025/opara/stardem_different && python3 -m http.server 8080


I really like the asthetics of this one. I like how clicking on one dot gives you some information about that topic or subtopic via a panel that appears on the right. For instance, in the middle of the mind map is a big red dot to which every other thing is connected. Clicking on that immediately gives you an overview of Talbot County's Public Safety beat. The dots are labelled too, which helps with navigation. The color legend at the bottom left also helps; one can see that blue dots represent coverage areas, green represents key people and so on. At the top of the map, There are buttons that help you filter through the map, and display just one group: key people only or key organizations only, etc.
I also like how the dots are connected to each other to show the connections between issues discussed. When a user clicks on one dot, the lines that connect that dot to other issues are immediately highllighted, so they can easily find other connected issues.
Although it has no dedicated source directory, the 'key people' groups work as a disjointed source directory because they provide the relevant information for the sources.

A few issues I felt might hinder the effectiveness of this map is that a reporter cannot access the information chronologically. Not exactly chronologically, but the kind of progression that occurs wwhen reading normally is absent in this case. Any do can be read first and anyone can be read last, unlike the other structures where you get to read the overview first and have an idea of what you are delving into. It seemes better suited for when you have already read a beat book and need a reference for something.
I think that because of how it is structured, a reporter will more likely read a written beat book than click on all the points on the map.
Also, this map does not come with story ideas a reporter can possibly explore. The information provided is not as detailed as the narrative structure, whicih makes sense; these are different structures.
A final limitation of this draft is that it is not searchable.

I thought of telling copilot to update the map and make it have some of these feature. I also wanted the background to have a different color since the blue was conflicting with some of the blue dots, but I worried it would mess it up so I asked for a second map.
Copilot refused to get it done a number of times but eventually did.

The new mindmap, talbot mindmap v2.html, included a story angle section. What I like about the story angles is that they are represented by a different color of dots and connected to their coverage areas. There is also a button at the top that makes other dots disappear so that a user only sees the story angles and the Talbot county overview.
One thing that did not change: It's still not very searchable.
Although there is a search bar at the top, it doesn't work when you search for anything word.
However, I think that the fact of beimng broken down into categories helpsn with the search process.
If a user need to find information about someone, for instance, they could filter for 'key people' and browse through those names.
Not the most ideal situation, but it I think it works still.




Link to server:
$ cd /workspaces/jour329w_fall2025/opara/stardem_different && python3 -m http.server 8080