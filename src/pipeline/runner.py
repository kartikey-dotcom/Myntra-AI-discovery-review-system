"""
Phase 2 Pipeline Runner: Pre-LLM Noise Filtration & Normalization Orchestrator.
Processes raw 15,000-record VoC corpus -> Filters non-fashion noise ->
Normalizes Hinglish fashion expressions -> Exports high-signal deliberation dataset.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.pipeline.noise_filter import NoiseFilter
from src.pipeline.normalizer import HinglishNormalizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Phase2PipelineRunner")

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_CORPUS_FILE = os.path.join(WORKSPACE_ROOT, "data", "raw_15k_corpus.json")
NORMALIZED_OUTPUT_FILE = os.path.join(WORKSPACE_ROOT, "data", "normalized_corpus_15k.json")

def run_phase_2():
    logger.info("=" * 65)
    logger.info("STARTING PHASE 2: NOISE FILTRATION & HINGLISH NORMALIZATION")
    logger.info("=" * 65)

    if not os.path.exists(RAW_CORPUS_FILE):
        logger.error(f"Raw corpus not found at {RAW_CORPUS_FILE}! Run Phase 1 first.")
        return

    with open(RAW_CORPUS_FILE, "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    logger.info(f"Loaded {len(raw_records)} raw records from {RAW_CORPUS_FILE}")

    noise_filter = NoiseFilter()
    normalizer = HinglishNormalizer()

    high_signal_records: List[Dict[str, Any]] = []
    discarded_stats: Dict[str, int] = {}
    channel_counts: Dict[str, int] = {}

    for record in raw_records:
        is_signal, rqs, reason = noise_filter.evaluate_record(record)
        
        if is_signal:
            raw_text = record.get("raw_text", "")
            norm_text, tags = normalizer.normalize_text(raw_text)

            enriched_record = {
                "record_id": record["record_id"],
                "source": record["source"],
                "sub_source": record["sub_source"],
                "created_at": record["created_at"],
                "rating": record["rating"],
                "upvotes_or_likes": record["upvotes_or_likes"],
                "apparel_category": record.get("apparel_category", "Unknown"),
                "brand_mentioned": record.get("brand_mentioned", "Unknown"),
                "user_metadata": record.get("user_metadata", {}),
                "raw_text": raw_text,
                "normalized_text": norm_text,
                "rqs_score": rqs,
                "detected_slang_tags": tags
            }
            high_signal_records.append(enriched_record)
            channel = record["source"].split("(")[0].strip()
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        else:
            discarded_stats[reason] = discarded_stats.get(reason, 0) + 1

    # Persist Normalized High-Signal Corpus
    with open(NORMALIZED_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(high_signal_records, f, indent=2, ensure_ascii=False)

    logger.info("=" * 65)
    logger.info(f"PHASE 2 EXECUTION SUMMARY:")
    logger.info(f"Total Raw Records Processed : {len(raw_records)}")
    logger.info(f"Discarded Noise Records     : {len(raw_records) - len(high_signal_records)}")
    logger.info(f"High-Signal Records Retained : {len(high_signal_records)} ({len(high_signal_records)/len(raw_records)*100:.1f}%)")
    logger.info(f"Discard Reasons Breakdown   : {discarded_stats}")
    logger.info(f"Retained Channel Distribution: {channel_counts}")
    logger.info(f"Normalized Corpus Saved To  : {NORMALIZED_OUTPUT_FILE}")
    logger.info("=" * 65)

    return high_signal_records

if __name__ == "__main__":
    run_phase_2()
