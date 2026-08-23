"""
Unit and Integration Tests for Pipeline Components.
"""

import os
import sys
import unittest

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.noise_filter import NoiseFilter
from src.pipeline.normalizer import HinglishNormalizer
from src.classification.taxonomy_classifier import TaxonomyClassifier
from src.classification.taxonomy import WishlistIntent, RootFriction, OfflineWorkaround, UserCohort

class TestVoCPipeline(unittest.TestCase):
    def setUp(self):
        self.noise_filter = NoiseFilter()
        self.normalizer = HinglishNormalizer()
        self.classifier = TaxonomyClassifier()

    def test_noise_filter_logistics(self):
        noisy_rec = {
            "raw_text": "Delivery boy was very rude and courier service was delayed by 5 days. Refund not received.",
            "rating": 1,
            "upvotes_or_likes": 0
        }
        is_signal, rqs, reason = self.noise_filter.evaluate_record(noisy_rec)
        self.assertFalse(is_signal)
        self.assertEqual(reason, "LOGISTICS_OR_TECHNICAL_NOISE")

    def test_noise_filter_spam_short(self):
        spam_rec = {"raw_text": "Nice product.", "rating": 5, "upvotes_or_likes": 0}
        is_signal, rqs, reason = self.noise_filter.evaluate_record(spam_rec)
        self.assertFalse(is_signal)
        self.assertEqual(reason, "SPAM_TOO_SHORT")

    def test_noise_filter_high_signal(self):
        valid_rec = {
            "raw_text": "Wishlisted this kurti for office wear, but I have no idea how to style it without looking too casual. Still sitting in saved items.",
            "rating": 3,
            "upvotes_or_likes": 45
        }
        is_signal, rqs, reason = self.noise_filter.evaluate_record(valid_rec)
        self.assertTrue(is_signal)
        self.assertGreaterEqual(rqs, 0.40)

    def test_hinglish_normalizer(self):
        text = "Kapda transparent hai and samajh nahi aa raha kiske saath pair karu."
        normalized, tags = self.normalizer.normalize_text(text)
        self.assertIn("FABRIC_TRANSPARENCY_DOUBT", tags)
        self.assertIn("STYLING_PAIRABILITY_ANXIETY", tags)
        self.assertIn("[FABRIC_TRANSPARENCY_DOUBT]", normalized)
        self.assertIn("[STYLING_PAIRABILITY_ANXIETY]", normalized)

    def test_taxonomy_classifier_styling(self):
        rec = {
            "record_id": "test_01",
            "source": "Reddit",
            "created_at": "2026-08-01",
            "rating": 4,
            "upvotes_or_likes": 30,
            "raw_text": "Wishlisted 5 tops, still haven't bought bcz I don't know how to style them with trousers.",
            "normalized_text": "Wishlisted 5 tops, still haven't bought bcz [STYLING_PAIRABILITY_ANXIETY] with trousers.",
            "detected_slang_tags": ["STYLING_PAIRABILITY_ANXIETY"],
            "user_metadata": {"cohort": "WORKING_PROFESSIONAL"}
        }
        classified = self.classifier.process_record(rec)
        self.assertEqual(classified.friction, RootFriction.STYLING_AND_PAIRABILITY_ANXIETY)
        self.assertEqual(classified.intent, WishlistIntent.GENUINE_PURCHASE_INTENT)
        self.assertEqual(classified.cohort, UserCohort.WORKING_PROFESSIONAL)

    def test_taxonomy_classifier_workaround(self):
        rec = {
            "record_id": "test_02",
            "source": "Google Play Store",
            "created_at": "2026-08-01",
            "rating": 3,
            "upvotes_or_likes": 12,
            "raw_text": "Wishlisted this dress and shared screenshot on our girlies WhatsApp group for second opinion.",
            "normalized_text": "Wishlisted this dress and shared screenshot on our girlies WhatsApp group for [PEER_SOCIAL_VALIDATION_LAG].",
            "detected_slang_tags": ["PEER_SOCIAL_VALIDATION_LAG"],
            "user_metadata": {"cohort": "STUDENT_GEN_Z"}
        }
        classified = self.classifier.process_record(rec)
        self.assertEqual(classified.workaround, OfflineWorkaround.WHATSAPP_SHARING)

if __name__ == "__main__":
    unittest.main()
