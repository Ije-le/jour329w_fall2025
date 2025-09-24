Ijeoma Opara 09/22/2025
URL: https://cnsmaryland.org/2025/05/19/nine-people-stand-between-her-child-and-citizenship-its-a-fight-she-cant-afford-to-lose/

Title: Nine people stand between her child and citizenship. It’s a fight she can’t afford to lose.

COMMAND:
uv run python -m newspaper --url=https://cnsmaryland.org/2025/05/19/nine-people-stand-between-her-child-and-citizenship-its-a-fight-she-cant-afford-to-lose/ -of=text | 
 uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Read the text in the article and identify five significant topics in it, bearing in mind that you are an expert at categorizing topics for news stories."
OUTPUT:
1. Executive Action & Constitutional Clash  
   – Trump’s Jan. 20 executive order seeking to curb birthright citizenship; the ensuing federal injunction; DOJ appeal to the Supreme Court; oral arguments in Trump v. CASA.

2. Legal Challenge & Plaintiffs  
   – CASA v. Trump lawsuit (consolidated with two sister suits); five anonymous pregnant mothers plus immigrant-rights nonprofits ASAP and CASA as plaintiffs; stakes for future U.S.-born children.

3. Human Impact: The Mothers’ Stories 
 Profiles of Meny (California), Georgina (Maryland), Niurka (Florida), Lesly (New Jersey): their migration paths, asylum status, economic hardship, and fears of statelessness for their babies.

4. Immigration Policy Uncertainty  
   – Shifting rules, long court backlogs, rising anti-immigrant sentiment; psychological toll on mixed-status families; financial barriers to legal counsel.

5. Identity, Risk & Advocacy  
   – Decision to join a high-profile Supreme Court case while remaining publicly anonymous; tension between personal visibility and collective protection; mothers framing the lawsuit as an act of advocacy for their children. 

The result of this command would have been closer to my expectations had there not been the accompanying explanations that came with each topic. This might have something to do with the way I phrased my question, because when I did a test run with the original sample ("You are an expert at categorizing topics for news stories. Read the text and provide no more than 5 topics."), it gave me five, impressive two-word tags


   COMMAND2:
   uv run python -m newspaper --url=https://cnsmaryland.org/2025/05/19/nine-people-stand-between-her-child-and-citizenship-its-a-fight-she-cant-afford-to-lose/ -of=text |
 uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Your topics are too wordy. Kindly produce 5 concise topics. Bear in mind that you are an expert at categorizing topics for news."
 OUTPUT:
1. Supreme Court weighs Trump birthright-citizenship ban; 5 pregnant moms sue.  
2. Stateless risk: Immigrant mothers fight to secure U.S. passports for July babies.  
3. CASA v. Trump: 48-hour lawsuit blocks order, nine justices now decide.  
4. Anonymity vs. exposure: Plaintiffs shield identities in high-stakes citizenship case.  
5. From Honduras to High Court: One educator’s asylum battle for her unborn child.

These responses took my comments on wordiness into account and reduced the output, but these will still not twork well as tags.

COMMAND3:
uv run python -m newspaper --url=https://cnsmaryland.org/2025/05/19/nine-people-stand-between-her-child-and-citizenship-its-a-fight-she-cant-afford-to-lose/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Please refrain from generating headlines. Rather, provide five topic with a maximum  length of two words. Remember, you are an expert at categorizing tooics for news stories."
OUTPUT:
Birthright Citizenship  
Supreme Court  
Immigrant Mothers  
Executive Order  
Legal Challenge

I decided to clearly include word limitations in my prompt since that seemed to be a recurrent factor throughout the process. This time the result was way better, and although I would substitute legal challenge if I was really using these as tags, I find the final output more satisfactory.

I don't think this was a very difficult process. It was not too deifficult to think of changes to the prompt, and the only repetitive task was modifying my prompt to produce the desired results, which is quite normal when working with llms generally.