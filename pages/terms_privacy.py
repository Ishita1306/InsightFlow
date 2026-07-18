import streamlit as st
from components.glass_card import glass_card_panel

terms_html = """
<div class="terms-scrollbox">
    <h3>1. Introduction</h3>
    <p>Kosvio is an enterprise-grade, AI-powered Business Intelligence platform designed to help professionals and teams turn raw tabular datasets into structured, actionable business decisions. The platform provides a suite of advanced workspace tools, including:</p>
    <ul>
        <li><strong>Data Profiling</strong>: Comprehensive automated scanning of datasets to extract structural schemas, cardinality records, and statistics.</li>
        <li><strong>Data Cleaning</strong>: Heuristics for handling duplicates, missing fields, datatype conversions, and outliers.</li>
        <li><strong>Interactive Dashboards</strong>: Premium business intelligence dashboards summarizing key performance indicators (KPIs).</li>
        <li><strong>Data Visualization</strong>: Refined charting interfaces (bar charts, line charts, scatter plots) for statistical distributions.</li>
        <li><strong>AI Insights</strong>: A contextual conversational chatbot powered by machine learning to answer natural language queries about active datasets.</li>
        <li><strong>Forecasting</strong>: Advanced time-series projection engines with configurable confidence intervals and trend parameters.</li>
        <li><strong>Report Generation</strong>: Enterprise-ready executive exports available in PDF, PowerPoint, Excel, and PNG formats.</li>
    </ul>
    <p>By accessing or using Kosvio, you explicitly agree to be bound by these Terms of Service and our Privacy Policy. If you do not agree to these terms, you must not access or use the application.</p>

    <h3>2. Purpose of Data Collection</h3>
    <p>Kosvio processes datasets and user parameters solely to deliver requested business intelligence features. The scope of processing includes:</p>
    <ul>
        <li>Analyzing uploaded file buffers to construct profile reports.</li>
        <li>Executing cleansing operations to adjust tabular data in-session.</li>
        <li>Generating interactive charts, forecasts, and AI conversational responses.</li>
        <li>Producing downloadable reports and exports.</li>
    </ul>
    <p>Kosvio operates under a strict data boundary. Under no circumstances will uploaded datasets, metadata, or queries be utilized for advertising, user tracking, marketing, resale, commercial profiling, or public distribution.</p>

    <h3>3. Data Privacy</h3>
    <p>We prioritize the privacy of your operational data:</p>
    <ul>
        <li><strong>Strict Isolation</strong>: Your active workspace and uploaded data remain strictly isolated from all other users of the application.</li>
        <li><strong>No Resale</strong>: We do not sell, rent, lease, or monetize your uploaded datasets or personal registration information.</li>
        <li><strong>No Third-Party Sharing</strong>: Uploaded files and session variables are never shared with external vendors, contractors, or marketing partners.</li>
        <li><strong>No Model Training</strong>: Your data is never transmitted to public repositories or used to train public large language models or public AI services.</li>
    </ul>

    <h3>4. Data Security</h3>
    <p>Kosvio enforces robust mechanisms to secure your data:</p>
    <ul>
        <li><strong>In-Memory Boundary</strong>: Uploaded datasets are loaded directly into active Streamlit memory (st.session_state) and are processed entirely in-session.</li>
        <li><strong>No Write Footprint</strong>: The application does not write or save uploaded files to local disk directories (such as /data, /database, /assets, or /exports) unless you explicitly trigger an export action.</li>
        <li><strong>Immediate Cleanup</strong>: Any temporary files or operational metadata tables created during analytical parsing are deleted immediately after loading into your session DataFrame.</li>
        <li><strong>Account Protection</strong>: Sensitive user credentials and passwords are encrypted and processed securely.</li>
    </ul>

    <h3>5. Data Retention</h3>
    <p>Kosvio operates under a zero-retention session policy:</p>
    <ul>
        <li><strong>Session Longevity</strong>: Uploaded datasets, cleaned outputs, cached profile charts, and AI chat histories exist only for the duration of your active session.</li>
        <li><strong>Secure Destruction</strong>: Logging out of your account or closing your browser session triggers the complete erasure of your workspace state.</li>
        <li><strong>Manual Purging</strong>: You can instantly destroy all uploaded and cleaned data at any time by clicking the "Clear Workspace" button.</li>
        <li><strong>Offline Exports</strong>: Exported files are served as raw bytes to your browser and exist permanently only where you choose to download them.</li>
    </ul>

    <h3>6. User Rights</h3>
    <p>As a user of Kosvio, you possess full sovereignty over your workspace:</p>
    <ul>
        <li>The right to upload any compatible spreadsheet (CSV, Excel) into the workspace.</li>
        <li>The right to replace, overwrite, or update active datasets at any time.</li>
        <li>The right to delete active data and clear conversational histories instantly.</li>
        <li>The right to export and download your charts, summaries, and forecasting tables.</li>
        <li>The right to terminate your authenticated session whenever you choose.</li>
    </ul>

    <h3>7. No Third-Party Sharing</h3>
    <p>To maintain strict compliance with enterprise privacy standards, Kosvio does NOT:</p>
    <ul>
        <li>Transmit or share uploaded files with any external cloud host or analytics vendor.</li>
        <li>Provide data access to advertisers, marketing trackers, or search engines.</li>
        <li>Use customer data to build commercial profiles or targeted campaigns.</li>
        <li>Sell account telemetry or file contents to data brokers.</li>
    </ul>

    <h3>8. Limitation of Liability</h3>
    <p>The analytics, time-series forecasts, and AI-generated insights provided by Kosvio are diagnostic tools designed to assist in business decision-making. They do not constitute certified financial, legal, or strategic business advice. Kosvio makes no guarantees regarding the accuracy or commercial viability of generated projections, and users remain solely responsible for validating critical business decisions prior to execution.</p>

    <h3>9. Changes to Terms</h3>
    <p>We may update these Terms of Service and Privacy Policy as Kosvio evolves to support new features or regulatory requirements. Continued use of the application after such updates constitutes explicit acceptance of the revised Terms.</p>

    <h3>10. Governing Law</h3>
    <p>These Terms of Service and Privacy Policy shall be governed by, interpreted, and construed in accordance with the laws of India, without regard to conflict of law principles.</p>

    <h3>11. Contact Information</h3>
    <p>For questions, feedback, or support requests regarding these Terms and Privacy Policy, please contact:</p>
    <p>
        <strong>Developer:</strong> Ishita Goswami<br>
        <strong>Email:</strong> ishitagoswami40@gmail.com<br>
        <strong>Application:</strong> Kosvio
    </p>
</div>
"""


