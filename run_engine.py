"""
Master Engine Orchestrator: Myntra VoC Discovery & Growth Intelligence Engine.
Executes the end-to-end pipeline:
Phase 1: Multi-Source 15K Ingestion & Resilience Generator
Phase 2: Pre-LLM Noise Filtration & Hinglish Normalization
Phase 3: 4-Dimensional Taxonomy Classification
Phase 4: Quantitative Opportunity Scoring & Friction Ranking
Phase 5: NextLeap Parts 1-7 Capstone Deliverables Generation
"""

import os
import sys
import time
import logging

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ingestion.orchestrator import IngestionOrchestrator
from src.pipeline.runner import run_phase_2
from src.classification.runner import run_phase_3
from src.analytics.opportunity_scorer import OpportunityScoringEngine
from src.generators.deliverables_builder import DeliverablesBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("MasterVoCEngine")

def run_full_pipeline():
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("🚀 STARTING MYNTRA VoC DISCOVERY & GROWTH INTELLIGENCE ENGINE")
    logger.info("   Target Metric: 30-Day Wishlist-to-Purchase Conversion Rate")
    logger.info("   Constraint   : STRICTLY ZERO MONETARY INCENTIVES")
    logger.info("   Corpus Scale : 15,000 Multi-Source Customer Feedback Records")
    logger.info("=" * 70)

    # Phase 1: Ingestion
    logger.info("\n>>> [PHASE 1] Executing Multi-Source Ingestion & Resilience Pipeline...")
    ingestion = IngestionOrchestrator(target_total=15000)
    raw_records = ingestion.run_ingestion()

    # Phase 2: Noise Filter & Normalization
    logger.info("\n>>> [PHASE 2] Executing Pre-LLM Noise Filtration & Hinglish Normalizer...")
    normalized_records = run_phase_2()

    # Phase 3: 4D Classification
    logger.info("\n>>> [PHASE 3] Executing 4-Dimensional Taxonomy Classification...")
    classification_summary = run_phase_3()

    # Phase 4: Opportunity Scoring
    logger.info("\n>>> [PHASE 4] Computing Quantitative Opportunity Scores & Ranking...")
    scorer = OpportunityScoringEngine()
    ranked_matrix = scorer.run_scoring()

    # Phase 5: PM Deliverables
    logger.info("\n>>> [PHASE 5] Synthesizing NextLeap Parts 1 to 7 Capstone Deliverables...")
    builder = DeliverablesBuilder()
    deliverables_doc = builder.build_all_deliverables()

    total_time = round(time.time() - start_time, 2)
    logger.info("=" * 70)
    logger.info("🎉 FULL END-TO-END PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    logger.info(f"   ⏱️ Total Execution Time: {total_time} seconds")
    logger.info("   📁 Raw Corpus File     : data/raw_15k_corpus.json")
    logger.info("   📁 Normalized Corpus   : data/normalized_corpus_15k.json")
    logger.info("   📁 Classified Corpus   : data/classified_corpus_15k.json")
    logger.info("   📁 Opportunity Matrix  : data/ranked_opportunity_matrix.json")
    logger.info("   📄 PM Capstone Report  : Docs/Part_1_to_7_NextLeap_Deliverables.md")
    logger.info("   🌐 Dashboard Running At: http://127.0.0.1:8000")
    logger.info("=" * 70)

    return {
        "status": "SUCCESS",
        "total_time_seconds": total_time,
        "raw_count": len(raw_records),
        "high_signal_count": len(normalized_records),
        "ranked_clusters": len(ranked_matrix)
    }

if __name__ == "__main__":
    run_full_pipeline()
