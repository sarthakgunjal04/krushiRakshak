"""Unit tests for advisory explainer service."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.explainer import explain_advisory


def test_explainer_basic():
    """Test basic explainer functionality."""
    print("=" * 60)
    print("Testing Advisory Explainer Service")
    print("=" * 60)
    
    # Test case 1: Pest alert scenario
    print("\n--- Test 1: Pest Alert Scenario ---")
    rule_breakdown = {
        "pest": {
            "fired": ["Aphid risk detected due to high humidity"],
            "score": 0.85
        },
        "irrigation": {
            "fired": [],
            "score": 0.0
        },
        "market": {
            "fired": [],
            "score": 0.0
        }
    }
    
    fired_rules = ["Aphid risk detected due to high humidity"]
    
    metrics = {
        "ndvi": 0.45,
        "humidity": 78,
        "temperature": 32,
        "soil_moisture": 55,
        "market_price": 2200,
    }
    
    crop_meta = {
        "name": "Cotton",
        "common_pests": ["aphids", "whitefly", "bollworm"],
        "common_diseases": ["bacterial blight"],
        "optimal_soil_moisture_min": 40,
        "optimal_soil_moisture_max": 70,
    }
    
    score = 0.82
    
    explanation = explain_advisory(
        rule_breakdown=rule_breakdown,
        fired_rules=fired_rules,
        metrics=metrics,
        crop_meta=crop_meta,
        score=score,
        district="Pune",
    )
    
    print(f"Summary: {explanation['summary']}")
    print(f"Severity: {explanation['severity']}")
    print(f"Confidence: {explanation['confidence']}")
    print(f"Why: {explanation['why']}")
    print(f"Actions: {len(explanation['actions'])}")
    for i, action in enumerate(explanation['actions'], 1):
        print(f"  {i}. {action['title']}")
        for step in action['steps']:
            print(f"     - {step}")
    print(f"Data Sources: {explanation['data_sources']}")
    
    # Assertions
    assert "summary" in explanation
    assert "actions" in explanation
    assert "why" in explanation
    assert "severity" in explanation
    assert "confidence" in explanation
    assert "data_sources" in explanation
    
    assert explanation["severity"] in ["low", "medium", "high"]
    assert 0.0 <= explanation["confidence"] <= 1.0
    assert 1 <= len(explanation["actions"]) <= 3
    assert isinstance(explanation["summary"], str)
    assert len(explanation["summary"]) > 0
    
    print("\n[PASS] Test 1 passed!")
    
    # Test case 2: Irrigation scenario
    print("\n--- Test 2: Irrigation Scenario ---")
    rule_breakdown2 = {
        "pest": {"fired": [], "score": 0.0},
        "irrigation": {
            "fired": ["Low soil moisture detected"],
            "score": 0.65
        },
        "market": {"fired": [], "score": 0.0}
    }
    
    metrics2 = {
        "soil_moisture": 35,
        "temperature": 28,
        "rainfall": 2,
    }
    
    explanation2 = explain_advisory(
        rule_breakdown=rule_breakdown2,
        fired_rules=["Low soil moisture detected"],
        metrics=metrics2,
        crop_meta=crop_meta,
        score=0.65,
    )
    
    print(f"Summary: {explanation2['summary']}")
    print(f"Actions: {len(explanation2['actions'])}")
    for action in explanation2['actions']:
        print(f"  - {action['title']}")
    
    assert explanation2["severity"] == "medium"
    assert len(explanation2["actions"]) > 0
    
    print("\n[PASS] Test 2 passed!")
    
    # Test case 3: Market scenario
    print("\n--- Test 3: Market Scenario ---")
    rule_breakdown3 = {
        "pest": {"fired": [], "score": 0.0},
        "irrigation": {"fired": [], "score": 0.0},
        "market": {
            "fired": ["Price drop detected"],
            "score": 0.55
        }
    }
    
    metrics3 = {
        "market_price": 1800,
        "price_change_percent": -8.5,
    }
    
    explanation3 = explain_advisory(
        rule_breakdown=rule_breakdown3,
        fired_rules=["Price drop detected"],
        metrics=metrics3,
        crop_meta=crop_meta,
        score=0.55,
    )
    
    print(f"Summary: {explanation3['summary']}")
    print(f"Actions: {len(explanation3['actions'])}")
    
    assert explanation3["severity"] == "low"
    
    print("\n[PASS] Test 3 passed!")
    
    # Test case 4: No alerts scenario
    print("\n--- Test 4: No Alerts Scenario ---")
    rule_breakdown4 = {
        "pest": {"fired": [], "score": 0.0},
        "irrigation": {"fired": [], "score": 0.0},
        "market": {"fired": [], "score": 0.0}
    }
    
    explanation4 = explain_advisory(
        rule_breakdown=rule_breakdown4,
        fired_rules=[],
        metrics={},
        crop_meta=crop_meta,
        score=0.3,
    )
    
    print(f"Summary: {explanation4['summary']}")
    assert explanation4["severity"] == "low"
    
    print("\n[PASS] Test 4 passed!")
    
    print("\n" + "=" * 60)
    print("All explainer tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_explainer_basic()

