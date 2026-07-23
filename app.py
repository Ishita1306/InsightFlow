"""
Kosvio AI Business Intelligence Platform entry point.

This module configures the Streamlit runtime, renders the landing page,
and routes user page workspace navigation.
"""

import streamlit as st

# Decrypt and load environment variables early before importing project components
from utils.crypto import decrypt_file_to_env
decrypt_file_to_env()

from components.sidebar_nav import render_sidebar_branding, render_sidebar_navigation
from pages import dashboard, upload, overview, visual_analytics, ai_insights, forecasting, reports, settings, document_analysis
from utils.theme_manager import inject_theme_css


@st.cache_data
def _read_stylesheet() -> str:
    # Read custom stylesheet (updated v13)
    with open("styles/theme.css", "r", encoding="utf-8") as f:
        return f.read()


def configure_page():
    """Apply global Streamlit page configuration."""
    st.set_page_config(
        page_title="Kosvio",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_styles():
    """Inject custom CSS for typography, spacing, and layout."""
    try:
        css_content = _read_stylesheet()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        inject_theme_css()
    except FileNotFoundError:
        st.warning("Theme stylesheet not found. Visual styling may be degraded.")


def render_hero():
    """Render the hero section with headline and call-to-action buttons."""
    with st.container():
        # Marker to target the container in CSS
        st.markdown('<div class="hero-section-marker"></div>', unsafe_allow_html=True)
        
        # Glow effects
        st.markdown('<div class="hero-glow hero-glow-a"></div><div class="hero-glow hero-glow-b"></div>', unsafe_allow_html=True)
        
        # Grid layout (columns)
        col_left, col_right = st.columns([1.1, 1], gap="large")
        
        with col_left:
            st.markdown(
                """
                <div class="hero-content">
                    <span class="hero-badge">
                        <svg class="hero-badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 12px; height: 12px; margin-right: 6px; display: inline-block; vertical-align: middle;"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                        Next-Gen AI Business Intelligence Platform
                    </span>
                    <h1 class="hero-title">Kosvio</h1>
                    <p class="hero-headline">
                        Every leader has a vision.<br>Every business file has its own story.
                    </p>
                    <p class="hero-description">
                        Instantly turn raw datasets and unstructured business documents (PDFs, Word files) 
                        into interactive dashboards, predictive forecasts, AI insights, and board-ready executive reports.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Sub-columns for buttons
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                st.markdown('<div class="hero-btn-primary-wrapper"></div>', unsafe_allow_html=True)
                if st.button("Get Started", key="hero_get_started", width="stretch"):
                    st.session_state["current_page"] = "upload"
                    st.rerun()
            with col_btn2:
                st.markdown('<div class="hero-btn-secondary-wrapper"></div>', unsafe_allow_html=True)
                if st.button("View Demo", key="hero_view_demo", width="stretch"):
                    st.session_state["current_page"] = "dashboard"
                    st.rerun()

        with col_right:
            st.markdown(
                """
                <div class="hero-visual">
                    <div class="dash-glow-ring"></div>
                    <div class="dash-frame">
                        <div class="dash-topbar">
                            <span class="dash-dot red"></span>
                            <span class="dash-dot yellow"></span>
                            <span class="dash-dot green"></span>
                            <span class="dash-topbar-title">
                                Kosvio Intelligence Hub
                            </span>
                        </div>
                        <div class="dash-body">
                            <div class="dash-sidebar">
                                <div class="dash-nav-item active"></div>
                                <div class="dash-nav-item"></div>
                                <div class="dash-nav-item"></div>
                                <div class="dash-nav-item"></div>
                            </div>
                            <div class="dash-main">
                                <div class="dash-widget">
                                    <div class="dash-widget-label">Quarterly Revenue</div>
                                    <div class="dash-kpi-row">
                                        <div class="dash-kpi">
                                            <div class="dash-kpi-val">$2.4M</div>
                                            <div class="dash-kpi-lbl">Total</div>
                                        </div>
                                        <div class="dash-kpi">
                                            <div class="dash-kpi-val">+18%</div>
                                            <div class="dash-kpi-lbl">Growth</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="dash-widget">
                                    <div class="dash-widget-label">Pipeline Health</div>
                                    <div class="dash-bars">
                                        <div class="dash-bar" style="height:55%"></div>
                                        <div class="dash-bar" style="height:80%"></div>
                                        <div class="dash-bar" style="height:45%"></div>
                                        <div class="dash-bar" style="height:90%"></div>
                                        <div class="dash-bar" style="height:65%"></div>
                                    </div>
                                </div>
                                <div class="dash-widget wide">
                                    <div class="dash-widget-label">
                                        Performance Forecast Trend
                                    </div>
                                    <div class="dash-line-chart">
                                        <svg viewBox="0 0 200 48" preserveAspectRatio="none">
                                            <polyline
                                                points="0,40 30,32 60,36 90,18 120,24 150,10 180,14 200,6"
                                                fill="none"
                                                stroke="#8B5CF6"
                                                stroke-width="2"
                                            />
                                            <polyline
                                                points="0,40 30,32 60,36 90,18 120,24 150,10 180,14 200,6 200,48 0,48"
                                                fill="url(#grad)"
                                                opacity="0.25"
                                              />
                                              <defs>
                                                  <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                                                      <stop offset="0%" stop-color="#7C3AED"/>
                                                      <stop offset="100%" stop-color="transparent"/>
                                                  </linearGradient>
                                              </defs>
                                          </svg>
                                      </div>
                                  </div>
                              </div>
                          </div>
                      </div>
                  </div>
                  """,
                unsafe_allow_html=True
            )


def render_kpi_stats():
    """Render KPI metric cards below the hero section."""
    st.markdown(
        """
        <div class="kpi-grid">
            <div class="kpi-card glass-card">
                <div class="kpi-top">
                    <div class="kpi-icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h10M4 17h14"/></svg>
                    </div>
                    <span class="kpi-trend">+24%</span>
                </div>
                <p class="kpi-value">2.4M+</p>
                <p class="kpi-label">Rows Processed</p>
                <p class="kpi-detail">Enterprise data analyzed at scale</p>
            </div>
            <div class="kpi-card glass-card">
                <div class="kpi-top">
                    <div class="kpi-icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
                    </div>
                    <span class="kpi-trend">+3.2%</span>
                </div>
                <p class="kpi-value">97.8%</p>
                <p class="kpi-label">Prediction Accuracy</p>
                <p class="kpi-detail">Validated model precision</p>
            </div>
            <div class="kpi-card glass-card">
                <div class="kpi-top">
                    <div class="kpi-icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
                    </div>
                    <span class="kpi-trend">+156</span>
                </div>
                <p class="kpi-value">1,200+</p>
                <p class="kpi-label">Dashboards Created</p>
                <p class="kpi-detail">Live views across organizations</p>
            </div>
            <div class="kpi-card glass-card">
                <div class="kpi-top">
                    <div class="kpi-icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.4V12h4a2 2 0 0 1 2 2v1h-2v5H8v-5H6v-1a2 2 0 0 1 2-2h4V9.4A4 4 0 0 1 12 2z"/></svg>
                    </div>
                    <span class="kpi-trend">+12K</span>
                </div>
                <p class="kpi-value">48K+</p>
                <p class="kpi-label">AI Insights Generated</p>
                <p class="kpi-detail">Automated recommendations delivered</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow():
    """Render the end-to-end data workflow section."""
    st.markdown(
        """
        <section class="page-section workflow-section">
            <div class="section-header center">
                <span class="section-label">Pipeline</span>
                <h2 class="section-title">From raw assets to business intelligence</h2>
                <p class="section-subtitle">
                    A refined five-stage pipeline that transforms datasets and reports
                    into strategic insights — seamlessly and at scale.
                </p>
            </div>
            <div class="timeline">
                <div class="timeline-rail"></div>
                <div class="timeline-step">
                    <span class="timeline-index">01</span>
                    <div class="timeline-node icon-box lg">
                        <svg viewBox="0 0 24 24"><path d="M12 16V4M12 16l-4-4M12 16l4-4M4 20h16"/></svg>
                    </div>
                    <div class="timeline-text">
                        <h4>Universal Ingestion</h4>
                        <p>CSV, Excel, PDF, or Word</p>
                    </div>
                </div>
                <div class="timeline-step">
                    <span class="timeline-index">02</span>
                    <div class="timeline-node icon-box lg">
                        <svg viewBox="0 0 24 24"><path d="M12 2v2M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
                    </div>
                    <div class="timeline-text">
                        <h4>AI Routing & Parsing</h4>
                        <p>Classify and extract data</p>
                    </div>
                </div>
                <div class="timeline-step">
                    <span class="timeline-index">03</span>
                    <div class="timeline-node icon-box lg">
                        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
                    </div>
                    <div class="timeline-text">
                        <h4>Interactive Visuals</h4>
                        <p>KPIs and chart dashboards</p>
                    </div>
                </div>
                <div class="timeline-step">
                    <span class="timeline-index">04</span>
                    <div class="timeline-node icon-box lg">
                        <svg viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                    </div>
                    <div class="timeline-text">
                        <h4>Forecast Outcomes</h4>
                        <p>Predict revenue trends</p>
                    </div>
                </div>
                <div class="timeline-step">
                    <span class="timeline-index">05</span>
                    <div class="timeline-node icon-box lg">
                        <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 15l2 2 4-4"/></svg>
                    </div>
                    <div class="timeline-text">
                        <h4>Executive Reports</h4>
                        <p>Polished briefs and tables</p>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_features():
    """Render the feature cards section."""
    st.markdown(
        """
        <section class="page-section">
            <div class="section-header center">
                <span class="section-label">Capabilities</span>
                <h2 class="section-title">Built for modern enterprise intelligence</h2>
                <p class="section-subtitle">
                    Six core modules engineered for clarity, performance, and the deep
                    strategic insights required by modern business leaders.
                </p>
            </div>
            <div class="feature-grid">
                <div class="feature-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
                    </div>
                    <h3>Analyze Datasets</h3>
                    <p>
                        Import and profile enterprise datasets to audit file health, identify missing columns, 
                        and standardize data structures.
                    </p>
                    <span class="feature-tag">Tabular Data</span>
                </div>
                <div class="feature-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/></svg>
                    </div>
                    <h3>Analyze Business Reports</h3>
                    <p>
                        Extract semantic text, structured data tables, and embedded images programmatically 
                        from PDF and DOCX reports.
                    </p>
                    <span class="feature-tag">Unstructured Documents</span>
                </div>
                <div class="feature-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
                    </div>
                    <h3>Generate Executive Summaries</h3>
                    <p>
                        Instantly compile dense, multi-page business files into concise 2-3 sentence executive summaries 
                        and strategic briefs.
                    </p>
                    <span class="feature-tag">AI Summarization</span>
                </div>
                <div class="feature-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 16l4-6 4 3 5-8"/></svg>
                    </div>
                    <h3>Forecast Sales</h3>
                    <p>
                        Project pipeline metrics, historical revenue trends, and growth forecasts using validated 
                        predictive modeling.
                    </p>
                    <span class="feature-tag">Predictive Analytics</span>
                </div>
                <div class="feature-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.4V12h4a2 2 0 0 1 2 2v1h-2v5H8v-5H6v-1a2 2 0 0 1 2-2h4V9.4A4 4 0 0 1 12 2z"/></svg>
                    </div>
                    <h3>Create AI Insights</h3>
                    <p>
                        Identify latent opportunities, project strategic risk warnings, and map key entity relationships 
                        automatically.
                    </p>
                    <span class="feature-tag">Strategic Advice</span>
                </div>
                <div class="feature-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 15l2 2 4-4"/></svg>
                    </div>
                    <h3>Produce Business-Ready Reports</h3>
                    <p>
                        Compile strategic summaries, key metrics, and charts into polished, board-ready 
                        PDF files.
                    </p>
                    <span class="feature-tag">PDF Export</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_why():
    """Render the 'Why Kosvio?' value proposition section."""
    st.markdown(
        """
        <section class="page-section why-section">
            <div class="section-header center">
                <span class="section-label">Why Us</span>
                <h2 class="section-title">Why Companies Choose Kosvio</h2>
                <p class="section-subtitle">
                    Trusted by forward-thinking organizations that refuse to
                    compromise on speed, security, or intelligence.
                </p>
            </div>
            <div class="why-grid">
                <div class="why-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                    </div>
                    <h3>Enterprise Security</h3>
                    <p>
                        SOC 2-ready architecture with encryption at rest
                        and in transit across every layer.
                    </p>
                </div>
                <div class="why-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                    </div>
                    <h3>Real-time Processing</h3>
                    <p>
                        Query millions of records in seconds with
                        sub-second response times at any scale.
                    </p>
                </div>
                <div class="why-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
                    </div>
                    <h3>AI-Powered Insights</h3>
                    <p>
                        Machine learning models surface patterns and
                        recommendations humans would miss.
                    </p>
                </div>
                <div class="why-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                    </div>
                    <h3>Scalable Architecture</h3>
                    <p>
                        Cloud-native infrastructure that grows with your
                        data volume and team size effortlessly.
                    </p>
                </div>
                <div class="why-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                    </div>
                    <h3>Seamless Integration</h3>
                    <p>
                        Connect CRM, ERP, and warehouse sources through
                        native connectors and open APIs.
                    </p>
                </div>
                <div class="why-card glass-card">
                    <div class="icon-wrap icon-box">
                        <svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                    </div>
                    <h3>Executive Reporting</h3>
                    <p>
                        Board-ready PDF exports with branded templates
                        and automated scheduling built in.
                    </p>
                </div>
            </div>
        </section>

        <section class="page-section tech-section">
            <span class="section-label">Technology</span>
            <h2 class="section-title">Powered by a modern stack</h2>
            <p class="section-subtitle">
                Built on proven, production-grade technologies for
                reliability, performance, and developer velocity.
            </p>
            <div class="tech-grid">
                <span class="tech-pill"><span class="tech-dot"></span>Python</span>
                <span class="tech-pill"><span class="tech-dot"></span>Streamlit</span>
                <span class="tech-pill"><span class="tech-dot"></span>Pandas</span>
                <span class="tech-pill"><span class="tech-dot"></span>NumPy</span>
                <span class="tech-pill"><span class="tech-dot"></span>Plotly</span>
                <span class="tech-pill"><span class="tech-dot"></span>Scikit-learn</span>
                <span class="tech-pill"><span class="tech-dot"></span>PostgreSQL</span>
                <span class="tech-pill"><span class="tech-dot"></span>Redis</span>
                <span class="tech-pill"><span class="tech-dot"></span>Docker</span>
                <span class="tech-pill"><span class="tech-dot"></span>REST API</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    """Render the site footer."""
    st.markdown(
        """
        <footer class="site-footer">
            <div class="footer-divider"></div>
            <div class="footer-inner">
                <div class="footer-top">
                    <div class="footer-brand">
                        <p class="footer-brand-name">Kosvio</p>
                        <p class="footer-brand-desc">
                            Every person has their own universe. Every dataset has its own story.
                        </p>
                        <div class="footer-social">
                            <span class="footer-social-icon icon-box">
                                <svg viewBox="0 0 24 24"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>
                            </span>
                            <span class="footer-social-icon icon-box">
                                <svg viewBox="0 0 24 24"><path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/></svg>
                            </span>
                            <span class="footer-social-icon icon-box">
                                <svg viewBox="0 0 24 24"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
                            </span>
                        </div>
                    </div>
                    <div class="footer-col">
                        <h5>Product</h5>
                        <p>Dashboards</p>
                        <p>Forecasting</p>
                        <p>AI Insights</p>
                        <p>Reports</p>
                    </div>
                    <div class="footer-col">
                        <h5>Platform</h5>
                        <p>Data Pipeline</p>
                        <p>Security</p>
                        <p>Integrations</p>
                        <p>API Access</p>
                    </div>
                    <div class="footer-col">
                        <h5>Company</h5>
                        <p>About</p>
                        <p>Careers</p>
                        <p>Contact</p>
                        <p>Legal</p>
                    </div>
                </div>
                <div class="footer-bottom">
                    <p class="footer-copy">
                        &copy; 2026 Kosvio. All rights reserved.
                    </p>
                    <span class="footer-badge">
                        <span class="footer-dot"></span>
                        All systems operational
                    </span>
                </div>
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder(title: str, badge: str = "Upcoming Feature") -> None:
    """Render a premium placeholder card for features in development."""
    inject_styles()
    import textwrap
    st.markdown(
        textwrap.dedent(
            f"""
            <div class="coming-soon-card glass-card">
                <span class="coming-soon-tag">{badge}</span>
                <div class="coming-soon-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="16" x2="12" y2="12"/>
                        <line x1="12" y1="8" x2="12.01" y2="8"/>
                    </svg>
                </div>
                <h2 style="margin: 0 0 1rem; font-size: 1.75rem; font-weight: 800; color: var(--text);">{title} Workspace</h2>
                <p style="margin: 0 auto; max-width: 420px; font-size: 0.95rem; line-height: 1.6; color: var(--subtext);">
                    This space is reserved for Phase 3 advanced extensions. 
                    Kosvio will connect specialized intelligence models to automate deep business recommendations here.
                </p>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True
    )


def render_landing_page():
    """Assemble and display the full landing page."""
    render_hero()
    render_kpi_stats()
    render_workflow()
    render_features()
    render_why()
    render_footer()


def main():
    """Bootstrap the application."""
    configure_page()

    # 1. User Authentication Guard
    if not st.session_state.get("authenticated", False):
        # Prevent any brief sidebar/header flicker by hiding them immediately
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stHeader"], .stAppHeader {
                    display: none !important;
                    width: 0 !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        inject_styles()
        from pages import auth
        auth.render()
        return

    # User is authenticated: inject regular styling
    inject_styles()

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "landing"

    render_sidebar_branding()
    render_sidebar_navigation(st.session_state["current_page"])

    current_page = st.session_state["current_page"]

    # 2. Workflow Quality Guard
    if current_page in ["dashboard", "visual_analytics", "reports"]:
        if "dataset" in st.session_state:
            df = st.session_state["dataset"]
            if "dataset_health_score" not in st.session_state:
                from pages.upload import calculate_health_score
                orig_df = st.session_state.get("original_df", df)
                st.session_state["dataset_health_score"] = calculate_health_score(orig_df)
                
            health = st.session_state["dataset_health_score"]
            if health < 80.0 and st.session_state.get("cleaned_df") is None:
                st.markdown('<div style="margin-top: 4rem;"></div>', unsafe_allow_html=True)
                from components.empty_state import render_empty_state
                render_empty_state(
                    title="Dataset Requires Cleaning",
                    message="This dataset requires cleaning before advanced analytics can produce reliable business insights.",
                    action_label="Clean Dataset",
                    navigate_to="upload"
                )
                return

    if current_page == "landing":
        render_landing_page()
    elif current_page == "dashboard":
        dashboard.render()
    elif current_page == "upload":
        upload.render()
    elif current_page == "overview":
        overview.render()
    elif current_page == "visual_analytics":
        visual_analytics.render()
    elif current_page == "ai_insights":
        ai_insights.render()
    elif current_page == "forecasting":
        forecasting.render()
    elif current_page == "reports":
        reports.render()
    elif current_page == "settings":
        settings.render()
    elif current_page == "document_analysis":
        document_analysis.render()

    # Inject JS Sidebar Auto-Collapse & Default Collapse Helper
    import streamlit.components.v1 as components
    with st.sidebar:
        components.html(
            """
            <script>
                const doc = window.parent.document;
                
                function collapseSidebar() {
                    const appContainer = doc.querySelector('[data-testid="stAppViewContainer"]');
                    if (appContainer && appContainer.getAttribute('data-sidebar-state') === 'expanded') {
                        const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                        if (sidebar) {
                            const collapseButton = sidebar.querySelector('button[aria-label="Collapse sidebar"]') || 
                                                   sidebar.querySelector('[data-testid="collapsedControl"] button') ||
                                                   sidebar.querySelector('button');
                            if (collapseButton) {
                                collapseButton.click();
                            }
                        }
                    }
                }
    
                // 1. Initial load collapse (collapse by default)
                if (!window.parent.__clario_initial_collapsed) {
                    window.parent.__clario_initial_collapsed = true;
                    setTimeout(collapseSidebar, 300);
                }
    
                // 2. Attach click listeners to all navigation buttons inside the sidebar
                function setupNavClickListeners() {
                    const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) {
                        const buttons = sidebar.querySelectorAll('button');
                        buttons.forEach(btn => {
                            const label = btn.getAttribute('aria-label') || '';
                            if (label !== 'Collapse sidebar' && !btn.id.includes('collapsedControl') && !btn.className.includes('collapsedControl')) {
                                if (!btn.__clario_listener_attached) {
                                    btn.__clario_listener_attached = true;
                                    btn.addEventListener('click', () => {
                                        setTimeout(collapseSidebar, 150);
                                    });
                                }
                            }
                        });
                    }
                }
    
                // Setup a mutation observer to watch for sidebar DOM changes and attach click listeners
                const targetNode = doc.querySelector('[data-testid="stSidebar"]');
                if (targetNode) {
                    const observer = new MutationObserver((mutations) => {
                        setupNavClickListeners();
                    });
                    observer.observe(targetNode, { childList: true, subtree: true });
                    setupNavClickListeners();
                }
            </script>
            """,
            height=0,
            width=0,
        )


if __name__ == "__main__":
    main()
