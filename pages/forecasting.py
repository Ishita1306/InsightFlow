"""
Forecasting Workspace Page.

Implements trend projections and predictive analytics on active datasets.
Features include target selection, forecast horizon controls, actuals comparison,
confidence intervals, and formatted exports.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.glass_card import glass_card_panel
from services.forecasting import ForecastingService


def render() -> None:
    """Render the Forecasting Workspace."""
    if "dataset" not in st.session_state:
        render_empty_state(
            title="No Dataset Selected",
            message="We couldn't locate an active dataset in memory. Please upload a dataset first.",
            action_label="Go to Upload Workspace",
            navigate_to="upload",
            navigate_label="Upload",
        )
        return

    df = st.session_state["dataset"]
    filename = st.session_state.get("dataset_filename", "dataset.csv")

    render_section_header(
        title="Predictive Forecasting Workspace",
        subtitle=f"Extrapolate future trajectories and confidence intervals for {filename}.",
        label="Predictive Engine",
    )

    if st.session_state.get("cleaned_df") is not None:
        st.info("All insights and metrics are generated from the cleaned dataset.")

    from services.visualization_service import VisualizationService
    detected = VisualizationService.detect_columns(df)
    numeric_cols = detected["numeric"]
    datetime_cols = detected["datetime"]

    if not numeric_cols:
        st.warning("Forecasting requires at least one numerical column. Please upload a dataset with numerical variables.")
        return

    from utils.theme_manager import get_current_theme
    theme_vars = get_current_theme()

    # Split Pane: Left Control Panel, Right Chart Panel
    col_ctrl, col_chart = st.columns([1, 2.5])

    with col_ctrl:
        st.markdown(f'<h4 style="margin-top: 0; font-weight: 700; color: var(--text);">Configuration</h4>', unsafe_allow_html=True)
        
        with glass_card_panel():
            target_var = st.selectbox(
                "Target variable (y)",
                options=numeric_cols,
                index=0,
                help="Select the continuous variable to project."
            )

            date_var = st.selectbox(
                "Timeline column (optional)",
                options=["[None]"] + datetime_cols,
                index=1 if datetime_cols else 0,
                help="Select a date column to align projections. If none selected, row sequence index is used."
            )

            horizon = st.slider(
                "Forecast horizon",
                min_value=7,
                max_value=120,
                value=30,
                step=1,
                help="Select the number of periods/days to project into the future."
            )

            st.markdown('<div style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>', unsafe_allow_html=True)
            
            # Run forecast
            forecast_df = ForecastingService.compute_forecast(df, target_var, date_var, horizon)
            
            if not forecast_df.empty:
                st.session_state["active_forecast"] = {
                    "df": forecast_df,
                    "target": target_var,
                    "date_col": date_var,
                    "horizon": horizon
                }
                # Add to activity log
                if "forecast_logged" not in st.session_state or st.session_state.get("forecast_logged") != (target_var, date_var, horizon):
                    st.session_state["forecast_logged"] = (target_var, date_var, horizon)
                    if "activity_log" in st.session_state:
                        import datetime
                        now_str = datetime.datetime.now().strftime("%I:%M %p")
                        st.session_state["activity_log"].insert(0, {"time": now_str, "event": f"Forecast: {target_var} (+{horizon} steps)"})

                # Export option
                csv_bytes = forecast_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Forecast Data",
                    data=csv_bytes,
                    file_name=f"kosvio_forecast_{target_var}.csv",
                    mime="text/csv",
                    width="stretch"
                )
            else:
                st.error("Failed to compute forecast. Ensure the selected variables contain valid rows.")

    with col_chart:
        # Inject CSS styles for the forecasting layout
        st.markdown(
            """
            <style>
            .fore-kpi-card {
                background: var(--card) !important;
                border: 1px solid var(--border) !important;
                border-radius: 12px !important;
                padding: 0.85rem !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                text-align: center !important;
                min-height: 80px !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            }
            .fore-kpi-lbl {
                font-size: 0.68rem !important;
                color: var(--subtext) !important;
                font-weight: 600 !important;
                letter-spacing: 0.05em !important;
                text-transform: uppercase !important;
                margin-bottom: 0.25rem !important;
            }
            .fore-kpi-val {
                font-size: 1.15rem !important;
                font-weight: 800 !important;
                color: var(--text) !important;
            }
            .rec-card {
                background: rgba(108, 99, 255, 0.03) !important;
                border: 1px solid rgba(108, 99, 255, 0.12) !important;
                border-left: 5px solid var(--primary) !important;
                border-radius: 12px !important;
                padding: 1rem !important;
                margin-bottom: 0.75rem !important;
                display: flex !important;
                gap: 0.75rem !important;
                align-items: flex-start !important;
            }
            .rec-card.accent {
                background: rgba(6, 182, 212, 0.03) !important;
                border: 1px solid rgba(6, 182, 212, 0.12) !important;
                border-left: 5px solid var(--accent) !important;
            }
            .rec-card-icon {
                font-size: 1.35rem !important;
                margin-top: 0.1rem !important;
                flex-shrink: 0 !important;
            }
            .rec-card-title {
                font-size: 0.9rem !important;
                font-weight: 700 !important;
                color: var(--text) !important;
                margin: 0 0 0.25rem 0 !important;
            }
            .rec-card-desc {
                font-size: 0.8rem !important;
                color: var(--subtext) !important;
                line-height: 1.4 !important;
                margin: 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f'<h4 style="margin-top: 0; font-weight: 700; color: var(--text);">Projection Canvas</h4>', unsafe_allow_html=True)
        
        if not forecast_df.empty:
            # Extract historical actuals and forecast values
            y_hist = forecast_df["Actual"].dropna().values
            y_fore = forecast_df["Forecast"].dropna().values
            n_hist = len(y_hist)
            
            # Show professional warning if dataset is too small for high-confidence predictions
            if n_hist < 15:
                st.warning("⚠️ Dataset size is insufficient for high-confidence forecasting. Results should be interpreted as illustrative estimates.")

            # Summary Metrics calculations
            hist_mean = np.mean(y_hist)
            fore_vals = y_fore[1:] if len(y_fore) > 1 else y_fore
            fore_mean = np.mean(fore_vals)
            fore_max = np.max(fore_vals)
            fore_min = np.min(fore_vals)
            
            # Growth Rate
            growth_rate = ((fore_mean - hist_mean) / hist_mean * 100) if hist_mean != 0 else 0.0
            
            # Accuracy (R-squared) calculation
            if n_hist > 2:
                t_hist = np.arange(n_hist)
                alpha, beta = np.polyfit(t_hist, y_hist, 1)
                residuals = y_hist - (alpha * t_hist + beta)
                var_res = np.var(residuals)
                var_y = np.var(y_hist)
                r_squared = 1.0 - (var_res / var_y) if var_y > 0 else 1.0
                r_squared = max(0.0, min(1.0, r_squared))
                accuracy_str = f"{r_squared * 100:.1f}%"
            else:
                alpha = 0.0
                accuracy_str = "N/A"

            # Growth Rate Arrow & Color styling
            if growth_rate > 0:
                growth_color = "#10B981"  # Emerald Green
                growth_arrow = "▲"
            elif growth_rate < 0:
                growth_color = "#EF4444"  # Red
                growth_arrow = "▼"
            else:
                growth_color = "var(--subtext)"
                growth_arrow = "•"

            # 1. Row 1: KPI Cards Grid
            kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
            
            with kpi_col1:
                st.markdown(f"""
                    <div class="fore-kpi-card">
                        <span class="fore-kpi-lbl">Hist Mean</span>
                        <span class="fore-kpi-val">{hist_mean:,.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            with kpi_col2:
                st.markdown(f"""
                    <div class="fore-kpi-card">
                        <span class="fore-kpi-lbl">Fore Mean</span>
                        <span class="fore-kpi-val" style="color: var(--accent);">{fore_mean:,.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            with kpi_col3:
                st.markdown(f"""
                    <div class="fore-kpi-card">
                        <span class="fore-kpi-lbl">Growth Rate</span>
                        <span class="fore-kpi-val" style="color: {growth_color};">{growth_arrow} {abs(growth_rate):.1f}%</span>
                    </div>
                """, unsafe_allow_html=True)
            with kpi_col4:
                st.markdown(f"""
                    <div class="fore-kpi-card">
                        <span class="fore-kpi-lbl">Horizon</span>
                        <span class="fore-kpi-val">{horizon} Steps</span>
                    </div>
                """, unsafe_allow_html=True)
            with kpi_col5:
                st.markdown(f"""
                    <div class="fore-kpi-card">
                        <span class="fore-kpi-lbl">Confidence</span>
                        <span class="fore-kpi-val">95.0%</span>
                    </div>
                """, unsafe_allow_html=True)
            with kpi_col6:
                st.markdown(f"""
                    <div class="fore-kpi-card">
                        <span class="fore-kpi-lbl">Accuracy</span>
                        <span class="fore-kpi-val">{accuracy_str}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

            # 2. Row 2: Large Forecast Chart
            fig = go.Figure()
            
            # Shaded Confidence Interval Region (Splined curves for modern styling)
            fig.add_trace(go.Scatter(
                x=forecast_df["Timeline"],
                y=forecast_df["Lower Bound"],
                mode="lines",
                line=dict(width=0, shape="spline"),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_df["Timeline"],
                y=forecast_df["Upper Bound"],
                mode="lines",
                line=dict(width=0, shape="spline"),
                fill="tonexty",
                fillcolor="rgba(108, 99, 255, 0.07)" if theme_vars["primary"] == "#6366F1" else "rgba(79, 70, 229, 0.07)",
                name="95% Confidence Interval",
                hoverinfo="skip"
            ))
            
            # Historical Actual Values
            fig.add_trace(go.Scatter(
                x=forecast_df["Timeline"],
                y=forecast_df["Actual"],
                mode="lines",
                line=dict(color=theme_vars["primary"], width=2.5, shape="spline"),
                name="Historical Actual",
                hovertemplate="Date: %{x}<br>Actual: %{y:,.2f}<extra></extra>"
            ))
            
            # Future Projections (Dashed curve)
            fig.add_trace(go.Scatter(
                x=forecast_df["Timeline"],
                y=forecast_df["Forecast"],
                mode="lines",
                line=dict(color=theme_vars["accent"], width=2.5, dash="dash", shape="spline"),
                name="Future Projection",
                hovertemplate="Date: %{x}<br>Projected: %{y:,.2f}<extra></extra>"
            ))
            
            # Vertical separator line marking forecast start
            last_hist_row = forecast_df[forecast_df["Actual"].notna()].iloc[-1]
            last_hist_date = last_hist_row["Timeline"]
            
            fig.add_vline(
                x=last_hist_date,
                line_width=1.5,
                line_dash="dash",
                line_color=theme_vars["subtext"],
                opacity=0.6,
                annotation_text="Forecast Start",
                annotation_position="top right",
                annotation_font=dict(size=10, color=theme_vars["subtext"])
            )
            
            # Apply Plotly theme details
            from services.visualization_service import VisualizationService
            VisualizationService.apply_theme(fig)
            fig.update_layout(
                title=dict(
                    text=f"Predictive Trajectory: {target_var} (+{horizon} steps)",
                    font=dict(size=14, color=theme_vars["text"]),
                    x=0.5,
                    xanchor="center"
                ),
                height=420,
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(l=30, r=30, t=60, b=30)
            )
            
            st.plotly_chart(fig, width="stretch")
            
            # 3. Row 3: Forecast Insights (Left) & Forecast Statistics (Right)
            col_insight, col_stats = st.columns([1.2, 1])
            
            # Trend type text helper
            trend_label = "Stable"
            trend_icon = "➡️"
            if n_hist > 2:
                if alpha > 0.001 * hist_mean:
                    trend_label = "Increasing"
                    trend_icon = "📈"
                elif alpha < -0.001 * hist_mean:
                    trend_label = "Decreasing"
                    trend_icon = "📉"

            with col_insight:
                with st.container(border=True):
                    st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em;">Forecast Insights</p>', unsafe_allow_html=True)
                    
                    if trend_label == "Increasing":
                        rec_text = "Based on the projected positive trajectory, we recommend increasing inventory buffer levels and resource allocation to align with expected demand spikes."
                    elif trend_label == "Decreasing":
                        rec_text = "Based on the projected negative trajectory, we recommend streamlining operational costs and verifying potential demand leaks or seasonal drop-offs."
                    else:
                        rec_text = "The stable trajectory suggests stable demand. We recommend maintaining current operational parameters and monitoring for micro-seasonal variance."
                        
                    st.markdown(
                        f"""
                        <div class="rec-card" style="margin-bottom: 0.75rem;">
                            <div class="rec-card-icon">{trend_icon}</div>
                            <div>
                                <h5 class="rec-card-title">Trend: {trend_label}</h5>
                                <p class="rec-card-desc">The model indicates a primarily {trend_label.lower()} path with moderate volatility.</p>
                            </div>
                        </div>
                        <div class="rec-card accent" style="margin-bottom: 0.75rem;">
                            <div class="rec-card-icon">⚡</div>
                            <div>
                                <h5 class="rec-card-title">Business Recommendation</h5>
                                <p class="rec-card-desc">{rec_text}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.markdown(
                        f"""
                        <div style="font-size: 0.82rem; line-height: 1.5; color: var(--text); padding: 0.5rem 0 0 0;">
                            <strong>Business Interpretation:</strong> The forecasting model projects the continuous path of <strong>{target_var}</strong> over the next <strong>{horizon}</strong> periods. The primary trend is <strong>{trend_label.lower()}</strong>, with a forecasted mean of <strong>{fore_mean:,.2f}</strong> (representing a <strong>{growth_rate:+.2f}%</strong> change from historical averages). The 95% confidence interval shows the range within which actual values are expected to fall, reflecting a model fit accuracy of <strong>{accuracy_str}</strong>.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            with col_stats:
                with st.container(border=True):
                    st.markdown('<p style="font-size: 0.85rem; font-weight: 600; color: var(--subtext); margin: 0 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em;">Forecast Statistics</p>', unsafe_allow_html=True)
                    
                    fore_std = np.std(fore_vals)
                    st.markdown(
                        f"""
                        <table style="width:100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.85rem;">
                            <thead>
                                <tr style="border-bottom: 1px solid var(--border); text-align: left; color: var(--subtext);">
                                    <th style="padding: 0.5rem 0;">Statistic</th>
                                    <th style="padding: 0.5rem 0; text-align: right;">Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                                    <td style="padding: 0.6rem 0; color: var(--text);">Mean</td>
                                    <td style="padding: 0.6rem 0; text-align: right; font-weight: 600; color: var(--text);">{fore_mean:,.2f}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                                    <td style="padding: 0.6rem 0; color: var(--text);">Median</td>
                                    <td style="padding: 0.6rem 0; text-align: right; font-weight: 600; color: var(--text);">{np.median(fore_vals):,.2f}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                                    <td style="padding: 0.6rem 0; color: var(--text);">Std Deviation</td>
                                    <td style="padding: 0.6rem 0; text-align: right; font-weight: 600; color: var(--text);">{fore_std:,.2f}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                                    <td style="padding: 0.6rem 0; color: var(--text);">Expected Minimum</td>
                                    <td style="padding: 0.6rem 0; text-align: right; font-weight: 600; color: var(--text);">{fore_min:,.2f}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                                    <td style="padding: 0.6rem 0; color: var(--text);">Expected Peak</td>
                                    <td style="padding: 0.6rem 0; text-align: right; font-weight: 600; color: var(--accent);">{fore_max:,.2f}</td>
                                </tr>
                            </tbody>
                        </table>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("A forecast chart will appear here once the configurations are validated.")


if __name__ == "__main__":
    render()
