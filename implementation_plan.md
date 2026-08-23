# Master Implementation Plan: Myntra VoC Discovery & Growth Intelligence Engine

This implementation plan outlines the engineering and analytics execution for the **Myntra VoC Discovery & Growth Intelligence Engine**, strictly adhering to the [problemStatement.md](file:///c:/Users/DELL/OneDrive/Desktop/Krishna/Myntra%20AI%20powered%20review%20discovery%20engine/problemStatement.md) and [Docs/architecture.md](file:///c:/Users/DELL/OneDrive/Desktop/Krishna/Myntra%20AI%20powered%20review%20discovery%20engine/Docs/architecture.md).

---

## Strict Constraints & Core Metric

> [!IMPORTANT]
> **1. Target Metric**: **30-Day Wishlist-to-Purchase Conversion Rate** (% of users purchasing $\ge 1$ item from wishlist within 30 days).  
> **2. Non-Negotiable Constraint**: **STRICTLY ZERO MONETARY INCENTIVES**. No discounts, coupons, price drop alerts, sale markdown push notifications, or cashback mechanics. All solutions must be purely psychological, informational, visual, or UX-driven.  
> **3. Corpus Scale**: **15,000+ customer records** across Play Store/App Store (10k), Reddit (3.5k), YouTube comments (1.5k), with a deterministic synthetic fail-safe generator.

---

## Phase-Wise Execution Roadmap

```mermaid
gantt
    title Myntra VoC Engine 7-Phase Execution Plan
    dateFormat  YYYY-MM-DD
    section Pipeline & Scaffolding
    Phase 1: 15K Multi-Source Ingestion & Fail-Safe Engine    :p1, 2026-08-24, 2d
    Phase 2: Pre-LLM Noise Filter & Hinglish Normalization   :p2, after p1, 2d
    section Classification & Analytics
    Phase 3: 4-Dimensional Taxonomy Classification Engine     :p3, after p2, 2d
    Phase 4: Opportunity Scoring & Ranked Friction Matrix    :p4, after p3, 2d
    section NextLeap Deliverables
    Phase 5: Automated Parts 1–7 Capstone Deliverables       :p5, after p4, 3d
    Phase 6: Interactive VoC Intelligence Dashboard UI       :p6, after p5, 2d
    section Verification & Audit
    Phase 7: End-to-End Execution, Testing & Capstone Audit  :p7, after p6, 2d
```

---

## Detailed Phase Breakdown & File Deliverables

### Phase 1: 15K Multi-Source Ingestion & Resilience Architecture
**Goal**: Build multi-channel scrapers and deterministic 15,000-record fallback generator matching real Indian fashion e-commerce distribution patterns.

#### [NEW] `data/synthetic_15k_corpus.py`
- Generates a statistically accurate 15,000-record dataset (Play Store: 10k, Reddit: 3.5k, YouTube: 1.5k) containing authentic Hinglish, sizing discrepancies, fit doubts, styling anxieties, and price speculation records.

#### [NEW] `src/ingestion/app_store_scraper.py`
- Scrapes reviews from `com.myntra.android` filtering on keywords (`wishlist`, `saved`, `fit`, `size`, `styling`, `pair`, `fabric`).

#### [NEW] `src/ingestion/reddit_scraper.py`
- Reddit crawler extracting discussions from `r/IndianFashionAddicts`, `r/TwoXIndia`, `r/delhi`, `r/bangalore`.

#### [NEW] `src/ingestion/youtube_scraper.py`
- Comment extractor from top 50 Myntra try-on and haul videos.

---

### Phase 2: Pre-LLM Noise Filtration & Hinglish Normalization Engine
**Goal**: Strip off-topic non-fashion noise (logistics, OTPs, refunds) to condense 15k records into ~3,500 high-signal deliberation records and normalize colloquial Indian fashion slang.

#### [NEW] `src/pipeline/noise_filter.py`
- Drops delivery agent complaints, courier delays, refund processing tickets, OTP bugs, and 1-word spam reviews. Computes Review Quality Score (RQS).

#### [NEW] `src/pipeline/normalizer.py`
- Standardizes colloquial terms (`"Kapda transparent"`, `"Roadster ka M size Mango ke S jaisa"`, `"Samajh nahi aa raha kiske saath pair karu"`, `"Model pe sahi lagta hai..."`).

#### [NEW] `data/normalized_corpus_15k.json`
- Cleaned, normalized, high-signal deliberation dataset.

---

### Phase 3: 4-Dimensional Taxonomy Classification Engine
**Goal**: Classify each deliberation record across the 4 orthogonal dimensions.

#### [NEW] `src/classification/taxonomy_classifier.py`
- **Dim 1 (Wishlist Intent)**: `GENUINE_PURCHASE_INTENT`, `AESTHETIC_BOOKMARKING`, `SHORTLIST_COMPARISON`, `PRICE_SPECULATION`.
- **Dim 2 (Root Friction)**: `FIT_AND_SILHOUETTE_AMBIGUITY`, `STYLING_AND_PAIRABILITY_ANXIETY`, `FABRIC_AND_TACTILE_DOUBT`, `SOCIAL_VALIDATION_LAG`, `OCCASION_DISCONNECT`, `COMPARISON_PARALYSIS`.
- **Dim 3 (Offline Workaround)**: `WHATSAPP_SHARING`, `YOUTUBE_TRYON_SEARCH`, `PINTEREST_CANVA_MOODBOARDING`, `BRACKETING`.
- **Dim 4 (User Cohort)**: `STUDENT_GEN_Z`, `WORKING_PROFESSIONAL`, `TIER_2_ASPIRATIONAL`.

---

### Phase 4: Opportunity Scoring & Ranked Friction Matrix
**Goal**: Quantify friction barriers using the scientific formula $\text{Opportunity Score} = \text{Freq \%} \times \text{Severity (1-5)} \times \text{Solvability (1-5)}$.

#### [NEW] `src/analytics/opportunity_scorer.py`
- Aggregates frequency share, assigns severity and non-monetary solvability scores, and ranks friction clusters.

#### [NEW] `data/ranked_opportunity_matrix.json` & `data/opportunity_matrix.md`
- Export of the ranked opportunity table with verbatims and cross-tabulations.

---

### Phase 5: Automated Parts 1 to 7 NextLeap Capstone Deliverables
**Goal**: Generate the comprehensive PM deliverable suite based on VoC analytics.

#### [NEW] `src/generators/deliverables_builder.py`
- Generates:
  1. **Part 1**: NextLeap 10-Question Discovery Audit.
  2. **Part 2**: 30-Day Wishlist-to-Purchase Funnel Metric Decomposition Tree.
  3. **Part 3**: 5 Primary Qualitative User Personas with discussion interview guides.
  4. **Part 4**: Root-Cause PM Problem Statement (Business Metric $\rightarrow$ Product Outcome $\rightarrow$ Root Cause).
  5. **Part 5**: MVP Product Specification for #1 Opportunity (Myntra "StyleStudio" Outfit Visualizer & Body-Matched UGC Carousel).
  6. **Part 6**: L1/L2 Metrics, Leading Behavioral Indicators, and Guardrail Metrics.
  7. **Part 7**: Top 4 Failure Modes, Edge Cases, and Risk Mitigation Matrix.

#### [NEW] `Docs/Part_1_to_7_NextLeap_Deliverables.md`
- Complete consolidated PM capstone report.

---

### Phase 6: Interactive VoC Intelligence Dashboard UI
**Goal**: Provide a rich, interactive web UI to explore the 15,000 corpus, filter by 4D taxonomy, view the opportunity scoreboard, and interact with the StyleStudio MVP simulator.

#### [NEW] `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`
- Interactive VoC Explorer, 4D Distribution Charts, Opportunity Matrix visualizer, and NextLeap Deliverables Hub.

---

### Phase 7: Full Pipeline Execution, Verification & Capstone Audit
**Goal**: Execute the end-to-end pipeline, validate the 15k processing run, and verify all constraints.

#### Verification Suite:
- Run `python run_engine.py` to process the 15k dataset.
- Verify 100% compliance with ZERO monetary incentives rule.
- Verify all 10 questions of the NextLeap Discovery Audit are answered with quantitative backing.
- Verify generated deliverables and launch dashboard on local port.

---
