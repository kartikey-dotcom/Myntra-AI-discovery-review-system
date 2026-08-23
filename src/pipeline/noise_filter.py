"""
Pre-LLM Noise Filter & Review Quality Scoring (RQS) Engine.
Filters out off-topic logistics complaints, courier delays, refund tickets, OTP bugs,
and low-effort spam reviews to isolate high-signal fashion deliberation records.
"""

import re
from typing import Dict, Any, Tuple

# Patterns identifying off-topic logistics/technical noise
LOGISTICS_NOISE_PATTERNS = [
    r"\b(delivery\s*(boy|guy|agent|service|partner)|courier|delayed|shipping|fast\s*shipping|package\s*neat)\b",
    r"\b(refund|bank\s*account|customer\s*care|executive|payment\s*gateway|flipkart|hang)\b",
    r"\b(otp|login\s*bug|app\s*crashing|android|update|install)\b",
    r"\b(wrong\s*item\s*delivered|wrong\s*color\s*delivered|return\s*pick\s*up)\b"
]

# Patterns indicating high-signal fashion deliberation (wishlist, sizing, fit, styling, fabric)
FASHION_SIGNAL_PATTERNS = [
    r"\b(wishlist|saved|hesitat|confus|decid|delay|lingering|sitting)\b",
    r"\b(pair|style|styling|outfit|wardrobe|bottom|trousers|skirt|sneakers|heels|accessories)\b",
    r"\b(fit|size|sizing|tight|loose|baggy|chest|bust|waist|shoulder|drape|silhouette|petite|tall|curvy|ankle)\b",
    r"\b(fabric|cotton|polyester|linen|viscose|transparent|patla|see-through|breathable|shrink|bleed|itchy|lining)\b",
    r"\b(whatsapp|screenshot|friends?|sister|roommate|opinion|verdict|approve)\b",
    r"\b(occasion|wedding|brunch|office|festive|party|goa)\b",
    r"\b(compare|comparing|similar|identical|fatigue)\b"
]

class NoiseFilter:
    def __init__(self):
        self.noise_regex = re.compile("|".join(LOGISTICS_NOISE_PATTERNS), re.IGNORECASE)
        self.fashion_regex = re.compile("|".join(FASHION_SIGNAL_PATTERNS), re.IGNORECASE)

    def calculate_rqs(self, text: str, rating: int, upvotes: int) -> float:
        """
        Computes Review Quality Score (RQS) between 0.0 and 1.0 based on:
        - Word count and substantive length (up to 0.40)
        - Fashion deliberation keyword matches (up to 0.40)
        - Community validation / upvotes (up to 0.20)
        """
        words = text.strip().split()
        word_count = len(words)
        
        # 1. Length score
        if word_count < 4:
            length_score = 0.05
        elif word_count < 10:
            length_score = 0.20
        elif word_count < 25:
            length_score = 0.35
        else:
            length_score = 0.40

        # 2. Fashion deliberation signal density
        matches = len(self.fashion_regex.findall(text))
        signal_score = min(matches * 0.12, 0.40)

        # 3. Community validation score
        vote_score = min(upvotes / 100.0 * 0.20, 0.20)

        rqs = round(length_score + signal_score + vote_score, 3)
        return min(max(rqs, 0.0), 1.0)

    def evaluate_record(self, record: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Evaluates a raw VoC record.
        Returns: (is_high_signal: bool, rqs_score: float, rejection_reason: str)
        """
        text = record.get("raw_text", "").strip()
        rating = record.get("rating", 3)
        upvotes = record.get("upvotes_or_likes", 0)

        # Rule 1: Very short / 1-word spam filter
        words = text.split()
        if len(words) <= 3:
            return False, 0.10, "SPAM_TOO_SHORT"

        # Rule 2: Pure logistics / app bugs / refund complaint
        if self.noise_regex.search(text) and not self.fashion_regex.search(text):
            return False, 0.15, "LOGISTICS_OR_TECHNICAL_NOISE"

        # Rule 3: Compute RQS
        rqs = self.calculate_rqs(text, rating, upvotes)
        
        # Must meet minimum deliberation threshold
        if rqs >= 0.35 and self.fashion_regex.search(text):
            return True, rqs, "HIGH_SIGNAL_DELIBERATION"
        else:
            return False, rqs, "LOW_DELIBERATION_SIGNAL"

if __name__ == "__main__":
    filter_engine = NoiseFilter()
    sample_text = "Saved this kurti 3 weeks ago in wishlist. Samajh nahi aa raha kiske saath pair karu. What color bottoms go with this?"
    is_signal, score, reason = filter_engine.evaluate_record({"raw_text": sample_text, "rating": 3, "upvotes_or_likes": 25})
    print(f"Signal: {is_signal}, Score: {score}, Reason: {reason}")
