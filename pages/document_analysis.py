"""
Document Analysis Page.

Displays AI-powered document intelligence summaries, business insights,
risks, opportunities, strategic recommendations, detected tables, and charts
inside a polished enterprise-grade glassmorphic workspace.
"""

import streamlit as st
import os
import re
import json
import pandas as pd
import logging
from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.glass_card import glass_card_panel

logger = logging.getLogger(__name__)


def sanitize_column_names(headers: list) -> list:
    """
    Rename duplicate, empty, or multi-level column names in a list while preserving readability.
    Example: ['Amount', 'Amount', '', None, 'Amount'] -> ['Amount', 'Amount_2', 'Column_3', 'Column_4', 'Amount_5']
    """
    seen = {}
    new_headers = []
    for idx, h in enumerate(headers):
        h_str = str(h).strip() if h is not None else ""
        if not h_str or h_str.lower() in ["none", "nan", "null"]:
            h_str = f"Column_{idx + 1}"
            
        h_str = re.sub(r'[\(\)\'\",]', '', h_str).strip()
        
        if h_str in seen:
            seen[h_str] += 1
            h_new = f"{h_str}_{seen[h_str]}"
        else:
            seen[h_str] = 1
            h_new = h_str
        new_headers.append(h_new)
    return new_headers


def render_metric_card(label: str, value: str, icon: str) -> None:
    """Render a premium glassmorphic metric badge with enhanced typography."""
    st.markdown(
        f"""
        <div class="glass-metric-card">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span style="font-size: 1.15rem; color: var(--primary);">{icon}</span>
                <p style="font-size: 0.68rem; font-weight: 600; color: var(--subtext); text-transform: uppercase; margin: 0; letter-spacing: 0.08em;">{label}</p>
            </div>
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text); margin: 0; line-height: 1.2;">{value}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )


def render() -> None:
    """Render the polished Executive Intelligence Report workspace."""
    # Verify active document is loaded
    if "document_analysis" not in st.session_state:
        render_empty_state(
            title="No Document Selected",
            message="We couldn't locate an active document in memory. Please upload a PDF or Word document first.",
            action_label="Go to Upload Workspace",
            navigate_to="upload",
        )
        return

    analysis = st.session_state["document_analysis"]
    filename = st.session_state.get("document_filename", "document.pdf")
    ext = os.path.splitext(filename.lower())[1]
    
    # Extract metadata fields
    meta = analysis.get("metadata", {})
    doc_type = meta.get("document_type", "PDF Document" if ext == ".pdf" else "Word Document")
    pages = meta.get("page_count", 1)
    sec_count = meta.get("section_count", 0)
    table_count = meta.get("table_count", 0)
    chart_count = meta.get("chart_count", 0)
    word_count = meta.get("word_count", 0)
    
    conf = meta.get("confidence_levels", {})
    ext_conf = conf.get("extraction", "High")
    ai_status = conf.get("ai_analysis", "Low (Rule-based)")
    
    sections = analysis.get("sections", [])
    key_findings = analysis.get("key_findings", [])
    business_insights = analysis.get("business_insights", [])
    recommendations = analysis.get("recommendations", [])
    risks = analysis.get("risks", [])
    opportunities = analysis.get("opportunities", [])
    timeline = analysis.get("timeline", [])
    ai_charts = analysis.get("detected_charts", [])
    ai_tables = analysis.get("detected_tables", [])
    docx_tables = st.session_state.get("document_docx_tables", [])

    render_section_header(
        title="Executive Intelligence Report",
        subtitle=f"Enterprise analysis, strategic insights, and key action items for {filename}",
        label="Executive Report",
    )

    # Active Document Title and Clear Workspace
    col_title, col_clear = st.columns([4, 1.2])
    with col_title:
        st.markdown(
            f"""
            <div style="margin-bottom: 1.5rem;">
                <span class="coming-soon-tag" style="background: rgba(139, 92, 246, 0.12) !important; color: #c084fc !important; border: 1px solid rgba(139, 92, 246, 0.25) !important; font-weight: 600;">
                    Active Session File
                </span>
                <h3 style="font-weight: 700; color: var(--text); margin-top: 0.5rem; margin-bottom: 0; font-size: 1.35rem; letter-spacing: -0.02em;">
                    File Profile: <span style="color: var(--primary);">{filename}</span>
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_clear:
        if st.button("Clear Workspace", key="doc_clear_workspace", type="secondary", width="stretch"):
            from utils.workspace_manager import clear_workspace
            clear_workspace()
            st.session_state.pop("document_text", None)
            st.session_state.pop("document_filename", None)
            st.session_state.pop("document_analysis", None)
            st.session_state.pop("document_docx_tables", None)
            st.session_state.pop("document_has_charts", None)
            st.session_state.pop("active_doc_section", None)
            st.session_state["current_page"] = "upload"
            st.rerun()

    # CSS overrides for custom alerts, metric grids, lists, checkmarks, and line heights
    st.markdown(
        """
        <style>
        @keyframes slideInUp {
            from { transform: translateY(12px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .animate-up {
            animation: slideInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .glass-metric-card {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px !important;
            padding: 0.85rem 1.15rem !important;
            box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .glass-metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(139, 92, 246, 0.35) !important;
            box-shadow: 0 6px 20px 0 rgba(139, 92, 246, 0.15);
        }
        .executive-box {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-left: 4px solid var(--primary) !important;
            border-radius: 8px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
        }
        .doc-bullet-item {
            position: relative;
            padding-left: 1.5rem;
            margin-bottom: 0.95rem;
            font-size: 0.88rem;
            line-height: 1.6;
            color: var(--subtext);
        }
        .doc-bullet-item::before {
            content: "✦";
            position: absolute;
            left: 0;
            color: var(--primary);
            font-weight: bold;
        }
        .doc-bullet-risk::before {
            content: "⚠️";
            color: #EF4444 !important;
            font-size: 0.8rem;
        }
        .doc-bullet-opp::before {
            content: "📈";
            color: #10B981 !important;
            font-size: 0.8rem;
        }
        .actionable-check-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 0.95rem;
            font-size: 0.88rem;
            line-height: 1.6;
            color: var(--subtext);
        }
        .actionable-check-box {
            color: var(--primary);
            font-weight: bold;
            font-size: 1.05rem;
            line-height: 1.2;
            user-select: none;
        }
        .asset-alert {
            background: rgba(245, 158, 11, 0.08) !important;
            border: 1px solid rgba(245, 158, 11, 0.2) !important;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        .asset-alert-icon {
            color: #F59E0B;
            font-weight: bold;
            font-size: 1.1rem;
            line-height: 1;
        }
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 8px !important;
            margin-bottom: 0.65rem !important;
            padding: 0.75rem 1rem !important;
        }
        .custom-section-title {
            margin-top: 0;
            margin-bottom: 1rem;
            color: var(--text);
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: -0.01em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="animate-up">', unsafe_allow_html=True)

    # 1. Executive Summary (Concise cohesive narrative paragraph)
    raw_exec = analysis.get("executive_summary", "No summary generated.")
    clean_exec = re.sub(r'<div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">.*?</div>', '', raw_exec, flags=re.DOTALL)
    
    st.markdown(
        f"""
        <div class="executive-box">
            <h4 style="margin: 0 0 0.85rem; color: var(--primary); font-weight: 700; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.08em; line-height: 1.2;">
                Executive Summary
            </h4>
            <div style="font-size: 0.95rem; line-height: 1.75; color: var(--text); font-weight: 450;">
                {clean_exec}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Business Health Assessment
    health_data = analysis.get("business_health", {"status": "Healthy", "explanation": "Key indicators reflect solid performance."})
    h_status = health_data.get("status", "Healthy")
    h_explanation = health_data.get("explanation", "")
    
    h_color = "#10B981"
    h_emoji = "🟢"
    if h_status == "Moderate":
        h_color = "#F59E0B"
        h_emoji = "🟡"
    elif h_status == "Critical":
        h_color = "#EF4444"
        h_emoji = "🔴"
        
    st.markdown(
        f"""
        <div class="executive-box" style="border-left: 4px solid {h_color}; margin-top: 1.25rem; margin-bottom: 1.25rem;">
            <h4 style="margin: 0 0 0.5rem; color: {h_color}; font-weight: 700; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.08em; line-height: 1.2;">
                Business Health Assessment: {h_status} {h_emoji}
            </h4>
            <div style="font-size: 0.88rem; line-height: 1.6; color: var(--subtext); font-weight: 450;">
                {h_explanation}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Executive KPI Dashboard
    kpis = analysis.get("kpis", [])
    if kpis:
        with st.expander("📈 Executive KPI Dashboard", expanded=True):
            st.markdown('<p class="custom-section-title">Corporate Key Performance Indicators</p>', unsafe_allow_html=True)
            for i in range(0, len(kpis), 4):
                cols = st.columns(min(4, len(kpis) - i))
                for idx, kpi in enumerate(kpis[i:i+4]):
                    with cols[idx]:
                        render_metric_card(kpi.get("label", ""), kpi.get("value", ""), "📊")
            st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)

    # 4. Top Business Findings (Maximum 5)
    with st.expander("✨ Top Business Findings", expanded=True):
        st.markdown('<p class="custom-section-title">Critical Factual Observations & Highlights</p>', unsafe_allow_html=True)
        highlights = key_findings[:5]
        if highlights:
            for hg in highlights:
                hg_clean = hg.replace("[Key Finding]", "").replace("[Important Metric]", "").strip()
                st.markdown(f"<p class='doc-bullet-item'>{hg_clean}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 0.85rem; color: var(--subtext); font-style: italic;'>No business highlights identified.</p>", unsafe_allow_html=True)

    # 5. Key Risks (Maximum 5)
    with st.expander("⚠️ Key Risks", expanded=True):
        st.markdown('<p class="custom-section-title">Extracted Risks & Challenges</p>', unsafe_allow_html=True)
        top_risks = risks[:5]
        if top_risks:
            for r in top_risks:
                st.markdown(f"<p class='doc-bullet-item doc-bullet-risk'>{r}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 0.85rem; color: var(--subtext); font-style: italic;'>No risks detected in content.</p>", unsafe_allow_html=True)

    # 6. Growth Opportunities (Maximum 5)
    with st.expander("🚀 Growth Opportunities", expanded=True):
        st.markdown('<p class="custom-section-title">Growth & Operational Expansion Opportunities</p>', unsafe_allow_html=True)
        top_opps = opportunities[:5]
        if top_opps:
            for o in top_opps:
                st.markdown(f"<p class='doc-bullet-item doc-bullet-opp'>{o}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 0.85rem; color: var(--subtext); font-style: italic;'>No growth opportunities detected.</p>", unsafe_allow_html=True)

    # 7. Strategic Recommendations (Maximum 5)
    with st.expander("💡 Strategic Recommendations", expanded=True):
        st.markdown('<p class="custom-section-title">Actionable Checklist Items</p>', unsafe_allow_html=True)
        top_recs = recommendations[:5]
        if top_recs:
            for rec in top_recs:
                rec_clean = rec.replace("[Recommendation]", "").replace("[Action Item]", "").strip()
                st.markdown(
                    f"""
                    <div class="actionable-check-item">
                        <span class="actionable-check-box">☑</span>
                        <span>{rec_clean}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<p style='font-size: 0.85rem; color: var(--subtext); font-style: italic;'>No strategic recommendations mapped.</p>", unsafe_allow_html=True)

    # 8. Business Milestones (Maximum 5)
    with st.expander("📅 Business Milestones", expanded=True):
        st.markdown('<p class="custom-section-title">Key Business Milestones</p>', unsafe_allow_html=True)
        valid_timeline = [t for t in timeline if t and "no significant business milestones" not in t.lower() and "no execution timeline" not in t.lower()]
        top_milestones = valid_timeline[:5]
        if top_milestones:
            for idx, t_item in enumerate(top_milestones):
                st.markdown(
                    f"""
                    <div style="display: flex; gap: 15px; margin-bottom: 0.85rem; align-items: flex-start;">
                        <div style="background: var(--primary); color: #fff; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; flex-shrink: 0; margin-top: 2px;">
                            {idx + 1}
                        </div>
                        <p style="margin: 0; font-size: 0.88rem; color: var(--subtext); line-height: 1.6;">{t_item}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<p style='font-size: 0.85rem; color: var(--subtext); font-style: italic;'>No significant business milestones detected.</p>", unsafe_allow_html=True)

    # 9. Financial Highlights (Exposes structured business intelligence highlights instead of raw table grids)
    highlights = analysis.get("financial_highlights", [])
    if highlights:
        with st.expander("📊 Financial Highlights", expanded=True):
            st.markdown('<p class="custom-section-title">Key Financial Highlights & Segment Performance</p>', unsafe_allow_html=True)
            for i in range(0, len(highlights), 4):
                cols = st.columns(4)
                chunk = highlights[i:i+4]
                for idx, h_item in enumerate(chunk):
                    with cols[idx]:
                        with glass_card_panel():
                            st.markdown(
                                f"""
                                <p style="font-size: 0.76rem; color: var(--subtext); margin: 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                    {h_item.get('label', '')}
                                </p>
                                <p style="font-size: 1.45rem; font-weight: 700; color: var(--primary); margin: 0.15rem 0 0; letter-spacing: -0.02em;">
                                    {h_item.get('value', '')}
                                </p>
                                """,
                                unsafe_allow_html=True
                            )

    # 10. Developer Mode (Collapsible, disabled/collapsed by default)
    with st.expander("🛠️ Developer Mode", expanded=False):
        st.markdown('<p class="custom-section-title">Document Intelligence Statistics & Diagnostics</p>', unsafe_allow_html=True)
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            render_metric_card("Document Type", doc_type, "📄")
        with m_col2:
            render_metric_card("Total Pages", f"{pages} Pages", "📖")
        with m_col3:
            render_metric_card("Sections Detected", f"{sec_count} Sections", "📑")
        with m_col4:
            render_metric_card("Isolated Tables", f"{table_count} Tables", "📊")
            
        st.markdown('<div style="margin-top: 0.75rem;"></div>', unsafe_allow_html=True)
        
        m2_col1, m2_col2, m2_col3, m2_col4 = st.columns(4)
        with m2_col1:
            render_metric_card("Charts Detected", "Yes" if chart_count > 0 or st.session_state.get("document_has_charts") else "No", "📈")
        with m2_col2:
            render_metric_card("Word Count", f"{word_count:,} words", "✍️")
        with m2_col3:
            render_metric_card("Extraction Confidence", ext_conf.split()[0], "🛡️")
        with m2_col4:
            render_metric_card("AI Copilot Status", ai_status.split()[0], "🔮")
            
        qa = analysis.get("quality_assessment", {})
        if qa:
            st.markdown('<p class="custom-section-title" style="margin-top: 1.5rem;">Document Intelligence Quality Assessment</p>', unsafe_allow_html=True)
            q_col1, q_col2, q_col3 = st.columns(3)
            with q_col1:
                render_metric_card("Extraction Completeness", f"{qa.get('extraction_completeness', 0)}%", "🔍")
            with q_col2:
                render_metric_card("Business Entity Detection", f"{qa.get('entity_detection', 0)}%", "🏢")
            with q_col3:
                render_metric_card("Financial Coverage", f"{qa.get('financial_coverage', 0)}%", "💰")
                
            st.markdown('<div style="margin-top: 0.75rem;"></div>', unsafe_allow_html=True)
            q2_col1, q2_col2, q2_col3 = st.columns(3)
            with q2_col1:
                render_metric_card("Metadata Quality", f"{qa.get('metadata_quality', 0)}%", "📋")
            with q2_col2:
                render_metric_card("Section Coverage", f"{qa.get('section_coverage', 0)}%", "📑")
            with q2_col3:
                render_metric_card("Overall Intelligence Score", f"{qa.get('overall_intelligence_score', 0)}%", "🛡️")

        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
        with st.expander("🔍 Raw Extraction JSON & Diagnostics", expanded=False):
            text = st.session_state.get("document_text", "")
            if text:
                try:
                    raw_data = json.loads(text)
                    pretty_json = json.dumps(raw_data, indent=2)
                    st.text_area("JSON Raw Response", value=pretty_json, height=350, disabled=True)
                except Exception:
                    st.text_area("Extracted Raw Text Block", value=text, height=350, disabled=True)
            else:
                st.info("No raw text block found in session cache.")
