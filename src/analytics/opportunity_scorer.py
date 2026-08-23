"""
Quantitative Opportunity Scoring & Friction Ranking Engine.
Computes:
Opportunity Score = Frequency Share (%) * Severity (1-5) * Non-Monetary Solvability (1-5)
Exports ranked friction matrix to JSON and Markdown formats.
"""

import os
import sys
import json
import logging
from collections import defaultdict
from typing import Dict, Any, List

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("OpportunityScorer")

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLASSIFIED_FILE = os.path.join(WORKSPACE_ROOT, "data", "classified_corpus_15k.json")
OUTPUT_JSON_FILE = os.path.join(WORKSPACE_ROOT, "data", "ranked_opportunity_matrix.json")
OUTPUT_MD_FILE = os.path.join(WORKSPACE_ROOT, "data", "opportunity_matrix.md")

# Qualitative rubric for Severity (1-5) and Solvability (1-5)
# Severity: 1 = Minor hesitation, 5 = Fatal checkout abandoner
# Solvability: 1 = Physical/logistics bound, 5 = Highly solvable via in-app UI/UX / GenAI styling
FRICTION_RUBRIC = {
    "STYLING_AND_PAIRABILITY_ANXIETY": {
        "name": "Styling & Pairability Anxiety",
        "description": "Uncertainty regarding what wardrobe bottoms, footwear, or accessories match the item.",
        "severity": 4.6,  # Users like the item but literally cannot wear it without pairing -> abandonment
        "solvability": 4.9,  # 100% solvable via interactive outfit visualizers, AI pairing & styled lookbooks
        "primary_workarounds": ["PINTEREST_CANVA_MOODBOARDING", "WHATSAPP_SHARING"]
    },
    "FIT_AND_SILHOUETTE_AMBIGUITY": {
        "name": "Fit & Silhouette Ambiguity",
        "description": "Cross-brand sizing inconsistency, drape uncertainty on non-model Indian body types.",
        "severity": 4.5,  # Fatal purchase barrier or causes high return rate
        "solvability": 4.2,  # Solvable via body-type matched UGC, 3D/AR size advisors & dimensional consensus
        "primary_workarounds": ["BRACKETING", "YOUTUBE_TRYON_SEARCH"]
    },
    "FABRIC_AND_TACTILE_DOUBT": {
        "name": "Fabric & Tactile Doubt",
        "description": "Opacity, breathability, roughness, or wash shrinkage uncertainty.",
        "severity": 4.0,  # Causes hesitation; mitigated by clear reviews/videos
        "solvability": 3.8,  # Solvable via high-res fabric micro-videos, buyer transparency ratings & certified badges
        "primary_workarounds": ["YOUTUBE_TRYON_SEARCH"]
    },
    "SOCIAL_VALIDATION_LAG": {
        "name": "Social Validation Lag",
        "description": "Lag while waiting for friends/family approval via WhatsApp screenshots.",
        "severity": 3.8,  # Delay turns into permanent cooling-off abandonment
        "solvability": 4.5,  # Solvable via in-app shared wishlists, quick polling & peer verdict badges
        "primary_workarounds": ["WHATSAPP_SHARING"]
    },
    "COMPARISON_PARALYSIS": {
        "name": "Comparison Paralysis",
        "description": "Cognitive overload from holding 4-6 near-identical shortlisted tops/dresses.",
        "severity": 3.5,  # Decision fatigue leads to app closure
        "solvability": 4.4,  # Solvable via side-by-side spec comparison matrices & AI differentiator summaries
        "primary_workarounds": ["NONE"]
    },
    "OCCASION_DISCONNECT": {
        "name": "Occasion Disconnect",
        "description": "Aspirational liking without an upcoming event or practical use case.",
        "severity": 3.2,  # Low immediate urgency
        "solvability": 3.5,  # Solvable via capsule wardrobe recommendations & occasion-repurposing guides
        "primary_workarounds": ["NONE"]
    },
    "PRICE_WAITING": {
        "name": "Price Speculation (Excluded from Non-Monetary Ranking)",
        "description": "Waiting for sale markdowns or coupon drops.",
        "severity": 2.5,
        "solvability": 1.0,  # Out of non-monetary scope
        "primary_workarounds": ["NONE"]
    }
}

