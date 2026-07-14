# nodes/filter_and_log.py
import json
import os
from datetime import datetime
from graph.state import CreatorFinderState, CreatorProfile

# Math filter thresholds
MIN_SUBS = 1_000
MAX_SUBS = 10_000_000
MIN_ENGAGEMENT_RATE = 1.0    # percent
MIN_AVG_VIEWS = 500


def passes_math_filter(profile: CreatorProfile) -> tuple[bool, str]:
    """Returns (passes, reason_if_rejected)"""
    if profile.subscribers < MIN_SUBS:
        return False, f"Too small ({profile.subscribers} subs)"
    if profile.subscribers > MAX_SUBS:
        return False, f"Too large ({profile.subscribers} subs)"
    if profile.engagement_rate < MIN_ENGAGEMENT_RATE:
        return False, f"Low engagement ({profile.engagement_rate}%)"
    if profile.avg_views_per_video < MIN_AVG_VIEWS:
        return False, f"Low avg views ({profile.avg_views_per_video})"
    return True, ""


def filter_and_log_node(state: CreatorFinderState) -> dict:
    print("\n--- NODE 5: MATH FILTER + LOG ---")

    candidates = state["candidates"]
    passed = {}
    rejected = []

    for channel_id, profile in candidates.items():
        ok, reason = passes_math_filter(profile)
        if ok:
            passed[channel_id] = profile
        else:
            rejected.append(f"{profile.channel_name}: {reason}")

    print(f"Passed : {len(passed)}")
    print(f"Rejected: {len(rejected)}")
    for r in rejected:
        print(f"  ✗ {r}")

    # serialize to JSON
    output = {
        "run_metadata": {
            "timestamp": datetime.now().isoformat(),
            "product": state["product_description"],
            "budget_tier": state["budget_tier"],
            "location": state["location"],
            "keywords_used": state["keywords"],
            "total_found": len(candidates),
            "passed_filter": len(passed),
        },
        "creators": [
            {
                "channel_id": p.channel_id,
                "channel_name": p.channel_name,
                "subscribers": p.subscribers,
                "total_views": p.total_views,
                "avg_views_per_video": p.avg_views_per_video,
                "engagement_rate": p.engagement_rate,
                "country": p.country,
                "bio": p.bio,
                "matched_keywords": p.matched_keywords,
                "recent_shorts": [
                    {
                        "title": s.title,
                        "views": s.views,
                        "likes": s.likes,
                        "comments": s.comments,
                        "url": s.url
                    }
                    for s in p.recent_shorts
                ]
            }
            for p in passed.values()
        ]
    }

    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/creators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {filename}")

    return {"candidates": passed}