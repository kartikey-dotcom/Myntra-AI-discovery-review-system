"""
4-Dimensional Taxonomy Classifier.
Classifies high-signal VoC records across:
1. Wishlist Behavioral Intent
2. Non-Monetary Root Friction
3. Offline User Workarounds
4. User Cohort
"""

import re
from typing import Dict, Any, Tuple, Optional
from src.classification.taxonomy import (
    WishlistIntent, RootFriction, OfflineWorkaround, UserCohort, ClassifiedRecord
)
from src.utils.llm_client import LLMClient

class TaxonomyClassifier:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        # Friction rules
        self.styling_pattern = re.compile(
            r"(\[STYLING_PAIRABILITY_ANXIETY\]|pair|kiske saath pair|styling|outfit|accessories|trousers|bottoms|shoes|sneakers|heels|styling inspo|complete look)",
            re.IGNORECASE
        )
        self.fit_pattern = re.compile(
            r"(\[CROSS_BRAND_SIZE_INCONSISTENCY\]|\[SILHOUETTE_BODY_MISMATCH\]|\[BRACKETING_AND_SHRINKAGE_HEDGE\]|fit|size|sizing|chest|bust|waist|shoulder|baggy|tight|5'10|5'2|ankles|midi|petite|curvy|broad shoulder)",
            re.IGNORECASE
        )
        self.fabric_pattern = re.compile(
            r"(\[FABRIC_TRANSPARENCY_DOUBT\]|fabric|patla|transparent|cotton|polyester|viscose|linen|see-through|breathable|bleed|shrink|scratchy|lining|itchy)",
            re.IGNORECASE
        )
        self.social_pattern = re.compile(
            r"(\[PEER_SOCIAL_VALIDATION_LAG\]|whatsapp|screenshot|girlies|sister|friends|roommate|opinion|verdict|approv)",
            re.IGNORECASE
        )
        self.occasion_pattern = re.compile(
            r"(\[OCCASION_DISCONNECT\]|nowhere to wear|future goa|aspirational buy|no immediate plan|too festive)",
            re.IGNORECASE
        )
        self.comparison_pattern = re.compile(
            r"(\[COMPARISON_PARALYSIS\]|identical|decision fatigue|confused between 3|comparing fabric|wishlist has 20)",
            re.IGNORECASE
        )
        self.price_pattern = re.compile(
            r"(\[PRICE_SPECULATION\]|waiting for eors|track discount|sale ke liye|price is currently|coupon)",
            re.IGNORECASE
        )

        # Workaround patterns
        self.whatsapp_pattern = re.compile(r"(whatsapp|screenshot|shared screenshot|sent the myntra link|girlies)", re.IGNORECASE)
        self.youtube_pattern = re.compile(r"(youtube|haul|video creator|try-on|video|real fabric movement)", re.IGNORECASE)
        self.canva_pattern = re.compile(r"(pinterest|canva|moodboard|collage|visualize|outfit inspo)", re.IGNORECASE)
        self.bracketing_pattern = re.compile(r"(buying 2 sizes|bracketing|order 2 sizes|return one)", re.IGNORECASE)

    def classify_intent(self, text: str, friction: RootFriction) -> WishlistIntent:
        if friction == RootFriction.PRICE_WAITING or self.price_pattern.search(text):
            return WishlistIntent.PRICE_SPECULATION
        elif friction == RootFriction.OCCASION_DISCONNECT or self.occasion_pattern.search(text):
            return WishlistIntent.AESTHETIC_BOOKMARKING
        elif friction == RootFriction.COMPARISON_PARALYSIS or self.comparison_pattern.search(text):
            return WishlistIntent.SHORTLIST_COMPARISON
        else:
            return WishlistIntent.GENUINE_PURCHASE_INTENT

    def classify_friction(self, text: str) -> RootFriction:
        # Priority matching based on signal specificity
        if self.styling_pattern.search(text):
            return RootFriction.STYLING_AND_PAIRABILITY_ANXIETY
        elif self.fit_pattern.search(text):
            return RootFriction.FIT_AND_SILHOUETTE_AMBIGUITY
        elif self.fabric_pattern.search(text):
            return RootFriction.FABRIC_AND_TACTILE_DOUBT
        elif self.social_pattern.search(text):
            return RootFriction.SOCIAL_VALIDATION_LAG
        elif self.comparison_pattern.search(text):
            return RootFriction.COMPARISON_PARALYSIS
        elif self.occasion_pattern.search(text):
            return RootFriction.OCCASION_DISCONNECT
        elif self.price_pattern.search(text):
            return RootFriction.PRICE_WAITING
        else:
            return RootFriction.STYLING_AND_PAIRABILITY_ANXIETY

    def classify_workaround(self, text: str, source: str) -> OfflineWorkaround:
        if self.whatsapp_pattern.search(text):
            return OfflineWorkaround.WHATSAPP_SHARING
        elif self.bracketing_pattern.search(text):
            return OfflineWorkaround.BRACKETING
        elif self.canva_pattern.search(text):
            return OfflineWorkaround.PINTEREST_CANVA_MOODBOARDING
        elif "YouTube" in source or self.youtube_pattern.search(text):
            return OfflineWorkaround.YOUTUBE_TRYON_SEARCH
        else:
            return OfflineWorkaround.NONE

    def classify_cohort(self, text: str, user_metadata: Dict[str, Any]) -> UserCohort:
        meta_cohort = user_metadata.get("cohort")
        if meta_cohort in [UserCohort.STUDENT_GEN_Z.value, UserCohort.WORKING_PROFESSIONAL.value, UserCohort.TIER_2_ASPIRATIONAL.value]:
            return UserCohort(meta_cohort)
        
        # Fallback to text heuristics
        if re.search(r"\b(college|hostel|roommate|brunch|casual)\b", text, re.IGNORECASE):
            return UserCohort.STUDENT_GEN_Z
        elif re.search(r"\b(office|workplace|workday|blazer|formal|work)\b", text, re.IGNORECASE):
            return UserCohort.WORKING_PROFESSIONAL
        else:
            return UserCohort.TIER_2_ASPIRATIONAL

    def process_record(self, record: Dict[str, Any]) -> ClassifiedRecord:
        text = record.get("normalized_text", record.get("raw_text", ""))
        source = record.get("source", "")
        metadata = record.get("user_metadata", {})

        friction = self.classify_friction(text)
        intent = self.classify_intent(text, friction)
        workaround = self.classify_workaround(text, source)
        cohort = self.classify_cohort(text, metadata)

        # Confidence calculation
        conf = 0.92
        if record.get("detected_slang_tags"):
            conf = 0.98

        return ClassifiedRecord(
            record_id=record["record_id"],
            source=record["source"],
            sub_source=record.get("sub_source", record["source"]),
            created_at=record["created_at"],
            rating=record["rating"],
            upvotes_or_likes=record["upvotes_or_likes"],
            apparel_category=record.get("apparel_category", "Unknown"),
            brand_mentioned=record.get("brand_mentioned", "Unknown"),
            user_metadata=metadata,
            raw_text=record["raw_text"],
            normalized_text=text,
            rqs_score=record.get("rqs_score", 0.8),
            detected_slang_tags=record.get("detected_slang_tags", []),
            intent=intent,
            friction=friction,
            workaround=workaround,
            cohort=cohort,
            confidence_score=conf
        )

if __name__ == "__main__":
    classifier = TaxonomyClassifier()
    sample = {
        "record_id": "voc_test_1",
        "source": "Reddit",
        "created_at": "2026-08-01",
        "rating": 4,
        "upvotes_or_likes": 20,
        "raw_text": "Saved this kurti 3 weeks ago in wishlist. Samajh nahi aa raha kiske saath pair karu.",
        "normalized_text": "Saved this kurti 3 weeks ago in wishlist. [STYLING_PAIRABILITY_ANXIETY].",
        "detected_slang_tags": ["STYLING_PAIRABILITY_ANXIETY"],
        "user_metadata": {"cohort": "WORKING_PROFESSIONAL"}
    }
    result = classifier.process_record(sample)
    print("Classified:", result.model_dump_json(indent=2))
