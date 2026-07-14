"""
Visualization service module.

Handles auto-detection of suitable dataset columns for plotting, and generates
premium dark-themed Plotly charts for Phase 2 dashboards.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class VisualizationService:
    """Service for generating premium, dark-themed interactive visualizations."""

    COLOR_SEQUENCE = ["#7C3AED", "#22D3EE", "#8B5CF6", "#3B82F6", "#EC4899", "#F59E0B", "#10B981"]
    
    # Gradient scale: Primary purple to dark surface, to accent cyan
    DIVERGING_SCALE = [
        [0.0, "#7C3AED"],
        [0.5, "#18181B"],
        [1.0, "#22D3EE"]
    ]

    @classmethod
    def apply_theme(cls, fig: go.Figure) -> None:
        """Apply the platform's luxury dark theme properties to a Plotly figure."""
        fig.update_layout(
            paper_bgcolor="rgba(24, 24, 27, 0.45)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            font_family="Inter, -apple-system, sans-serif",
            font_color="#FAFAFA",
            title_font_color="#FAFAFA",
            legend_font_color="#A1A1AA",
            margin=dict(l=50, r=40, t=60, b=50),
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.08)",
                zerolinecolor="rgba(255, 255, 255, 0.15)",
                color="#A1A1AA",
                tickfont=dict(size=10),
                title=dict(font=dict(color="#A1A1AA", size=11)),
            ),
            yaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.08)",
                zerolinecolor="rgba(255, 255, 255, 0.15)",
                color="#A1A1AA",
                tickfont=dict(size=10),
                title=dict(font=dict(color="#A1A1AA", size=11)),
            ),
            # Set grid styles for 3D coordinates if applicable
            scene=dict(
                xaxis=dict(
                    backgroundcolor="rgba(0,0,0,0)",
                    gridcolor="rgba(255,255,255,0.08)",
                    color="#A1A1AA"
                ),
                yaxis=dict(
                    backgroundcolor="rgba(0,0,0,0)",
                    gridcolor="rgba(255,255,255,0.08)",
                    color="#A1A1AA"
                ),
                zaxis=dict(
                    backgroundcolor="rgba(0,0,0,0)",
                    gridcolor="rgba(255,255,255,0.08)",
                    color="#A1A1AA"
                )
            )
        )

    @classmethod
    def detect_columns(cls, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Auto-detect lists of numeric, categorical, and datetime columns.
        
        Args:
            df (pd.DataFrame): Input dataset.

        Returns:
            Dict[str, List[str]]: Lists of detected column names by type.
        """
        # Numeric columns
        numeric = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Datetime columns (including objects that can be parsed as dates)
        datetime_cols = df.select_dtypes(include=[np.datetime64, "datetime64[ns]"]).columns.tolist()
        
        # Categorical columns
        categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        
        # Inspect objects to see if they can be candidate dates or categories
        for col in df.select_dtypes(include=["object"]):
            if col in datetime_cols or col in categorical:
                continue
            # Check if it could be a date
            try:
                # If first few elements are date-like
                sample = df[col].dropna().head(5)
                if not sample.empty and pd.to_datetime(sample, errors="raise"):
                    datetime_cols.append(col)
                    continue
            except (ValueError, TypeError):
                pass
            
            # Default to categorical for object columns
            categorical.append(col)

        return {
            "numeric": numeric,
            "categorical": categorical,
            "datetime": datetime_cols,
            "all": df.columns.tolist()
        }

    @classmethod
    def sample_if_large(cls, df: pd.DataFrame, max_rows: int = 10000) -> pd.DataFrame:
        """Sample a dataset if it exceeds max_rows to keep browser plotting responsive."""
        if len(df) > max_rows:
            return df.sample(n=max_rows, random_state=42)
        return df

    # 1. Correlation Heatmap
    @classmethod
    def create_correlation_heatmap(cls, df: pd.DataFrame) -> go.Figure:
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            fig = go.Figure()
            fig.update_layout(title="Correlation heatmap requires at least 2 numerical columns.")
            cls.apply_theme(fig)
            return fig

        corr = numeric_df.corr()
        fig = px.imshow(
            corr,
            x=corr.columns,
            y=corr.columns,
            color_continuous_scale=cls.DIVERGING_SCALE,
            aspect="auto",
            title="Pearson Correlation Matrix",
        )
        cls.apply_theme(fig)
        return fig

    # 2. Histogram
    @classmethod
    def create_histogram(cls, df: pd.DataFrame, column: str, bins: int = 30) -> go.Figure:
        fig = px.histogram(
            df,
            x=column,
            nbins=bins,
            title=f"Distribution of {column}",
            color_discrete_sequence=[cls.COLOR_SEQUENCE[0]],
        )
        cls.apply_theme(fig)
        fig.update_layout(bargap=0.05)
        return fig

    # 3. Box Plot
    @classmethod
    def create_box_plot(cls, df: pd.DataFrame, y_col: str, x_col: Optional[str] = None) -> go.Figure:
        sampled_df = cls.sample_if_large(df, 20000)
        fig = px.box(
            sampled_df,
            x=x_col,
            y=y_col,
            title=f"Box Plot of {y_col}" + (f" grouped by {x_col}" if x_col else ""),
            color_discrete_sequence=[cls.COLOR_SEQUENCE[2]],
        )
        cls.apply_theme(fig)
        return fig

    # 4. Scatter Plot
    @classmethod
    def create_scatter_plot(
        cls, df: pd.DataFrame, x_col: str, y_col: str, color_col: Optional[str] = None
    ) -> go.Figure:
        sampled_df = cls.sample_if_large(df, 10000)
        fig = px.scatter(
            sampled_df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f"Scatter Plot: {x_col} vs {y_col}",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
            color_continuous_scale=cls.DIVERGING_SCALE,
        )
        cls.apply_theme(fig)
        return fig

    # 5. Line Chart
    @classmethod
    def create_line_chart(
        cls, df: pd.DataFrame, x_col: str, y_col: str, group_col: Optional[str] = None
    ) -> go.Figure:
        # Group and aggregate if we have duplicates for the same X to avoid messy lines
        plot_df = df
        if group_col:
            grouped = df.groupby([x_col, group_col])[y_col].mean().reset_index()
            plot_df = grouped
        else:
            grouped = df.groupby(x_col)[y_col].mean().reset_index()
            plot_df = grouped

        plot_df = plot_df.sort_values(by=x_col)
        fig = px.line(
            plot_df,
            x=x_col,
            y=y_col,
            color=group_col,
            title=f"Line Chart of Average {y_col} by {x_col}",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
        )
        cls.apply_theme(fig)
        return fig

    # 6. Area Chart
    @classmethod
    def create_area_chart(
        cls, df: pd.DataFrame, x_col: str, y_col: str, group_col: Optional[str] = None
    ) -> go.Figure:
        if group_col:
            grouped = df.groupby([x_col, group_col])[y_col].mean().reset_index()
        else:
            grouped = df.groupby(x_col)[y_col].mean().reset_index()
        
        grouped = grouped.sort_values(by=x_col)
        fig = px.area(
            grouped,
            x=x_col,
            y=y_col,
            color=group_col,
            title=f"Area Chart of Average {y_col} by {x_col}",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
        )
        cls.apply_theme(fig)
        return fig

    # 7. Pie Chart
    @classmethod
    def create_pie_chart(cls, df: pd.DataFrame, names_col: str, values_col: Optional[str] = None) -> go.Figure:
        if values_col:
            grouped = df.groupby(names_col)[values_col].sum().reset_index()
            # Sort and take top 10 to keep it clean
            grouped = grouped.sort_values(by=values_col, ascending=False).head(10)
        else:
            grouped = df[names_col].value_counts().reset_index()
            grouped.columns = [names_col, "Count"]
            grouped = grouped.head(10)
            values_col = "Count"

        fig = px.pie(
            grouped,
            names=names_col,
            values=values_col,
            title=f"Distribution of {names_col} (Top 10)",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
        )
        cls.apply_theme(fig)
        return fig

    # 8. Donut Chart
    @classmethod
    def create_donut_chart(cls, df: pd.DataFrame, names_col: str, values_col: Optional[str] = None) -> go.Figure:
        if values_col:
            grouped = df.groupby(names_col)[values_col].sum().reset_index()
            grouped = grouped.sort_values(by=values_col, ascending=False).head(10)
        else:
            grouped = df[names_col].value_counts().reset_index()
            grouped.columns = [names_col, "Count"]
            grouped = grouped.head(10)
            values_col = "Count"

        fig = px.pie(
            grouped,
            names=names_col,
            values=values_col,
            hole=0.6,
            title=f"Distribution breakdown of {names_col} (Top 10)",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
        )
        cls.apply_theme(fig)
        return fig

    # 9. Treemap
    @classmethod
    def create_treemap(cls, df: pd.DataFrame, path_cols: List[str], values_col: Optional[str] = None) -> go.Figure:
        # Group to avoid huge treemaps
        if values_col:
            grouped = df.groupby(path_cols)[values_col].sum().reset_index()
            # limit rows for safety
            grouped = grouped.sort_values(by=values_col, ascending=False).head(50)
        else:
            grouped = df.groupby(path_cols).size().reset_index(name="Count")
            grouped = grouped.sort_values(by="Count", ascending=False).head(50)
            values_col = "Count"

        fig = px.treemap(
            grouped,
            path=path_cols,
            values=values_col,
            title=f"Treemap Hierarchy: {' > '.join(path_cols)}",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
        )
        cls.apply_theme(fig)
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        return fig

    # 10. Sunburst
    @classmethod
    def create_sunburst(cls, df: pd.DataFrame, path_cols: List[str], values_col: Optional[str] = None) -> go.Figure:
        if values_col:
            grouped = df.groupby(path_cols)[values_col].sum().reset_index()
            grouped = grouped.sort_values(by=values_col, ascending=False).head(40)
        else:
            grouped = df.groupby(path_cols).size().reset_index(name="Count")
            grouped = grouped.sort_values(by="Count", ascending=False).head(40)
            values_col = "Count"

        fig = px.sunburst(
            grouped,
            path=path_cols,
            values=values_col,
            title=f"Sunburst Hierarchy: {' > '.join(path_cols)}",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
        )
        cls.apply_theme(fig)
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        return fig

    # 11. Violin Plot
    @classmethod
    def create_violin_plot(cls, df: pd.DataFrame, y_col: str, x_col: Optional[str] = None) -> go.Figure:
        sampled_df = cls.sample_if_large(df, 15000)
        fig = px.violin(
            sampled_df,
            x=x_col,
            y=y_col,
            box=True,
            points="outliers",
            title=f"Violin Plot of {y_col}" + (f" by {x_col}" if x_col else ""),
            color_discrete_sequence=[cls.COLOR_SEQUENCE[1]],
        )
        cls.apply_theme(fig)
        return fig

    # 12. Pair Plot (Scatter Matrix)
    @classmethod
    def create_pair_plot(cls, df: pd.DataFrame, num_cols: List[str], color_col: Optional[str] = None) -> go.Figure:
        # Cap columns to 4 for visibility and rendering speed
        selected_cols = num_cols[:4]
        sampled_df = cls.sample_if_large(df, 2000) # Scatter matrices are expensive
        fig = px.scatter_matrix(
            sampled_df,
            dimensions=selected_cols,
            color=color_col,
            title=f"Scatter Matrix (Pair Plot) of Numerical Features",
            color_discrete_sequence=cls.COLOR_SEQUENCE,
            color_continuous_scale=cls.DIVERGING_SCALE,
        )
        cls.apply_theme(fig)
        # Update diagonal settings and marker size
        fig.update_traces(diagonal_visible=False, marker=dict(size=3, opacity=0.7))
        return fig
