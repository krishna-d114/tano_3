# nodes/search.py
from graph.state import CreatorFinderState
from tools.youtube import search_shorts


def search_node(state: CreatorFinderState) -> dict:
    idx = state["current_keyword_idx"]
    keyword = state["keywords"][idx]

    print(f"\n--- NODE 3: SEARCH [{idx + 1}/{len(state['keywords'])}] ---")
    print(f"Keyword: {keyword}")

    items = search_shorts(query=keyword, max_results=10)

    # extract unique channel IDs from results
    channel_ids = list(set([
        item["snippet"]["channelId"] for item in items
    ]))

    print(f"Found {len(channel_ids)} unique channels")

    return {"current_batch_channel_ids": channel_ids}