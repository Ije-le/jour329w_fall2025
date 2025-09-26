CNS Metadata
09/26/2025

STORIES/URL:
1. Trump administration warns Maryland against “DEI” contracts in Key Bridge rebuild: https://cnsmaryland.org/2025/09/19/trump-administration-warns-maryland-against-dei-contracts-in-key-bridge-rebuild/
Names
Donald Trump -U.S. President
Wes Moore -Maryland Governor
Sean Duffy -Secretary of Transportation

Organizations
None

Geographical location
Baltimore
Los Angeles
Memphis

Two-word topics
Baltimore bridge
Key bridge
DEI contracts

The story is a news story
Impact: 3


2. Nine people stand between her child and citizenship. It’s a fight she can’t afford to lose: https://cnsmaryland.org/2025/05/19/nine-people-stand-between-her-child-and-citizenship-its-a-fight-she-cant-afford-to-lose/
Names
Meny -U.S. Immigrant
Donald Trump -U.S. President
Leidy Perez -Communications Director, Asylum Seeker Advocacy Project

Organizations
Asylum Seeker Advocacy Project
U.S. Customs and Border Protections
U.S. Citizenship and Immigration Services

Geographical lication
Maryland
California
Cuba

Two-word topics
Birthright citizenship
Immigration clampdown
Executive orders

The story is a feature story
Imapct:4

3. Maryland will slow – not stop – its investment in schools: https://cnsmaryland.org/2025/04/08/maryland-will-slow-not-stop-its-investment-in-schools/
Names
Jim Rosapepe -Maryland Senator representing PG and Anne Arundel Counties
Wes Moore -Governor of Maryland
Justin Ready -Maryland Senator representing Caroll and Frederick Coounties

Organizations
Department of Education
House of Representatives
Senate

Geographical locations
Caroll County
Anne Arundel County
Frederick County

Two-word topics
Education bill
Education funding
Maryland education

The story is a news story
Impact 5

4. Brother of Bel Air murder victim speaks at the Republican convention: https://cnsmaryland.org/2024/07/16/brother-of-bel-air-murder-victim-speaks-at-the-republican-convention/
Names
Michael Morin -Brother of murder victim
Rachael Morin -Murder victim
Victor Antonio Martinez-Hernandez

Organizations
CATO Institute
ICE
Harford County Detention Center

Geographical location:
Maryland
Milwaukee
Bel Air

Two word topics
Bel Air murder
Republican convention
Murder case


The story is a news story
Impact: 5


5. Election takeaway: abortion remains a potent issue for voters: https://cnsmaryland.org/2023/11/10/election-takeaway-abortion-remains-a-potent-issue-for-voters/
Names
Sherod Brown -Ohio Senator
Jacob Rubashkin -Analyst
J.D. Vance -Ohio Senator

Organizations
Inside Elections
United Nations
Jackson Women's Health Organization

Geographical location
Ohio
Virginia
New Jersey

Two word topics
abortion rights
reproductive rights
abortion access

The story is an analysis
Impact: 5

llm

First story (Trump administration warns Maryland against “DEI” contracts in Key Bridge rebuild)
Prompt: uv run python -m newspaper --url=https://cnsmaryland.org/2025/09/19/trump-administration-warns-maryland-against-dei-contracts-in-key-bridge-rebuild/ -of=text | uv run llm -m groq/qwen/qwen3-32b "Extract structured metadata from this news story and return as JSON with these exact fields:
{
  \"url\": \"the url of the story\",
  \"people\": [\"list of up to 3 people with their titles/roles\"],
  \"organizations\": [\"government agencies, companies, groups mentioned\"],  
  \"locations\": [\"cities, counties, states, specific places\"],
  \"topics\": [\"3-5 topic tags, max 2 words each\"],
  \"story_type\": \"breaking news, feature, analysis, investigation, other\",
  \"impact\": \"a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people\",
  \"
}"

Response: <think>
Okay, let's start by reading through the user's query carefully. They want me to extract structured metadata from a news story about the Trump administration warning Maryland against using DEI contracts in the Key Bridge rebuild. The output should be in JSON with specific fields. 

First, I need to parse the given article for each required field. The URL field is tricky because the article doesn't provide a specific URL. Since the user wants the actual URL, but it's not mentioned, maybe they expect a placeholder or perhaps it's okay to leave it as "the url of the story" as stated. But looking back, the user's example shows that if the URL isn't present, it's left as "the url of the story". Hmm, the user might be using a placeholder, but the actual URL is not in the provided text. So I'll keep it as the example shows.

Next, the people field requires up to three people with their titles/roles. The article mentions Sean Duffy as the Secretary of Transportation, Gov. Wes Moore, and President Donald Trump. Each has their roles listed, so that's straightforward.

For organizations, the government agencies mentioned are the Trump administration, the Maryland congressional delegation, and the federal government. The Federal Department of Transportation could be under the Trump administration, so I'll list them as separate. The Maryland congressional delegation is a group of Democrats, so that's included.

Locations are Maryland, Baltimore, Francis Scott Key Bridge, Port of Baltimore, Los Angeles, Washington, and Memphis. These are all mentioned as places affected or referenced.

Topics should be 3-5 tags. Looking at the main subjects: DEI (Diversity, Equity, Inclusion), Infrastructure, Trump Administration, Legal Issues, Government. That's five, but maybe reduce if necessary. Let me check the article. The main topics are definitely DEI contracts, the bridge reconstruction, legal vulnerabilities, federal funding, and political conflict between Trump and Moore. So DEI, Infrastructure, Legal Issues, Federal Funding, Political Conflict. That's five.

The story type here is a breaking news since it's a recent development with the Trump administration's warning. 

Impact rating on a 1-5 scale. Since it's a federal funding issue affecting a major infrastructure project, which has economic and safety implications for Maryland and beyond, the impact is significant. I'd rate it 4 or 5. Given federal involvement and potential legal issues, 4 is a safe choice.

Now, putting this all together in JSON. Make sure the fields are exactly as specified. Let me double-check each section for accuracy. People have the correct roles, organizations include all agencies mentioned, locations are all present, topics cover the main issues without being too vague or too specific. Story type is breaking news, impact is high. Looks good.
</think>

{
  "url": "the url of the story",
  "people": [
    "Sean Duffy - Secretary of Transportation",
    "Wes Moore - Maryland Governor",
    "Donald Trump - President"
  ],
  "organizations": [
    "Trump administration",
    "Maryland congressional delegation (Democrats)",
    "Federal Department of Transportation"
  ],
  "locations": [
    "Maryland",
    "Baltimore",
    "Francis Scott Key Bridge",
    "Port of Baltimore",
    "Washington",
    "Los Angeles",
    "Memphis"
  ],
  "topics": [
    "DEI (Diversity, Equity, Inclusion)",
    "Infrastructure",
    "Government Contracting",
    "Legal Disputes",
    "Political Conflict"
  ],
  "story_type": "breaking news",
  "impact": 4