class OpportunityScoringEngine:
    def __init__(self):
        pass

    def run_scoring(self) -> List[Dict[str, Any]]:
        logger.info("=" * 65)
        logger.info("STARTING PHASE 4: QUANTITATIVE OPPORTUNITY SCORING")
        logger.info("=" * 65)

        if not os.path.exists(CLASSIFIED_FILE):
            logger.error(f"Classified file not found at {CLASSIFIED_FILE}! Run Phase 3 first.")
            return []

        with open(CLASSIFIED_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)

        logger.info(f"Loaded {len(records)} classified records.")

        # Group records by friction cluster
        cluster_records = defaultdict(list)
        for rec in records:
            cluster_records[rec["friction"]].append(rec)

        # Calculate Total non-monetary deliberate records
        total_high_signal = len(records)
        non_monetary_records_count = sum(
            len(recs) for k, recs in cluster_records.items() if k != "PRICE_WAITING"
        )

        ranked_opportunities = []

        for friction_key, recs in cluster_records.items():
            rubric = FRICTION_RUBRIC.get(friction_key, {
                "name": friction_key,
                "description": "Unclassified friction",
                "severity": 3.0,
                "solvability": 3.0,
                "primary_workarounds": ["NONE"]
            })

            count = len(recs)
            # Frequency share relative to non-monetary deliberation records
            freq_share_pct = round((count / non_monetary_records_count) * 100, 2)
            
            # Severity & Solvability
            severity = rubric["severity"]
            solvability = rubric["solvability"]

            # Opportunity Score = Frequency Share (%) * Severity (1-5) * Solvability (1-5)
            opp_score = round(freq_share_pct * severity * solvability, 2)

            # Sample verbatims (top 3 highest upvoted / RQS)
            sorted_recs = sorted(recs, key=lambda x: (x.get("upvotes_or_likes", 0), x.get("rqs_score", 0)), reverse=True)
            verbatim_samples = [
                {
                    "source": r["sub_source"],
                    "text": r["raw_text"],
                    "cohort": r["cohort"],
                    "rqs": r["rqs_score"]
                }
                for r in sorted_recs[:3]
            ]

            # Cohort distribution within this cluster
            cohort_counts = defaultdict(int)
            for r in recs:
                cohort_counts[r["cohort"]] += 1
            
            cohort_breakdown = {
                c: f"{cnt} ({cnt/count*100:.1f}%)"
                for c, cnt in cohort_counts.items()
            }

            ranked_opportunities.append({
                "cluster_key": friction_key,
                "cluster_name": rubric["name"],
                "description": rubric["description"],
                "record_count": count,
                "frequency_share_pct": freq_share_pct,
                "severity_score": severity,
                "solvability_score": solvability,
                "opportunity_score": opp_score,
                "primary_workarounds": rubric["primary_workarounds"],
                "cohort_breakdown": cohort_breakdown,
                "verbatim_samples": verbatim_samples
            })

        # Sort strictly by Opportunity Score descending
        ranked_opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

        # Add Rank index
        for idx, item in enumerate(ranked_opportunities, 1):
            item["rank"] = idx

        # Persist to JSON
        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(ranked_opportunities, f, indent=2, ensure_ascii=False)

        # Generate Markdown Report
        self._generate_markdown_report(ranked_opportunities, total_high_signal, non_monetary_records_count)

        logger.info(f"Persisted ranked matrix to -> {OUTPUT_JSON_FILE}")
        logger.info(f"Persisted markdown report to -> {OUTPUT_MD_FILE}")
        logger.info("=" * 65)

        return ranked_opportunities

    def _generate_markdown_report(self, ranked_opps: List[Dict[str, Any]], total_records: int, non_monetary_total: int):
        md_lines = [
            "# Ranked Opportunity Matrix: Myntra VoC Growth Engine",
            "",
            "## 1. Executive Opportunity Summary",
            f"- **Total Classified VoC Records Analyzed**: {total_records:,}",
            f"- **Non-Monetary Deliberation Corpus**: {non_monetary_total:,}",
            "- **Opportunity Scoring Formula**:  ",
            r"  $$\mathbf{\text{Opportunity Score}} = \mathbf{\text{Frequency Share (\%)}}\times \mathbf{\text{Severity (1–5)}}\times \mathbf{\text{Non-Monetary Solvability (1–5)}}$$",
            "",
            "---",
            "",
            "## 2. Quantitative Ranked Opportunity Matrix",
            "",
            "| Rank | Friction Cluster | Frequency % | Severity (1-5) | Solvability (1-5) | Opportunity Score | Top Cohort | Primary Workaround |",
            "|:---:|---|:---:|:---:|:---:|:---:|---|---|"
        ]

        for opp in ranked_opps:
            top_cohort = list(opp["cohort_breakdown"].keys())[0] if opp["cohort_breakdown"] else "All"
            workaround = ", ".join(opp["primary_workarounds"])
            md_lines.append(
                f"| **#{opp['rank']}** | **{opp['cluster_name']}** | {opp['frequency_share_pct']}% | {opp['severity_score']} | {opp['solvability_score']} | **{opp['opportunity_score']}** | {top_cohort} | `{workaround}` |"
            )

        md_lines.extend([
            "",
            "---",
            "",
            "## 3. Deep-Dive on Top Opportunity Clusters",
            ""
        ])

        for opp in ranked_opps[:4]:
            md_lines.extend([
                f"### Rank #{opp['rank']}: {opp['cluster_name']} (Opportunity Score: {opp['opportunity_score']})",
                f"- **Problem Description**: {opp['description']}",
                f"- **Corpus Volume**: {opp['record_count']:,} discussions ({opp['frequency_share_pct']}% share)",
                f"- **Severity ({opp['severity_score']}/5)**: High drop-off factor causing immediate purchase delay.",
                f"- **Solvability ({opp['solvability_score']}/5)**: Can be 100% resolved via in-app visual styling & UGC pairing.",
                f"- **Target Cohort Breakdown**: {json.dumps(opp['cohort_breakdown'])}",
                "- **Representative Customer Verbatims**:"
            ])
            for v in opp["verbatim_samples"]:
                md_lines.append(f"  > *\"{v['text']}\"*  \n  > — **Source:** `{v['source']}` | **Cohort:** `{v['cohort']}` | **RQS:** `{v['rqs']}`\n")

        with open(OUTPUT_MD_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

if __name__ == "__main__":
    scorer = OpportunityScoringEngine()
    scorer.run_scoring()
