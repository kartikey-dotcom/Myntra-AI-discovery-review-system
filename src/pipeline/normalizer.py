"""
Hinglish & Colloquial Fashion Slang Normalization Engine.
Translates unstructured, regional, and code-mixed Indian fashion phrases
into standardized canonical analytical tags.
"""

import re
from typing import Dict, Any, List, Tuple

CANONICAL_SLANG_MAPPINGS: List[Tuple[str, str, str]] = [
    # (Regex Pattern, Replacement Tag, Category Description)
    (
        r"(kapda\s*(patla|transparent|see[\s-]?through)|transparent\s*doubt|inner\s*slip\s*is\s*needed|see[\s-]?through)",
        "[FABRIC_TRANSPARENCY_DOUBT]",
        "Fabric opacity uncertainty"
    ),
    (
        r"(m\s*size\s*mango\s*ke\s*s\s*jaisa|sizing\s*is\s*so\s*unpredictable|size\s*chart\s*is\s*totally\s*confusing|mango\s*size\s*6\s*vs\s*zara\s*s)",
        "[CROSS_BRAND_SIZE_INCONSISTENCY]",
        "Discrepancy in sizing across brands"
    ),
    (
        r"(samajh\s*nahi\s*aa\s*raha\s*kiske\s*saath\s*pair\s*karu|no\s*idea\s*how\s*to\s*style|styling\s*confusion\s*is\s*real|what\s*color\s*bottoms\s*go|what\s*accessories\s*will\s*go|what\s*trousers\s*in\s*my\s*wardrobe)",
        "[STYLING_PAIRABILITY_ANXIETY]",
        "Lack of pairing and wardrobe integration confidence"
    ),
    (
        r"(model\s*is\s*5'10.*i\s*am\s*5'2|reach\s*my\s*ankles\s*instead\s*of\s*midi|model\s*pe\s*sahi\s*lagta\s*hai.*clown|broad\s*shoulders.*baggy\s*on\s*waist|curvy\s*body\s*type.*sit\s*weirdly)",
        "[SILHOUETTE_BODY_MISMATCH]",
        "Uncertainty of garment drape on non-model Indian body types"
    ),
    (
        r"(waiting\s*for\s*eors|sale\s*ke\s*liye\s*wishlist|track\s*discount|price\s*is\s*currently.*will\s*only\s*buy\s*if|coupon\s*\/\s*bank\s*discount)",
        "[PRICE_SPECULATION]",
        "Pure price waiting behavior"
    ),
    (
        r"(whatsapp\s*group|asked\s*in\s*whatsapp|second\s*opinion\s*from\s*my\s*sister|sent\s*the\s*myntra\s*link\s*to.*friends|waiting\s*for.*approv)",
        "[PEER_SOCIAL_VALIDATION_LAG]",
        "External offline friend/family validation loop"
    ),
    (
        r"(buying\s*2\s*sizes\s*and\s*returning\s*one|bracketing|shrinks\s*a\s*bit\s*after\s*wash)",
        "[BRACKETING_AND_SHRINKAGE_HEDGE]",
        "Ordering multiple sizes or hedging wash distortion"
    ),
    (
        r"(6\s*almost\s*identical|decision\s*fatigue|wishlist\s*has\s*20\s*items.*confused\s*between\s*3)",
        "[COMPARISON_PARALYSIS]",
        "Cognitive overload among shortlisted alternatives"
    ),
    (
        r"(nowhere\s*to\s*wear|future\s*goa\s*trip|aspirational\s*buy|no\s*immediate\s*plan)",
        "[OCCASION_DISCONNECT]",
        "Aspirational saving without real-world utility"
    )
]

class HinglishNormalizer:
    def __init__(self):
        self.compiled_rules = [
            (re.compile(pattern, re.IGNORECASE), replacement, desc)
            for pattern, replacement, desc in CANONICAL_SLANG_MAPPINGS
        ]

    def normalize_text(self, text: str) -> Tuple[str, List[str]]:
        """
        Replaces colloquial slang phrases with standardized analytical tags.
        Returns: (normalized_text, list_of_detected_tags)
        """
        normalized = text
        detected_tags = []
        
        for pattern, replacement, desc in self.compiled_rules:
            if pattern.search(normalized):
                detected_tags.append(replacement.strip("[]"))
                normalized = pattern.sub(replacement, normalized)

        return normalized, detected_tags

if __name__ == "__main__":
    normalizer = HinglishNormalizer()
    sample = "Saved this kurti 3 weeks ago in wishlist. Samajh nahi aa raha kiske saath pair karu. What color bottoms go with this?"
    norm_text, tags = normalizer.normalize_text(sample)
    print("Original:", sample)
    print("Normalized:", norm_text)
    print("Tags:", tags)
