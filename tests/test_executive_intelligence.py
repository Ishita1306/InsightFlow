"""
Unit tests for the refined Executive Intelligence module.
Verifies KPI validation, health scoring, risk clustering, deduplication, and formatting rules.
"""

import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.document_service import (
    validate_kpi_candidate,
    format_kpi_value,
    calculate_business_health,
    deduplicate_insights,
    cluster_risks,
    clean_opportunity,
    clean_recommendation,
    score_insight_confidence,
    is_delta_value,
    generate_rewritten_summary,
    extract_high_value_kpis
)

def test_kpi_validation_subscribers():
    # Microsoft 365 subscriber count = 365 is invalid
    assert not validate_kpi_candidate("Subscribers", "365", "Microsoft 365 subscriber base increased.")
    assert not validate_kpi_candidate("Subscribers", "365", "The subscriber count is office 365.")
    # Valid subscriber count
    assert validate_kpi_candidate("Subscribers", "50 million", "We reached 50 million subscribers in Q3.")

def test_kpi_validation_employees():
    # Employees count must come from workforce context
    assert not validate_kpi_candidate("Employees", "220,000", "Total items in the warehouse was 220,000.")
    assert validate_kpi_candidate("Employees", "220K", "Kosvio workforce grew to 220K active employees.")
    # Reject year as headcount
    assert not validate_kpi_candidate("Employees", "2026", "Our workforce headcount target for 2026.")
    # Reject percentages or currency
    assert not validate_kpi_candidate("Employees", "10%", "We have 10% more employees.")
    assert not validate_kpi_candidate("Employees", "$150,000", "Average salary per employee is $150,000.")

def test_kpi_validation_gross_margin_delta():
    # Gross Margin Increase 13% should NOT become Gross Margin = 13%
    assert not validate_kpi_candidate("Gross Margin", "13%", "Gross Margin Increase of 13% this quarter.")
    assert not validate_kpi_candidate("Gross Margin", "5%", "Gross margins grew by 5% year-over-year.")
    # Absolute margin is valid
    assert validate_kpi_candidate("Gross Margin", "72%", "The gross margin rate was 72% for the fiscal year.")

def test_kpi_validation_carbon_reduction():
    # Reject incomplete units without context
    assert not validate_kpi_candidate("Carbon Reduction", "30 million", "The target reduction is 30 million.")
    # Accept complete or recover from context
    assert validate_kpi_candidate("Carbon Reduction", "30 million metric tons", "We removed 30 million metric tons of CO2.")
    assert validate_kpi_candidate("Carbon Reduction", "30 million", "We target carbon reduction of 30 million metric tons.")

def test_kpi_formatting():
    # Revenue formatting
    assert format_kpi_value("Revenue", "281.7 billion", "Total revenue was 281.7 billion dollars.") == "$281.7B"
    assert format_kpi_value("Revenue", "$168.9B", "") == "$168.9B"
    assert format_kpi_value("Revenue", "30 million", "") == "$30.0M"
    
    # Employees formatting
    assert format_kpi_value("Employees", "228,000", "") == "228K Employees"
    assert format_kpi_value("Employees", "228 thousand", "") == "228K Employees"
    
    # Growth/Margin formatting
    assert format_kpi_value("Revenue Growth", "15%", "") == "15%"
    assert format_kpi_value("Gross Margin", "0.72", "") == "72.0%"

    # Carbon reduction formatting
    assert format_kpi_value("Carbon Reduction", "30 million", "Carbon reduction target of 30 million metric tons.") == "30 million metric tons"

def test_business_health_scoring():
    # Simulated sections with cost increase but positive growth/profitability
    sections = [
        {
            "heading": "Financial Performance",
            "paragraphs": [
                "Revenue increased to record levels this year. Operating income grew significantly.",
                "Operating expenses rose due to strategic growth investments in cloud and AI infrastructure.",
                "The company remains highly profitable and generated strong cash flows and liquidity."
            ]
        }
    ]
    findings = ["Revenue increased to record levels."]
    risks = ["Operating expenses rose."]
    
    health = calculate_business_health(sections, findings, risks)
    # Costs increased should not drag rating down solely.
    assert health["status"] in ["Healthy", "Excellent"]
    assert health["score"] >= 70
    
    # Verify explanation contains Positive and Negative drivers
    explanation = health["explanation"]
    assert "Positive Drivers" in explanation
    assert "Negative Drivers" in explanation
    assert "✓ Revenue Growth" in explanation
    assert "• Rising Operating Expenses" in explanation

def test_insight_deduplication():
    insights = [
        "Revenue grew by 15% to $280 billion.",
        "Revenue rose by 15% to $280 billion.", # Duplicate
        "Operating margins expanded to 43%.",
        "We expanded operating margins to 43%." # Duplicate
    ]
    deduped = deduplicate_insights(insights)
    assert len(deduped) == 2
    assert deduped[0] == "Revenue grew by 15% to $280 billion."
    assert deduped[1] == "Operating margins expanded to 43%."

