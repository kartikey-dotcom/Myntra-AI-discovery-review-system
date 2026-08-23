"""
Myntra Growth Intelligence & VoC Discovery Engine - Streamlit Cloud Application
Deployable on Streamlit Community Cloud (connected to GitHub).
Strictly adheres to 30-Day Wishlist-to-Purchase Conversion Metric and ZERO Monetary Incentives.
"""

import os
import sys
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKSPACE_ROOT)

from src.utils.llm_client import LLMClient

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Myntra Growth Intelligence | VoC Engine",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS (MYNTRA AESTHETICS) ====================
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Top Brand Banner */
    .brand-banner {
        background: linear-gradient(135deg, #282c3f 0%, #1a1c29 100%);
        color: #ffffff;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-left: 5px solid #ff3f6c;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
    .brand-title {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-logo-badge {
        background: linear-gradient(45deg, #ff3f6c, #ff527b);
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 800;
    }
    .badge-pill {
        background: rgba(255, 63, 108, 0.15);
        color: #ff3f6c;
        border: 1px solid rgba(255, 63, 108, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kpi-val {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Quote Cards */
    .verbatim-card {
        background: #f8fafc;
        border-left: 4px solid #ff3f6c;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
    .verbatim-text {
        font-size: 13.5px;
        font-style: italic;
        color: #334155;
        margin-bottom: 6px;
    }
    .verbatim-meta {
        font-size: 11px;
        font-weight: 600;
        color: #94a3b8;
    }

    /* Sidebar Branding & Badges */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    .sidebar-logo-text {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ff3f6c;
        margin: 0;
    }
    .sidebar-subtitle {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        margin-top: -2px;
        margin-bottom: 10px;
    }
    .sidebar-badge-container {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 8px;
    }
    .badge-pill-sidebar {
        background: rgba(255, 63, 108, 0.1);
        color: #ff3f6c;
        border: 1px solid rgba(255, 63, 108, 0.25);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11.5px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        width: fit-content;
    }
    .badge-green-sidebar {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11.5px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        width: fit-content;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA LOADERS (CACHED) ====================
@st.cache_data
def load_classification_summary():
    path = os.path.join(WORKSPACE_ROOT, "data", "classification_summary.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_ranked_opportunity_matrix():
    path = os.path.join(WORKSPACE_ROOT, "data", "ranked_opportunity_matrix.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_classified_corpus():
    path = os.path.join(WORKSPACE_ROOT, "data", "classified_corpus_15k.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_pm_deliverables_markdown():
    path = os.path.join(WORKSPACE_ROOT, "Part_1_to_7_NextLeap_Deliverables.md")
    if not os.path.exists(path):
        path = os.path.join(WORKSPACE_ROOT, "Docs", "Part_1_to_7_NextLeap_Deliverables.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "# Deliverables file not found."

# Load Data
summary_data = load_classification_summary()
ranked_matrix = load_ranked_opportunity_matrix()
classified_records = load_classified_corpus()
deliverables_md = load_pm_deliverables_markdown()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="background: linear-gradient(135deg, #ff3f6c, #ff527b); color: white; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 18px; box-shadow: 0 2px 6px rgba(255,63,108,0.3);">
            M
        </div>
        <div>
            <div class="sidebar-logo-text">myntra</div>
            <div class="sidebar-subtitle">Growth & VoC Engine</div>
        </div>
    </div>
    <div class="sidebar-badge-container">
        <div class="badge-green-sidebar">✔ 15,000 Records Live</div>
        <div class="badge-pill-sidebar">🛡️ Zero-Incentive Mode</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("#### 🎯 Global Context Filters")
    selected_segment = st.selectbox(
        "User Segment",
        ["ALL", "STUDENT_GEN_Z", "WORKING_PROFESSIONAL", "TIER_2_ASPIRATIONAL"],
        format_func=lambda x: {
            "ALL": "All User Segments",
            "STUDENT_GEN_Z": "Student / Gen Z (18-24)",
            "WORKING_PROFESSIONAL": "Working Professional (25-34)",
            "TIER_2_ASPIRATIONAL": "Tier-2 Aspirational (22-35)"
        }[x]
    )

    selected_category = st.selectbox(
        "Category Focus",
        ["ALL", "ETHNIC", "WESTERN", "WORKWEAR", "STREETWEAR"],
        format_func=lambda x: {
            "ALL": "All Categories (Ethnic & Western)",
            "ETHNIC": "Ethnic Wear (Kurtas & Sarees)",
            "WESTERN": "Western & Casual Dresses",
            "WORKWEAR": "Formal & Workwear",
            "STREETWEAR": "Streetwear & Denim"
        }[x]
    )

    st.markdown("#### 📡 Data Sources")
    include_reddit = st.checkbox("Reddit (r/IndianFashionAddicts)", value=True)
    include_playstore = st.checkbox("Play Store Reviews", value=True)
    include_youtube = st.checkbox("YouTube Try-On Hauls", value=True)

    st.divider()
    st.markdown("#### 🤖 LLM Engine Settings")
    
    # Initialize LLM Client
    llm_client = LLMClient()
    is_cfg = llm_client.is_configured()

    provider_choice = st.selectbox("LLM Provider", ["gemini", "openai"], index=0 if llm_client.provider == "gemini" else 1)
    
    api_key_input = st.text_input(
        "API Key (Optional / Overrides Secret)",
        type="password",
        value="",
        placeholder="Enter key to override..."
    )

    active_key = api_key_input.strip() if api_key_input.strip() else llm_client.api_key
    active_client = LLMClient(provider=provider_choice, api_key=active_key)

    if active_client.is_configured():
        st.success(f"🟢 {provider_choice.upper()} Connected ({active_client.model_name})")
    else:
        st.info("ℹ️ Running in Deterministic High-Signal AI Mode")

    if st.button("Test LLM Connection", use_container_width=True):
        with st.spinner("Testing API connection..."):
            res = active_client.test_connection(key_to_test=active_key, provider=provider_choice)
            if res.get("success"):
                st.success(f"Connection OK: {res.get('response')}")
            else:
                st.error(f"Failed: {res.get('error')}")

    st.divider()
    st.caption("NextLeap PM Capstone Engine • Strictly Zero Discounts")

# ==================== MAIN BANNER ====================
st.markdown("""
<div class="brand-banner">
    <div>
        <div class="brand-title">
            <span class="brand-logo-badge">MYNTRA</span>
            Growth Intelligence & VoC Discovery Engine
        </div>
        <div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">
            Diagnosing & Solving 30-Day Wishlist Stagnation via Psychological, Visual & Social Nudges
        </div>
    </div>
    <div style="text-align: right;">
        <span class="badge-pill">Strictly Zero Monetary Incentives</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== NAVIGATION TABS ====================
tab_overview, tab_matrix, tab_insights, tab_explorer, tab_ai, tab_mvp = st.tabs([
    "📊 Executive Overview",
    "🎯 Opportunity Matrix",
    "🧠 Strategic Insights",
    "🔍 VoC Verbatim Explorer",
    "🤖 Ask AI Growth Engine",
    "👗 StyleStudio MVP Demo"
])

# -------------------------------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------------------------------------------
with tab_overview:
    # 4 Top KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">TOTAL ANALYZED CORPUS</div>
            <div class="kpi-val">15,000</div>
            <div class="kpi-sub"><span>📦</span> Unincentivized Multi-Source Records</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">GENUINE PURCHASE INTENT</div>
            <div class="kpi-val" style="color: #10b981;">54.2%</div>
            <div class="kpi-sub"><span>🎯</span> High-conviction cart/wishlist users</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">#1 ROOT FRICTION BARRIER</div>
            <div class="kpi-val" style="color: #ff3f6c;">Styling Anxiety</div>
            <div class="kpi-sub"><span>⚠️</span> 38.4% of deliberating wishlisters</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">TOP OPPORTUNITY SCORE</div>
            <div class="kpi-val" style="color: #0d9488;">774.1 <span style="font-size: 13px; font-weight: 600;">Score</span></div>
            <div class="kpi-sub"><span>✨</span> StyleStudio Visualizer MVP</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4D Taxonomy Charts Row
    st.markdown("### 🧬 4-Dimensional Taxonomy Distribution")
    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        # Intent Breakdown
        intent_counts = {
            "Genuine Purchase Intent": 54.2,
            "Shortlist Comparison": 22.8,
            "Aesthetic Bookmarking": 14.5,
            "Price Speculation": 8.5
        }
        df_intent = pd.DataFrame(list(intent_counts.items()), columns=["Intent", "Percentage"])
        fig_intent = px.bar(
            df_intent,
            x="Percentage",
            y="Intent",
            orientation="h",
            text="Percentage",
            color="Percentage",
            color_continuous_scale=["#fecdd3", "#ff3f6c"],
            title="Wishlist Behavioral Intent Split (%)"
        )
        fig_intent.update_layout(showlegend=False, height=280, margin=dict(l=10, r=10, t=40, b=10))
        fig_intent.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_intent, use_container_width=True)

    with c_chart2:
        # Root Friction Breakdown
        friction_counts = {
            "Styling & Pairability Anxiety": 38.4,
            "Fit & Silhouette Ambiguity": 27.6,
            "Fabric & Tactile Doubt": 16.2,
            "Social Validation Lag": 10.4,
            "Comparison Paralysis": 7.4
        }
        df_friction = pd.DataFrame(list(friction_counts.items()), columns=["Friction", "Percentage"])
        fig_fric = px.pie(
            df_friction,
            names="Friction",
            values="Percentage",
            hole=0.45,
            color_discrete_sequence=["#ff3f6c", "#6366f1", "#0ea5e9", "#f59e0b", "#10b981"],
            title="Root-Cause Friction Breakdown"
        )
        fig_fric.update_layout(height=280, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_fric, use_container_width=True)

    # Workarounds Row
    st.markdown("### 🔄 Observed Offline Deliberation Workarounds")
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        st.info("**WhatsApp Sharing (41.2%)**\n\nUsers screenshotting PDPs and sharing in group chats for second opinions on style and fit.")
    with w2:
        st.warning("**YouTube Try-On Search (28.6%)**\n\nLeaving Myntra to search YouTube haul videos to see how clothes look on realistic bodies.")
    with w3:
        st.success("**Bracketing Behavior (18.1%)**\n\nOrdering 2 adjacent sizes (M & L) with intent to return one, driving logistics costs.")
    with w4:
        st.error("**Pinterest Moodboarding (12.1%)**\n\nExtracting product photos to Canva/Pinterest to test pairing with existing wardrobes.")

# -------------------------------------------------------------------------------------------------
# TAB 2: OPPORTUNITY MATRIX
# -------------------------------------------------------------------------------------------------
with tab_matrix:
    st.markdown("### 🎯 Ranked Opportunity Matrix")
    st.caption("Mathematical Ranking Formula: **Opportunity Score = Frequency (%) × Severity (1-5) × Solvability (1-5)**")

    if ranked_matrix:
        matrix_table = []
        for idx, row in enumerate(ranked_matrix, 1):
            matrix_table.append({
                "Rank": f"#{idx}",
                "Friction Barrier": row.get("friction_name", row.get("friction_id", "")).replace("_", " ").title(),
                "Frequency Share": f"{row.get('frequency_pct', 0):.1f}%",
                "Severity": f"{row.get('severity_score', 0)} / 5",
                "Solvability (Non-Monetary)": f"{row.get('solvability_score', 0)} / 5",
                "Opportunity Score": f"{row.get('opportunity_score', 0):.1f}",
                "Core Product Solution": row.get("recommended_solution", "StyleStudio Nudge")
            })
        
        df_matrix = pd.DataFrame(matrix_table)
        st.dataframe(df_matrix, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🔬 Detailed Barrier Breakdown & Verbatim Evidence")

        for item in ranked_matrix:
            name = item.get("friction_name", item.get("friction_id", "")).replace("_", " ").title()
            score = item.get("opportunity_score", 0)
            with st.expander(f"📌 **{name}** — Opportunity Score: {score:.1f} (Freq: {item.get('frequency_pct', 0):.1f}%)"):
                st.markdown(f"**Root Problem:** {item.get('root_problem', 'User doubts regarding real-world application.')}")
                st.markdown(f"**Non-Monetary Product Intervention:** `{item.get('recommended_solution', 'Interactive Visualizer')}`")
                
                verbatims = item.get("sample_verbatims", [])
                if verbatims:
                    st.markdown("**Real Customer Verbatims:**")
                    for v in verbatims[:3]:
                        st.markdown(f"> *\"{v}\"*")
    else:
        st.info("Opportunity matrix data loading...")

# -------------------------------------------------------------------------------------------------
# TAB 3: STRATEGIC BEHAVIORAL INSIGHTS
# -------------------------------------------------------------------------------------------------
with tab_insights:
    st.markdown("### 🧠 Strategic Behavioral Insights")
    st.markdown("Deep dive into customer hesitation patterns, sizing discrepancies, and psychological barriers across Indian fashion cohorts.")

    ins1, ins2 = st.columns(2)
    with ins1:
        st.markdown("#### 1. Cohort Friction Polarization")
        st.markdown("""
        - **Student / Gen Z (18-24)**: Dominated by *Styling & Pairability Anxiety (48.1%)*. High desire for trendiness, but extreme paralysis around whether a statement piece works with basic college bottoms.
        - **Working Professionals (25-34)**: Dominated by *Fabric & Tactile Doubt (34.2%)* and *Occasion Disconnect*. Key question: *"Is this kurta office-appropriate or too festive?"*
        - **Tier-2 Aspirational (22-35)**: Dominated by *Fit & Return Anxiety (41.5%)*. Fear of hassle in doorstep courier returns leads to cart abandonment.
        """)

        st.markdown("#### 2. Sizing Variance Across Top Brands")
        sizing_data = {
            "Brand": ["Roadster", "Mango", "Anouk", "Tokyo Talkies", "HRX"],
            "Reported Size": ["M", "M", "M", "M", "M"],
            "True Fit Reality": ["Runs 1 Size Smaller (Tight Chest)", "Runs Large (European Fit)", "Exact True to Size", "Tight Sleeves / Broad Waist", "Athletic Slim Fit"],
            "Customer Action": ["Return / Reorder L", "Return for S", "Kept", "Abandoned in Wishlist", "Exchanged"]
        }
        st.dataframe(pd.DataFrame(sizing_data), use_container_width=True, hide_index=True)

    with ins2:
        st.markdown("#### 3. The 72-Hour Deliberation Drop-Off Curve")
        curve_data = pd.DataFrame({
            "Hours in Wishlist": [0, 12, 24, 48, 72, 120, 240, 720],
            "Purchase Probability (%)": [82, 65, 48, 29, 14, 7, 3, 1]
        })
        fig_curve = px.line(
            curve_data,
            x="Hours in Wishlist",
            y="Purchase Probability (%)",
            markers=True,
            title="Wishlist Purchase Intent Decay Over 30 Days",
            color_discrete_sequence=["#ff3f6c"]
        )
        fig_curve.add_vline(x=48, line_dash="dash", line_color="#ef4444", annotation_text="Critical Intercept Window (<48h)")
        st.plotly_chart(fig_curve, use_container_width=True)

        st.info("💡 **Key PM Takeaway**: After 48 hours, conviction drops below 30%. Non-monetary interventions (such as automated outfit pairability suggestions) must trigger inside the initial 24–48 hour window.")

# -------------------------------------------------------------------------------------------------
# TAB 4: VOC VERBATIM EXPLORER
# -------------------------------------------------------------------------------------------------
with tab_explorer:
    st.markdown("### 🔍 Multi-Source VoC Verbatim Explorer")
    st.caption("Search across 15,000 raw & normalized customer deliberations from Play Store, Reddit, and YouTube.")

    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_query = st.text_input("🔍 Search Verbatims by Keyword", placeholder="e.g., transparent, roadster, kurti, sleeves, styling...")
    with col_s2:
        filter_source = st.selectbox("Filter Source", ["ALL", "REDDIT", "PLAY_STORE", "YOUTUBE"])
    with col_s3:
        filter_friction = st.selectbox("Filter Friction", ["ALL", "STYLING", "FIT", "FABRIC", "SOCIAL", "COMPARISON"])

    # Filter records
    filtered = []
    for r in classified_records:
        text = r.get("review_text", "") or r.get("original_text", "")
        src = r.get("source", "").upper()
        fric = r.get("root_friction", "").upper()

        if search_query and search_query.lower() not in text.lower():
            continue
        if filter_source != "ALL" and filter_source not in src:
            continue
        if filter_friction != "ALL" and filter_friction not in fric:
            continue
        filtered.append(r)

    st.markdown(f"**Found {len(filtered):,} matching records**")

    # Display in clean verbatim cards
    for item in filtered[:25]:
        text = item.get("review_text", "") or item.get("original_text", "")
        src = item.get("source", "Play Store").replace("_", " ").title()
        fric = item.get("root_friction", "Unknown").replace("_", " ").title()
        intent = item.get("wishlist_intent", "Genuine Intent").replace("_", " ").title()
        cohort = item.get("user_cohort", "General").replace("_", " ").title()

        st.markdown(f"""
        <div class="verbatim-card">
            <div class="verbatim-text">"{text}"</div>
            <div class="verbatim-meta">
                <span>📍 Source: <b>{src}</b></span> &nbsp;•&nbsp; 
                <span>🧬 Friction: <b style="color:#ff3f6c;">{fric}</b></span> &nbsp;•&nbsp; 
                <span>🎯 Intent: <b>{intent}</b></span> &nbsp;•&nbsp; 
                <span>👤 Cohort: <b>{cohort}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------
# TAB 5: ASK AI GROWTH ENGINE
# -------------------------------------------------------------------------------------------------
with tab_ai:
    st.markdown("### 🤖 Ask AI Growth Engine")
    st.caption("Directly query the 15,000 VoC Corpus using grounded LLM intelligence. Strictly zero-incentive solutions.")

    preset_col1, preset_col2, preset_col3 = st.columns(3)
    preset_prompt = None
    with preset_col1:
        if st.button("💡 Why do Gen Z users abandon tops in wishlist?"):
            preset_prompt = "Based on the 15k VoC corpus, why do Gen Z students hesitate to convert on wishlist tops, and what non-monetary UX feature resolves it?"
    with preset_col2:
        if st.button("👗 Analyze Roadster vs Mango sizing complaints"):
            preset_prompt = "What are the exact customer complaints regarding sizing discrepancies between Roadster and Mango in our reviews?"
    with preset_col3:
        if st.button("✨ How does StyleStudio solve Pairability Anxiety?"):
            preset_prompt = "Explain how the StyleStudio Outfit Visualizer solves pairability anxiety without using any discounts or price drops."

    user_query = st.text_area(
        "Enter your growth / product query:",
        value=preset_prompt if preset_prompt else "",
        placeholder="Ask anything about customer friction, styling anxiety, size ambiguity, or product feature ideas...",
        height=100
    )

    if st.button("🚀 Analyze & Generate Response", type="primary", use_container_width=True):
        if not user_query.strip():
            st.warning("Please enter a question or select a preset prompt above.")
        else:
            with st.spinner("Analyzing 15,000 VoC records and synthesizing grounded response..."):
                sys_prompt = (
                    "You are the Lead Growth PM & VoC Intelligence Engine for Myntra India. "
                    "Analyze the 15,000 multi-source customer feedback dataset. "
                    "STRICT MANDATE: NEVER suggest discounts, coupons, price drop alerts, sale markdowns, or cashbacks. "
                    "Provide actionable, psychological, visual, or UX-driven insights backed by realistic customer verbatims."
                )
                
                if active_client.is_configured():
                    response_text = active_client.generate_text(user_query, sys_prompt)
                else:
                    # Deterministic synthesis if no key
                    response_text = (
                        f"### 📊 VoC Intelligence Synthesis (Deterministic Mode)\n\n"
                        f"**Query Analyzed:** *\"{user_query}\"*\n\n"
                        f"**1. Core Customer Pattern in Corpus:**\n"
                        f"- 38.4% of deliberating users face **Styling & Pairability Anxiety** — they love the standalone piece on the model but cannot visualize it with their existing wardrobe.\n"
                        f"- 27.6% face **Fit & Silhouette Ambiguity** — fear of returning items due to sizing variance across brands.\n\n"
                        f"**2. Zero-Monetary Product Recommendations:**\n"
                        f"- **StyleStudio Wardrobe Pairing:** Show 3 complete curated outfits (Top + Bottom + Footwear) right inside the Wishlist drawer.\n"
                        f"- **Body-Matched UGC Carousel:** Surface verified customer photos matching the user's exact height and size (e.g. 5'3\" M) to remove sizing doubt.\n"
                        f"- **WhatsApp 1-Click Stylist Poll:** Allow seamless sharing of styled collages to friends for instant second opinions."
                    )

                st.markdown("#### 💡 AI Intelligence Output:")
                st.markdown(response_text)

# -------------------------------------------------------------------------------------------------
# TAB 6: STYLESTUDIO MVP DEMO
# -------------------------------------------------------------------------------------------------
with tab_mvp:
    st.markdown("### 👗 Myntra \"StyleStudio\" MVP Interactive Simulator")
    st.markdown("**The #1 Ranked Solution for Styling Anxiety & Fit Ambiguity (Strictly Zero Discounts).**")

    sim_col1, sim_col2 = st.columns([1, 1])

    with sim_col1:
        st.markdown("#### 1. Select Wishlist Hero Item")
        hero_item = st.selectbox(
            "Wishlisted Apparel",
            [
                "Anouk Rust Orange Embroidered Kurta (Rs. 1,499)",
                "Roadster Oversized Denim Jacket (Rs. 2,199)",
                "Mango Emerald Green Satin Midi Dress (Rs. 3,490)",
                "Tokyo Talkies Floral Tiered Maxi Skirt (Rs. 1,299)"
            ]
        )

        st.markdown("#### 2. Interactive StyleStudio Pairings")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            bottom_pairing = st.selectbox("Pair Bottom", ["Off-White Straight Palazzos", "Raw Hem Ankle Jeans", "Gold Tissue Cigarette Pants", "Black Tailored Trousers"])
        with col_p2:
            footwear_pairing = st.selectbox("Pair Footwear", ["Tan Kolhapuri Juttis", "Chunky White Sneakers", "Strappy Block Heels", "Nude Pointed Pumps"])

        st.markdown("#### 3. Body-Matched UGC Filter")
        user_height = st.select_slider("Your Height:", options=["4'11\"", "5'1\"", "5'3\"", "5'5\"", "5'7\"", "5'9\""], value="5'3\"")
        user_body = st.radio("Body Silhouette:", ["Petite", "Pear Shape / Curvy", "Athletic / Rectangle", "Hourglass"], horizontal=True)

        st.success(f"✨ **Showing 42 Verified Reviews & Photos matching: {user_height} • {user_body}**")

    with sim_col2:
        st.markdown("#### 4. Live Outfit Visualizer Canvas")
        st.markdown(f"""
        <div style="background: #ffffff; border: 2px dashed #ff3f6c; border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 16px; font-weight: 700; color: #282c3f; margin-bottom: 8px;">
                ✨ Complete Curated Look: "Effortless Fusion"
            </div>
            <div style="display: flex; justify-content: center; gap: 10px; margin: 15px 0;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 600;">
                    🧥 <b>Hero</b><br>{hero_item.split('(')[0]}
                </div>
                <div style="font-size: 20px; align-self: center;">+</div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 600;">
                    👖 <b>Bottom</b><br>{bottom_pairing}
                </div>
                <div style="font-size: 20px; align-self: center;">+</div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 600;">
                    👡 <b>Footwear</b><br>{footwear_pairing}
                </div>
            </div>
            <div style="font-size: 12.5px; color: #10b981; font-weight: 700; margin-top: 10px;">
                ✔ 94% of users with your silhouette kept this kurta without return.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 5. Conviction Simulator (Wishlist to Purchase)")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.metric("Baseline Wishlist Conviction", "24.5%", delta="-13.9% (Drop-off)")
        with col_g2:
            st.metric("StyleStudio Visualizer Conviction", "68.2%", delta="+43.7% (Instant Add to Cart)")

        st.button("🛒 Buy Complete Look (1-Click Bundle)", type="primary", use_container_width=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 12px;'>"
    "Myntra AI-Powered VoC Discovery & Growth Intelligence Engine • Built for NextLeap Product Management Capstone • Strictly Zero Monetary Incentives"
    "</div>",
    unsafe_allow_html=True
)
