## Stardem_choice     11/12/2025

# Note: The two useful json files here are stories_with_entities_v1.json, stories_with_entities_v2.json and stories_with_entities_v4.json. v3 was generated in error,

# Documentation:
I had started this exercise with stories_with_entities_v1.json, using the groq/meta-llama/llama-4-maverick-17b-128e-instruct for 926 stories, but that started to return a rate-limit error after 150 stories, so I ended it, thinking it was a thing with the script. Then I began the same process for stories_with_entities_v2.json with the same model. That was slow too, but it ended on its own because a notification popped up on my screen that I had to stop my codespaces and restart. Because I did not see any reasonable improvement in the speed, I decided to use the groq/moonshotai/kimi-k2-instruct-0905 for the next trial. I saved these stories to replace the incomplete data in stories_with_entities_v1.json (since I now had two versions with incomplete data). It was also at this point that I reduced the sample size to 300. The Kimi model was still very slow, but I let it run. Because of the rate-limt error, this took more than six hours, but the scripts eventually got processed.

While testing the output before running the entire input json, I noticed the model was ignoring my prompts requesting that it skips processing for stories with no geographical ties to Eastern Shore. It would say "Skipped processing ..." in the timeline, and still return values in the output json file. Since it insisted on returning values, I asked Copilot to do this:
    "Instead of returning any values  for names, places and organizations for the stories that have no geographical focus in Eastern Shore, update the prompt so that the the only values in the list for these stories says SKIPPED Remember to keep the prompt in a variable format."
This mostly worked. When it returned the output json, theere were two stories I saw that had values returned even though they were unconnected to Eastern Shore. But the model skipped about 23 stories out of 300.

For the next variation, I decided to use a different model to see how it would perform with skipping the stories I did not want.
Also, since I lost my progress at least twice for this task, I asked copilot what I could do about it and copilot suggsted that I update my prompt to include a command that saves each result to the otput json after they are processed, so that even if I have to start afresh, I wouldn't lose the progress I'd made. I updated my prommt to reflect this.
# prompt here:

I tried using the glm-4.6:cloud, but it kept saying all stories had been processed. I tried switching to a new topic: Public Safety, but I still got the respomse that all the stories had been processed, so I used a new model with the same public safety story: groq/openai/gpt-oss-120b. 
This worked, but. I noticed it updated the figures weirdly in the terminal. When I tried the first 10, I was getting responses that looked like this:
    Processing story 7/10: Never plug these into power strip...
      Skipped: Not focused on Eastern Shore
    Processing story 9/10: WHAT A NIGHT! - Storms cause damage, flooding in Mid-Shore r...
    Processing story 11/10: Police investigating Easton homicide...
    Processing story 13/10: Cambridge theater has another incident of smoke in theater...
    Processing story 15/10: Dispute over girlfriend led to shooting, police say - Suspec...
    Processing story 17/10: Fire group raising $5 million for training center...
    Processing story 19/10: St. Michaels reorganizes police, OKs raises...
For some weird reason, it was arranging the stories by odd numbers alone, and even returning values with numbers above ten. Copilot said this was because I had set my script to save responses as they are generated and only continue from where they stopped. When I compared the stories in the output file with those in the input one, they were accurate. So while the terminal showed the stories in odd numbers, it was not skipping stories labelled with even numbers in the json file. It was randomly selecting stories as instructed, so I didn't think there was need to be worried.
When the model had process about a hundred stories, it began the rate limit crawl. It was almost midnight, so I waited a little because rate limits would be reset for the other models. I decided to test if the progress I had made was actually being saved if I switched to a different model halfway through. I interrupted the process and swtiched to groq/meta-llama/llama-4-maverick-17b-128e-instruct
It did not start afresh. I had 114 stories processed at this time (what was showing in the terminal was 229/300 because it was skipping even numbers). When I started afresh with the new model, It told me just that:

    Found 114 already processed stories. Resuming...
    Randomly selected 300 stories from the total available
    Processing 186 remaining stories (out of 300 total) with model groq/meta-llama/llama-4-maverick-17b-128e-instruct...
    Processing story 115/300: Cambridge man found guilty of child abuse, assault...
    Processing story 117/300: Tilghman man sentenced to five years for sexual abuse of a c...

So for v4, I used two models. If using two models for one task will not be a problem, I will likely continue to include this to all my prompts going forward, so that I dont have to start afresh if something interrupts progress in the terminal.
The Llama model worked faster this time I guess because the limit had reset. At the end of the process, this model skipped just 13 stories, which I found a little surprising, because the other one skipped 23.
stories_with_entities_v2.json did not have up to 300 stories, so I loaded only stories_with_entities_v1.json and stories_with_entities_v4.json to Datsette.