def test_risk_clustering():
    risks = [
        "Foreign currency fluctuations could adversely affect consolidated revenues.",
        "Exchange rate volatility represents a compliance risk for international transactions.",
        "Regulatory compliance scrutiny is increasing across all business operations."
    ]
    clustered = cluster_risks(risks)
    assert len(clustered) == 2
    assert any("Foreign Currency Risk" in c for c in clustered)
    assert any("Regulatory & Compliance Risk" in c for c in clustered)
    assert any("<strong>[High]</strong>" in c for c in clustered)

def test_opportunity_cleaning():
    # Verify raw opportunity cleaning helper still functions
    opp1 = "Implementing the target recommendation to expand Azure capacity is expected to deliver long-term business value."
    assert clean_opportunity(opp1) == "Expand Azure capacity"

def test_recommendation_cleaning():
    rec1 = "[Recommendation] strengthen global risk management."
    cleaned1 = clean_recommendation(rec1)
    assert "<strong>[High]</strong>" in cleaned1
    assert "Strengthen global risk management" in cleaned1
    assert "Expected Impact" in cleaned1
    
    rec2 = "Management should focus on efforts to optimize operational efficiency."
    cleaned2 = clean_recommendation(rec2)
    assert "<strong>[Medium]</strong>" in cleaned2
    assert "Optimize operational efficiency" in cleaned2
    assert "Expected Impact" in cleaned2

def test_confidence_scoring():
    # Template strings should score very low
    assert score_insight_confidence("finding", "implementing the target recommendation") < 30
    assert score_insight_confidence("finding", "parsed business intelligence indicates stable corporate execution") < 30
    # True finding should score high
    assert score_insight_confidence("finding", "Revenue grew by 15% to $281.7B in fiscal year 2026.") >= 70

def test_executive_summary_synthesis():
    sections = [
        {"heading": "Operations", "paragraphs": ["Revenue grew to $281.7B."]}
    ]
    findings = ["Revenue grew to $281.7B."]
    risks = ["Cybersecurity threats are rising."]
    recs = ["Increase security investment."]
    opportunities = ["Expand cloud capacity."]
    
    summary = generate_rewritten_summary(sections, findings, risks, recs, opportunities, "Business Report")
    words = summary.split()
    
    assert 150 <= len(words) <= 180
    
    for forbidden in ["parsed business intelligence indicates", "is expected to deliver long-term business value", "implementing the target recommendation", "operational execution remains robust"]:
        assert forbidden not in summary.lower()
        
    assert "trajectory" in summary.lower() or "direction" in summary.lower()

def test_adaptive_kpi_extraction():
    # 1. ESG Report
    esg_sections = [
        {
            "heading": "Environment",
            "paragraphs": [
                "Carbon emissions were 45 million metric tons.",
                "Water usage declined to 12 million gallons.",
                "Energy consumption reached 800 MWh.",
                "Solid waste generated was 250 tons."
            ]
        }
    ]
    kpis = extract_high_value_kpis(esg_sections, "ESG Report")
    labels = [k["label"] for k in kpis]
    assert "Carbon Emissions" in labels
    assert "Water Usage" in labels
    assert "Energy" in labels
    assert "Waste" in labels
    assert len(kpis) >= 4
    
    carbon_val = [k["value"] for k in kpis if k["label"] == "Carbon Emissions"][0]
    assert "45 million metric tons" in carbon_val
    
    # 2. Healthcare Report with backfill
    hc_sections = [
        {
            "heading": "Operations",
            "paragraphs": [
                "The facility admitted 120 thousand patients.",
                "Processed medical claims exceeded 500K claims.",
                "We managed 12 clinics and hospitals.",
                "Total facility revenue rose to $10B."
            ]
        }
    ]
    kpis_hc = extract_high_value_kpis(hc_sections, "Healthcare")
    labels_hc = [k["label"] for k in kpis_hc]
    assert "Patients" in labels_hc
    assert "Claims" in labels_hc
    assert "Hospitals" in labels_hc
    assert "Revenue" in labels_hc
    assert len(kpis_hc) == 4

if __name__ == "__main__":
    print("Running manually triggered Executive Intelligence unit tests...")
    test_kpi_validation_subscribers()
    test_kpi_validation_employees()
    test_kpi_validation_gross_margin_delta()
    test_kpi_validation_carbon_reduction()
    test_kpi_formatting()
    test_business_health_scoring()
    test_insight_deduplication()
    test_risk_clustering()
    test_opportunity_cleaning()
    test_recommendation_cleaning()
    test_confidence_scoring()
    test_executive_summary_synthesis()
    test_adaptive_kpi_extraction()
    print("ALL TESTS PASSED SUCCESSFULLY!")
