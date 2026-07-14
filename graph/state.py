from typing import TypedDict, List,Dict,Optional
from pydantic import BaseModel, Field

class ShortMetrics(BaseModel):
    title : str = Field(description = "Title of the video")
    views : int = Field(description = "view count ")
    likes : int = Field(description = "likes count")
    comments : int = Field(description = "comments count")
    url : str = Field(description = "URL of the short")


class CreatorProfile(BaseModel):
    channel_id: str
    channel_name:str
    subscribers:int = 0
    total_views: int = 0
    video_count:int = 0
    country :str = "N/A"
    bio:str = ""
    avg_views_per_video:int = 0
    engagement_rate:float = 0.0
    recent_shorts:List[ShortMetrics] = []
    matched_keywords:List[str] = []
    llm_status:str = "pending"
    llm_reasoning:str = ""

class CreatorFinderState(TypedDict):
    product_description:str
    budget_tier: str
    location:str

    keywords:List[str]
    current_keyword_idx:int

    current_batch_channel_ids: List[str]

    candidates: Dict[str,CreatorProfile]

    shortlist:List[CreatorProfile]
    error:str
