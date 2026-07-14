# tools/youtube.py
import os
import requests
from dotenv import load_dotenv
from graph.state import CreatorProfile, ShortMetrics

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE = "https://www.googleapis.com/youtube/v3"

# Budget tier → subscriber range
BUDGET_TIERS = {
    "low":  (1_000,    50_000),
    "mid":  (50_000,   500_000),
    "high": (500_000,  999_999_999),
}


def search_shorts(query: str, max_results: int = 10) -> list[dict]:
    """
    Search YouTube Shorts by keyword.
    Returns a list of raw items from the YouTube search API.
    Costs 100 units per call.
    """
    resp = requests.get(
        f"{BASE}/search",
        params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoDuration": "short",
            "maxResults": max_results,
            "key": API_KEY,
        }
    ).json()

    if "error" in resp:
        raise Exception(f"YouTube API error: {resp['error']['message']}")

    return resp.get("items", [])


def get_channel_profiles(channel_ids: list[str]) -> dict[str, dict]:
    """
    Fetch channel stats + snippet for a batch of channel IDs.
    Returns dict keyed by channel_id.
    Costs 1 unit per call regardless of batch size.
    """
    if not channel_ids:
        return {}

    resp = requests.get(
        f"{BASE}/channels",
        params={
            "part": "snippet,statistics",
            "id": ",".join(channel_ids),
            "key": API_KEY,
        }
    ).json()

    return {c["id"]: c for c in resp.get("items", [])}


def get_last_n_shorts(channel_id: str, n: int = 5) -> list[ShortMetrics]:
    """
    Fetch the last N shorts from a specific channel.
    Costs 100 units (search) + 1 unit (videos.list).
    """
    # search for recent shorts from this channel
    search_resp = requests.get(
        f"{BASE}/search",
        params={
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "videoDuration": "short",
            "order": "date",
            "maxResults": n,
            "key": API_KEY,
        }
    ).json()

    video_ids = [i["id"]["videoId"] for i in search_resp.get("items", [])]
    if not video_ids:
        return []

    # get stats for all videos in one call
    videos_resp = requests.get(
        f"{BASE}/videos",
        params={
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": API_KEY,
        }
    ).json()

    shorts = []
    for v in videos_resp.get("items", []):
        stats = v.get("statistics", {})
        shorts.append(ShortMetrics(
            title=v["snippet"]["title"],
            views=int(stats.get("viewCount", 0)),
            likes=int(stats.get("likeCount", 0)),
            comments=int(stats.get("commentCount", 0)),
            url=f"https://youtube.com/watch?v={v['id']}"
        ))

    return shorts


def build_creator_profile(channel_id: str,channel_data: dict,matched_keyword: str,n_shorts: int = 5) -> CreatorProfile:
    """
    Given raw channel data from the API, build a full CreatorProfile
    including last N shorts.
    """
    stats = channel_data.get("statistics", {})
    snippet = channel_data.get("snippet", {})

    subs = int(stats.get("subscriberCount", 0))
    total_views = int(stats.get("viewCount", 0))
    video_count = int(stats.get("videoCount", 1))

    avg_views = total_views // video_count if video_count else 0
    engagement_rate = round((avg_views / subs * 100), 2) if subs else 0.0

    recent_shorts = get_last_n_shorts(channel_id, n=n_shorts)

    return CreatorProfile(
        channel_id=channel_id,
        channel_name=snippet.get("title", "Unknown"),
        subscribers=subs,
        total_views=total_views,
        video_count=video_count,
        country=snippet.get("country", "N/A"),
        bio=snippet.get("description", "")[:300],
        avg_views_per_video=avg_views,
        engagement_rate=engagement_rate,
        recent_shorts=recent_shorts,
        matched_keywords=[matched_keyword],
    )


def filter_by_budget(profile: CreatorProfile, budget_tier: str) -> bool:
    """
    Returns True if the creator's subscriber count falls within
    the budget tier range.
    """
    low, high = BUDGET_TIERS.get(budget_tier, (0, 999_999_999))
    return low <= profile.subscribers <= high