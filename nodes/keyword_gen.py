# nodes/keyword_gen.py
import os
import json
from openai import OpenAI
from graph.state import CreatorFinderState
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

SYSTEM_PROMPT = """You are a YouTube content researcher. Your job is to generate search 
keywords that will find content creators in a specific niche on YouTube Shorts.

Rules:
- Only suggest keywords that real creators actually use in their video titles and descriptions
- Never invent niche-specific compound terms that don't exist (e.g. "AIFitnessLife")
- Think from the CREATOR's perspective — what does a creator in this niche 
  title their shorts? Not what a brand would call their product.
- Mix your list:
    2 broad keywords   : high volume, millions of results (e.g. "fitness", "workout")
    3 mid keywords     : niche community terms, hundreds of thousands (e.g. "home workout", "gym motivation")
    3 specific keywords: tight niche, tens of thousands (e.g. "calisthenics beginner", "desk worker fitness")
- If you cannot find 8 real keywords, return fewer. A short honest list beats a padded fake one.
- When in doubt about whether a keyword has a real creator community, leave it out.

Return ONLY a JSON array of strings, no explanation, no markdown.
Example: ["fitness", "workout", "home workout", "gym motivation", "calisthenics"]"""


def keyword_gen_node(state: CreatorFinderState) -> dict:
    print("\n--- NODE 2: KEYWORD GENERATION ---")

    completion = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate search keywords for YouTube Shorts creators who could promote this product:\n\n{state['product_description']}"}
        ]
    )

    raw = completion.choices[0].message.content.strip()

    try:
        keywords = json.loads(raw)
        if not isinstance(keywords, list):
            raise ValueError("Response is not a list")
    except Exception as e:
        print(f"Failed to parse keywords: {e}\nRaw: {raw}")
        return {"error": f"Keyword generation failed: {e}"}

    print(f"Generated {len(keywords)} keywords: {keywords}")
    return {"keywords": keywords}