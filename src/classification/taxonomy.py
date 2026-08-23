"""
4-Dimensional Classification Taxonomy Definitions & Enums for Myntra VoC Engine.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class WishlistIntent(str, Enum):
    GENUINE_PURCHASE_INTENT = "GENUINE_PURCHASE_INTENT"
    AESTHETIC_BOOKMARKING = "AESTHETIC_BOOKMARKING"
    SHORTLIST_COMPARISON = "SHORTLIST_COMPARISON"
    PRICE_SPECULATION = "PRICE_SPECULATION"

class RootFriction(str, Enum):
    FIT_AND_SILHOUETTE_AMBIGUITY = "FIT_AND_SILHOUETTE_AMBIGUITY"
    STYLING_AND_PAIRABILITY_ANXIETY = "STYLING_AND_PAIRABILITY_ANXIETY"
    FABRIC_AND_TACTILE_DOUBT = "FABRIC_AND_TACTILE_DOUBT"
    SOCIAL_VALIDATION_LAG = "SOCIAL_VALIDATION_LAG"
    OCCASION_DISCONNECT = "OCCASION_DISCONNECT"
    COMPARISON_PARALYSIS = "COMPARISON_PARALYSIS"
    PRICE_WAITING = "PRICE_WAITING"

class OfflineWorkaround(str, Enum):
    WHATSAPP_SHARING = "WHATSAPP_SHARING"
    YOUTUBE_TRYON_SEARCH = "YOUTUBE_TRYON_SEARCH"
    PINTEREST_CANVA_MOODBOARDING = "PINTEREST_CANVA_MOODBOARDING"
    BRACKETING = "BRACKETING"
    NONE = "NONE"

class UserCohort(str, Enum):
    STUDENT_GEN_Z = "STUDENT_GEN_Z"
    WORKING_PROFESSIONAL = "WORKING_PROFESSIONAL"
    TIER_2_ASPIRATIONAL = "TIER_2_ASPIRATIONAL"

class ClassifiedRecord(BaseModel):
    record_id: str
    source: str
    sub_source: str
    created_at: str
    rating: int
    upvotes_or_likes: int
    apparel_category: str
    brand_mentioned: str
    user_metadata: Dict[str, Any]
    raw_text: str
    normalized_text: str
    rqs_score: float
    detected_slang_tags: List[str]
    intent: WishlistIntent
    friction: RootFriction
    workaround: OfflineWorkaround
    cohort: UserCohort
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