def render() -> None:
    """Render the scrollable Terms of Service & Privacy Agreement panel."""
    # Ensure terms acceptance state exists
    if "terms_accepted" not in st.session_state:
        st.session_state["terms_accepted"] = False

    st.markdown(
        """
        <style>
        .terms-scrollbox {
            max-height: 380px !important;
            overflow-y: auto !important;
            padding: 1.25rem !important;
            background: rgba(255, 255, 255, 0.01) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            margin-bottom: 1.25rem !important;
            font-size: 0.82rem !important;
            line-height: 1.55 !important;
            color: var(--subtext) !important;
        }
        .terms-scrollbox h3 {
            color: var(--text) !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            margin-top: 1.25rem !important;
            margin-bottom: 0.4rem !important;
        }
        .terms-scrollbox h3:first-of-type {
            margin-top: 0 !important;
        }
        .terms-scrollbox p, .terms-scrollbox ul {
            margin: 0 0 0.75rem 0 !important;
        }
        .terms-scrollbox li {
            margin-bottom: 0.35rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with glass_card_panel():
        # Title Header (Sticky Visual Placement)
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: var(--text);">Terms & Privacy</h3>
                <p style="margin: 0.25rem 0 0; font-size: 0.8rem; color: var(--subtext);">Please read and accept the agreement before continuing.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Scrollable Content Box
        # Strip leading whitespace from each line to prevent Markdown from rendering it as preformatted code
        formatted_terms = "\n".join(line.strip() for line in terms_html.split("\n"))
        st.markdown(formatted_terms, unsafe_allow_html=True)

        # Sticky Footer Section (Interactive Elements)
        terms_accepted = st.checkbox(
            "I have read and agree to the Terms of Service and Privacy Policy.",
            value=st.session_state["terms_accepted"],
            key="terms_agreement_checkbox"
        )
        st.session_state["terms_accepted"] = terms_accepted

        if st.button("Continue", type="primary", width="stretch", disabled=not terms_accepted):
            st.session_state["show_terms"] = False
            st.rerun()
