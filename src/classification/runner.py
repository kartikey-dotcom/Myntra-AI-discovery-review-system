"""
Phase 3 Classification Runner.
Classifies high-signal VoC corpus across 4 orthogonal dimensions:
1. Wishlist Intent
2. Non-Monetary Root Friction
3. Offline Workarounds
4. User Cohort
Persists to data/classified_corpus_15k.json.
"""

import os
import sys
import json
import logging
from collections import Counter
from typing import Dict, Any, List

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.classification.taxonomy_classifier import TaxonomyClassifier
from src.classification.taxonomy import ClassifiedRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Phase3ClassificationRunner")

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NORMALIZED_FILE = os.path.join(WORKSPACE_ROOT, "data", "normalized_corpus_15k.json")
CLASSIFIED_OUTPUT_FILE = os.path.join(WORKSPACE_ROOT, "data", "classified_corpus_15k.json")
SUMMARY_REPORT_FILE = os.path.join(WORKSPACE_ROOT, "data", "classification_summary.json")

def run_phase_3():
    logger.info("=" * 65)
    logger.info("STARTING PHASE 3: 4-DIMENSIONAL TAXONOMY CLASSIFICATION")
    logger.info("=" * 65)

    if not os.path.exists(NORMALIZED_FILE):
        logger.error(f"Normalized corpus not found at {NORMALIZED_FILE}! Run Phase 2 first.")
        return

    with open(NORMALIZED_FILE, "r", encoding="utf-8") as f:
        normalized_records = json.load(f)

    logger.info(f"Loaded {len(normalized_records)} high-signal records for classification.")

    classifier = TaxonomyClassifier()
    classified_records: List[Dict[str, Any]] = []

    intent_counter = Counter()
    friction_counter = Counter()
    workaround_counter = Counter()
    cohort_counter = Counter()
    cohort_friction_crosstab: Dict[str, Counter] = {
        "STUDENT_GEN_Z": Counter(),
        "WORKING_PROFESSIONAL": Counter(),
        "TIER_2_ASPIRATIONAL": Counter()
    }

    for rec in normalized_records:
        classified: ClassifiedRecord = classifier.process_record(rec)
        record_dict = classified.model_dump()
        classified_records.append(record_dict)

        intent_counter[classified.intent.value] += 1
        friction_counter[classified.friction.value] += 1
        workaround_counter[classified.workaround.value] += 1
        cohort_counter[classified.cohort.value] += 1
        cohort_friction_crosstab[classified.cohort.value][classified.friction.value] += 1

    # Persist Classified Corpus
    with open(CLASSIFIED_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(classified_records, f, indent=2, ensure_ascii=False)

    # Generate Summary Metrics
    total = len(classified_records)
    summary = {
        "total_records_classified": total,
        "dimension_1_intent_distribution": {
            k: {"count": v, "percentage": round(v / total * 100, 2)}
            for k, v in intent_counter.most_common()
        },
        "dimension_2_root_friction_distribution": {
            k: {"count": v, "percentage": round(v / total * 100, 2)}
            for k, v in friction_counter.most_common()
        },
        "dimension_3_offline_workarounds": {
            k: {"count": v, "percentage": round(v / total * 100, 2)}
            for k, v in workaround_counter.most_common()
        },
        "dimension_4_cohort_distribution": {
            k: {"count": v, "percentage": round(v / total * 100, 2)}
            for k, v in cohort_counter.most_common()
        },
        "cohort_friction_breakdown": {
            cohort: {
                friction: {"count": cnt, "pct_within_cohort": round(cnt / sum(crosstab.values()) * 100, 2)}
                for friction, cnt in crosstab.most_common()
            }
            for cohort, crosstab in cohort_friction_crosstab.items()
        }
    }

    with open(SUMMARY_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info("=" * 65)
    logger.info("PHASE 3 CLASSIFICATION COMPLETE:")
    logger.info(f"Total Classified Records: {total}")
    logger.info("\n--- DIMENSION 1: WISHLIST BEHAVIORAL INTENT ---")
    for k, v in summary["dimension_1_intent_distribution"].items():
        logger.info(f"  {k:30s}: {v['count']:5d} ({v['percentage']}%)")

    logger.info("\n--- DIMENSION 2: NON-MONETARY ROOT FRICTION ---")
    for k, v in summary["dimension_2_root_friction_distribution"].items():
        logger.info(f"  {k:35s}: {v['count']:5d} ({v['percentage']}%)")

    logger.info("\n--- DIMENSION 3: OFFLINE USER WORKAROUNDS ---")
    for k, v in summary["dimension_3_offline_workarounds"].items():
        logger.info(f"  {k:30s}: {v['count']:5d} ({v['percentage']}%)")

    logger.info("\n--- DIMENSION 4: TARGET USER COHORTS ---")
    for k, v in summary["dimension_4_cohort_distribution"].items():
        logger.info(f"  {k:25s}: {v['count']:5d} ({v['percentage']}%)")

    logger.info(f"\nPersisted classified corpus to: {CLASSIFIED_OUTPUT_FILE}")
    logger.info(f"Persisted summary report to   : {SUMMARY_REPORT_FILE}")
    logger.info("=" * 65)

    return summary

if __name__ == "__main__":
    run_phase_3()