#### Experiment Design
I only changed the model for both versions and I was open to seein what difference could come up from running the same prompt with different models. The difference was not too obvious.
My first attempt at this process (which was not saved in either of this variations because of the rate limit issue), I figured that telling the LLM to return [SKIPPED] would improve my results and take out stories about places that are not Eastern Shore, especially because there was no other way to get those stories out of the way. It did improve the responses by narraowing down the stories to only those about Eastern Shore, but also, having the [SKIPPED] tag helped me differentiate between stories that just had no relationship with Eastern Shore and those who actually did not have any names/places/organizations mentioned in them.
First because they were the only complete versions I had, but also because they were narrowed down to the geographical area I was interested in.

#### Comparative Analysis
I would say v1 produced a better result than v4. Both versions were identical  and had similiar probelems: they sometimes retruned the names of authors as part of the values for 'people'.  But I think this was more prominent in v4 than v1, which is why I would choose v1 over v4.
I think both versions did very well with the organizations category, but I liked v4's organization section more because I could see more cases of consistency in it. For exmaple, the model was able to decipher that SMFD meant St Michaels Volunteer Fire Department. It did not return SMFD and St Michaels Volunteer Fire Department. It picked one, the unabbreviated version, and stuck with it. v1 also expanded abbreviations, but I found more cases of this in v4.
I did not notice any unexpected strengths or weakness in both cases, but I like how they expanded organization names.

#### Prompt Engineering Insights
The prompt element with the biggest impact on quality is the part where I asked that it return [SKIPPED], since the model was hell bent on returning a list anyway. But for the overall process, I definitely think the best prompt was the on that had each result getting saved to the output json as soon as it was processed, so that my work doesn't get lost.
Adding examples did help. At first, I gave copilot examples of stories to avoid. I said: avoid ART AROUND THE WORLD if it involved Art outside of Eastern Shore. It helped a little, but stories like one about Johnny Depp's performance in London still kept popping up. Because these stories kept returning lists, I gave an example of what should be returned if a story wasnt situated in Eastern Shore: [SKIPPED]. That settled it.
Instructions should be very specific, but more importantly, I think they are more effective if tailored to address initial unfavorable results. 

#### Final Recommendations
I would use v1 if I were to create a beatbook. I recommend the uv run python add_entities.py --model groq/openai/gpt-oss-120b --input topic_stories.json with this prompt:

If I had to work on this afresh, I would prompt the LLM to avoid including authors names to the list.




### My Prompts 
-Simplify this script when it calls llm. Do not have multiple candidates. Do not use llm chat. The correct and only command begins with uv run llm --model 

-Return the original json object and add then add metadata in stories_with_entities_v1.json 
What I want is to process all of the stories when there is no --limit argument

-Rewrite the script so it saves output to stories_with_entities_v1.json and with the prompt still in a variable format, update it so that it skips processing for stories that are not situated in Eastern Shore. Examples of stories to skip are those like ART AROUND THE WORLD if they are not talking of Art in Eastern Shore.

-Instead of returning any values  for names, places and organizations for the stories that have no geographical focus in Eastern Shore, update the prompt so that the the only values in the list for these stories says SKIPPED Remember to keep the prompt in a variable format.

-Update the script to recall that stories outside Eastern Shore should only return a list that says [SKIPPED]

-Update the script to save the output to stories_with_entities_v2.json and remember to return SKIPPED for stories with no geographical focus on Eastern Shore. Let the results be saved to the output json after each story is processed. Bear in mind that  I want to be able to:
Stop it anytime without losing progress
Resume from where it left off
Have a partial file even if it never completes

-Update the script to save the output to stories_with_entities_v2.json and remember to return SKIPPED for stories with no geographical focus on Eastern Shore. Let the results be saved to the output json after each story is processed. Bear in mind that  I want to be able to:
Stop it anytime without losing progress
Resume from where it left off
Have a partial file even if it never completes

-Update the script to select 300 random stories for processing.

-Update the script so that it saves output to stories_with_entities_v3.json.

-Update the script so that it saves output to stories_with_entities_v3.json. Let it take input from public_safety_stories.json and remember to return the original object, then ad metadata in stories_with_entities_v3.json. Remember we are processing 300 random stories. Also remember to return SKIPPED for stories with no geographical focus on Eastern Shore. Let the results be saved to the output json after each story is processed. Bear in mind that  I want to be able to:
Stop it anytime without losing progress
Resume from where it left off
Have a partial file even if it never completes

-You did not update the new_entities.py script to reflect that we are now taking input from public_safety_stories.json. Kindly do that now. On line 7 it has this:  reads a topic JSON (default: `arts_culture_stories.json` in the same directory) calls the specified model exactly ONCE with the full set of stories (default: groq/meta-l

