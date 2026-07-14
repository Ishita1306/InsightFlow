"""
Sanity tests for Phase 2 components.

Verifies column auto-detection, down-sampling, and figure creation for
all 12 required interactive Plotly charts.
"""

import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Ensure path is mapped correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.visualization_service import VisualizationService


def test_column_auto_detection():
    print("Verifying Column Auto-Detection...")
    data = {
        "A": [1, 2, 3, 4, 5],
        "B": ["cat", "dog", "dog", "mouse", "cat"],
        "C": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"],
    }
    df = pd.DataFrame(data)
    
    # Cast C to datetime for test
    df["C"] = pd.to_datetime(df["C"])
    
    detected = VisualizationService.detect_columns(df)
    
    assert "A" in detected["numeric"]
    assert "B" in detected["categorical"]
    assert "C" in detected["datetime"]
    print("SUCCESS: Column auto-detection tests passed.")


def test_sampling_for_large_datasets():
    print("Verifying Down-sampling logic for performance...")
    # Create large dummy dataset
    large_df = pd.DataFrame({"X": np.random.rand(12000), "Y": np.random.rand(12000)})
    
    sampled = VisualizationService.sample_if_large(large_df, max_rows=10000)
    assert len(sampled) == 10000
    
    small_df = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
    assert len(VisualizationService.sample_if_large(small_df)) == 2
    print("SUCCESS: Performance sampling validation passed.")


def test_plotly_figures_generation():
    print("Verifying generation of all 12 Plotly charts...")
    # Create a dummy DataFrame with continuous, categorical, and datetime fields
    data = {
        "Numeric1": [10.0, 20.0, 15.0, 30.0, 25.0],
        "Numeric2": [100, 120, 110, 140, 130],
        "Category1": ["Apples", "Oranges", "Apples", "Bananas", "Oranges"],
        "Category2": ["USA", "USA", "UK", "UK", "Germany"],
        "DateCol": pd.to_datetime(["2026-07-01", "2026-07-02", "2026-07-03", "2026-07-04", "2026-07-05"]),
    }
    df = pd.DataFrame(data)

    # 1. Correlation Heatmap
    fig = VisualizationService.create_correlation_heatmap(df)
    assert isinstance(fig, go.Figure)
    
    # 2. Histogram
    fig = VisualizationService.create_histogram(df, "Numeric1")
    assert isinstance(fig, go.Figure)

    # 3. Box Plot
    fig = VisualizationService.create_box_plot(df, "Numeric1", "Category1")
    assert isinstance(fig, go.Figure)

    # 4. Scatter Plot
    fig = VisualizationService.create_scatter_plot(df, "Numeric1", "Numeric2", "Category1")
    assert isinstance(fig, go.Figure)

    # 5. Line Chart
    fig = VisualizationService.create_line_chart(df, "DateCol", "Numeric1", "Category1")
    assert isinstance(fig, go.Figure)

    # 6. Area Chart
    fig = VisualizationService.create_area_chart(df, "DateCol", "Numeric1", "Category1")
    assert isinstance(fig, go.Figure)

    # 7. Pie Chart
    fig = VisualizationService.create_pie_chart(df, "Category1", "Numeric1")
    assert isinstance(fig, go.Figure)

    # 8. Donut Chart
    fig = VisualizationService.create_donut_chart(df, "Category1", "Numeric1")
    assert isinstance(fig, go.Figure)

    # 9. Treemap
    fig = VisualizationService.create_treemap(df, ["Category2", "Category1"], "Numeric1")
    assert isinstance(fig, go.Figure)

    # 10. Sunburst
    fig = VisualizationService.create_sunburst(df, ["Category2", "Category1"], "Numeric1")
    assert isinstance(fig, go.Figure)

    # 11. Violin Plot
    fig = VisualizationService.create_violin_plot(df, "Numeric1", "Category1")
    assert isinstance(fig, go.Figure)

    # 12. Pair Plot (Scatter Matrix)
    fig = VisualizationService.create_pair_plot(df, ["Numeric1", "Numeric2"], "Category1")
    assert isinstance(fig, go.Figure)

    print("SUCCESS: All 12 Plotly figures generated successfully.")


def run_all_tests():
    test_column_auto_detection()
    test_sampling_for_large_datasets()
    test_plotly_figures_generation()
    print("\nAll Phase 2 validations completed successfully!")


if __name__ == "__main__":
    run_all_tests()
