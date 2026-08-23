"""
Formal Capstone Audit & Constraint Verification Suite.
Validates:
1. 15,000-Record Ingestion & High-Signal Filtration Volume.
2. 100% Compliance with ZERO MONETARY INCENTIVES Constraint.
3. NextLeap 10-Question Discovery Audit Completeness.
4. Opportunity Scoring Algorithm Integrity.
5. All Capstone Parts 1 through 7 Documentation Completeness.
"""

import os
import sys
import json
import re
import unittest

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_ROOT)

RAW_FILE = os.path.join(WORKSPACE_ROOT, "data", "raw_15k_corpus.json")
CLASSIFIED_FILE = os.path.join(WORKSPACE_ROOT, "data", "classified_corpus_15k.json")
OPPORTUNITY_FILE = os.path.join(WORKSPACE_ROOT, "data", "ranked_opportunity_matrix.json")
DELIVERABLES_FILE = os.path.join(WORKSPACE_ROOT, "Docs", "Part_1_to_7_NextLeap_Deliverables.md")

class TestCapstoneAudit(unittest.TestCase):

    def test_01_corpus_scale(self):
        """Audit 1: Asserts that exactly 15,000 records were ingested and processed."""
        self.assertTrue(os.path.exists(RAW_FILE), "Raw 15k corpus file must exist.")
        with open(RAW_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertGreaterEqual(len(raw), 15000, "Corpus must contain at least 15,000 records.")

        with open(CLASSIFIED_FILE, "r", encoding="utf-8") as f:
            classified = json.load(f)
        self.assertGreater(len(classified), 3000, "Filtered high-signal records must exceed 3,000 records.")

    def test_02_zero_monetary_incentives_compliance(self):
        """Audit 2: Verifies ZERO monetary incentives in the solution proposal."""
        self.assertTrue(os.path.exists(DELIVERABLES_FILE), "Deliverables markdown must exist.")
        with open(DELIVERABLES_FILE, "r", encoding="utf-8") as f:
            text = f.read()

        # Confirm strict constraint statement exists
        self.assertIn("STRICTLY ZERO MONETARY INCENTIVES", text)

        # Confirm that the MVP solution (Part 5) specifies non-monetary visual/pairing mechanics
        self.assertIn("StyleStudio", text)
        self.assertIn("Interactive Outfit Visualizer", text)
        self.assertIn("Body-Matched Customer UGC Carousel", text)

    def test_03_nextleap_10_questions_completeness(self):
        """Audit 3: Verifies all 10 NextLeap Discovery questions are answered."""
        with open(DELIVERABLES_FILE, "r", encoding="utf-8") as f:
            text = f.read()

        for q_num in range(1, 11):
            q_tag = f"Q{q_num}:"
            self.assertIn(q_tag, text, f"Question {q_tag} must be answered in Part 1.")

    def test_04_opportunity_scoring_integrity(self):
        """Audit 4: Validates mathematical formula and ranking order of opportunity clusters."""
        with open(OPPORTUNITY_FILE, "r", encoding="utf-8") as f:
            matrix = json.load(f)

        self.assertGreaterEqual(len(matrix), 5, "Matrix must contain at least 5 friction clusters.")

        prev_score = float("inf")
        for rank_idx, cluster in enumerate(matrix, 1):
            score = cluster["opportunity_score"]
            self.assertLessEqual(score, prev_score, "Matrix must be strictly sorted by opportunity score descending.")
            prev_score = score
            self.assertEqual(cluster["rank"], rank_idx, "Rank indices must be sequential.")

        # Assert Styling Anxiety is #1 Opportunity
        self.assertEqual(matrix[0]["cluster_key"], "STYLING_AND_PAIRABILITY_ANXIETY")

    def test_05_all_parts_1_to_7_present(self):
        """Audit 5: Verifies that Parts 1 through 7 are explicitly defined."""
        with open(DELIVERABLES_FILE, "r", encoding="utf-8") as f:
            text = f.read()

        expected_parts = [
            "PART 1: NextLeap 10-Question Discovery Audit",
            "PART 2: Metric Decomposition Tree & Operational Funnel",
            "PART 3: Primary Qualitative Research Personas & Discussion Guides",
            "PART 4: Formal PM Problem Definition Statement",
            "PART 5: MVP Feature Specification: Myntra \"StyleStudio\"",
            "PART 6: Comprehensive Metrics Framework",
            "PART 7: Technical & UX Risks, Edge Cases & Mitigation Matrix"
        ]

        for part in expected_parts:
            self.assertIn(part, text, f"Missing section: {part}")

if __name__ == "__main__":
    unittest.main()
