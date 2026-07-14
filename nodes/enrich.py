# nodes/enrich.py
import time
from graph.state import CreatorFinderState
from tools.youtube import get_channel_profiles, build_creator_profile, filter_by_budget


def enrich_node(state: CreatorFinderState) -> dict:
    idx = state["current_keyword_idx"]
    keyword = state["keywords"][idx]
    channel_ids = state["current_batch_channel_ids"]
    candidates = dict(state["candidates"])  # copy existing candidates
    budget_tier = state["budget_tier"]

    print(f"\n--- NODE 4: ENRICH ---")
    print(f"Enriching {len(channel_ids)} channels for keyword: '{keyword}'")

    # batch fetch all channel profiles in one API call (1 unit)
    channel_map = get_channel_profiles(channel_ids)

    added = 0
    skipped_budget = 0
    skipped_duplicate = 0

    for channel_id in channel_ids:
        # skip if already in candidates from a previous keyword
        if channel_id in candidates:
            candidates[channel_id].matched_keywords.append(keyword)
            skipped_duplicate += 1
            continue

        channel_data = channel_map.get(channel_id)
        if not channel_data:
            continue

        # build full profile including last 5 shorts
        profile = build_creator_profile(
            channel_id=channel_id,
            channel_data=channel_data,
            matched_keyword=keyword,
            n_shorts=5
        )

        # hard filter by budget tier before adding
        if not filter_by_budget(profile, budget_tier):
            skipped_budget += 1
            continue

        candidates[channel_id] = profile
        added += 1

        # be nice to the API
        time.sleep(0.5)

    print(f"Added: {added} | Budget filtered: {skipped_budget} | Duplicates merged: {skipped_duplicate}")
    print(f"Total candidates so far: {len(candidates)}")

    return {
        "candidates": candidates,
        "current_keyword_idx": idx + 1  # move to next keyword
    }