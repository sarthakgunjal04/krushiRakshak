"""
Fusion Engine - Intelligence layer that merges data sources and generates advisories.

Combines weather (IMD), market prices (Agmarknet), and satellite imagery (Bhuvan)
to provide crop advisories, pest alerts, and risk detection.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import sys
from typing import Dict, Any, List, Tuple

# Add backend directory to path for imports
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BACKEND_DIR)

from etl.make_features import evaluate_rules, load_rules, combine_features

router = APIRouter(prefix="/fusion", tags=["Fusion Engine"])

# Get the backend directory path (already set above)
DATA_PATH = os.path.join(BACKEND_DIR, "data")
RULES_PATH = os.path.join(BACKEND_DIR, "rules")
MOCK_PATH = os.path.join(os.path.dirname(__file__), "mock_data")


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {file_path}: {str(e)}")


def load_crop_mock(crop_name: str) -> Dict[str, Any]:
    """Load mock data JSON for a given crop if available."""
    filename = f"{crop_name.lower()}.json"
    file_path = os.path.join(MOCK_PATH, filename)
    if os.path.exists(file_path):
        return load_json_file(file_path)
    return {}


def build_advisory_from_features(crop: str, features: Dict[str, Any]) -> Tuple[Dict[str, Any], float, List[str]]:
    """Evaluate rules and produce an advisory summary, severity, alerts, and metrics.
    Returns advisory fields plus max score and fired rules for compatibility.
    """
    # Evaluate rules
    pest_rules = load_rules("pest")
    irrigation_rules = load_rules("irrigation")
    market_rules = load_rules("market")

    fired_pest, pest_score = evaluate_rules(pest_rules, features)
    fired_irrigation, irrigation_score = evaluate_rules(irrigation_rules, features)
    fired_market, market_score = evaluate_rules(market_rules, features)

    max_score = max(pest_score, irrigation_score, market_score, 0.0)

    # Severity mapping
    if max_score >= 0.8:
        severity = "high"
        summary = "High risk detected"
    elif max_score >= 0.6:
        severity = "medium"
        summary = "Moderate risk detected"
    else:
        severity = "low"
        summary = "Low risk detected"

    alerts: List[Dict[str, str]] = []
    for msg in fired_pest:
        alerts.append({"type": "pest", "message": msg})
    for msg in fired_irrigation:
        alerts.append({"type": "soil", "message": msg})
    for msg in fired_market:
        alerts.append({"type": "market", "message": msg})

    metrics = {
        "ndvi": features.get("ndvi"),
        "soil_moisture": features.get("soil_moisture"),
        "market_price": features.get("price_change_percent") if features.get("price_change_percent") is not None else None,
        "temperature": features.get("temperature"),
        "humidity": features.get("humidity"),
        "rainfall": features.get("rainfall"),
    }

    advisory_fields = {
        "summary": summary,
        "severity": severity,
        "alerts": alerts,
        "metrics": metrics,
    }

    return advisory_fields, max_score, (fired_pest + fired_irrigation + fired_market)


@router.get("/dashboard")
async def get_dashboard_data(crop: str = None):
    """
    Combine weather, market, and alert mock data for dashboard.
    
    Query params:
    - crop: Optional crop name to highlight/filter (e.g., cotton, wheat, rice)
    
    Returns combined overview with:
    - Weather data (temperature, humidity, rainfall, wind)
    - Market prices (wheat, rice, cotton, etc.)
    - Active alerts (pest, irrigation, market)
    - Crop health summary
    - user_crop: The crop parameter if provided
    """
    try:
        # Load data files
        weather = load_json_file(os.path.join(DATA_PATH, "weather_data.json"))
        market = load_json_file(os.path.join(DATA_PATH, "market_prices.json"))
        alerts = load_json_file(os.path.join(DATA_PATH, "alerts.json"))
        crop_health = load_json_file(os.path.join(DATA_PATH, "crop_health.json"))
        
        # Calculate summary statistics
        total_alerts = len(alerts) if isinstance(alerts, list) else 0
        high_priority_alerts = [
            alert for alert in alerts 
            if isinstance(alert, dict) and alert.get("level") == "high"
        ] if isinstance(alerts, list) else []
        
        response_data = {
            "weather": weather,
            "market": market,
            "alerts": alerts,
            "crop_health": crop_health,
            "summary": {
                "total_alerts": total_alerts,
                "high_priority_count": len(high_priority_alerts),
                "crops_monitored": len(crop_health) if isinstance(crop_health, dict) else 0
            },
            "timestamp": weather.get("timestamp", "2025-11-10T16:00:00Z")
        }
        
        # Add user's crop if provided
        if crop:
            response_data["user_crop"] = crop.lower()
        
        return JSONResponse(response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard data: {str(e)}")


@router.get("/advisory/{crop_name}")
async def get_advisory(crop_name: str):
    """
    Fetch rule-based advisory for given crop.
    
    Now loads per-crop mock data if available, applies rules, and returns:
    {
      "summary": str,
      "severity": "low|medium|high",
      "alerts": [ {"type": "pest|soil|market", "message": str}, ... ],
      "metrics": { ndvi, soil_moisture, market_price, temperature, humidity, rainfall },
      // plus legacy fields maintained for compatibility
    }
    """
    try:
        crop = crop_name.lower()

        # Load mock crop data if present
        mock = load_crop_mock(crop)
        if mock:
            # Build features directly from mock
            features = {
                "temperature": mock.get("temperature"),
                "humidity": mock.get("humidity"),
                "rainfall": mock.get("rainfall"),
                "ndvi": mock.get("ndvi"),
                "ndvi_change": 0.0,  # mock may not include change
                "soil_moisture": mock.get("soil_moisture"),
                "crop_stage": "unknown",
                "price_change_percent": 0,  # not provided in mock
            }

            advisory_fields, max_score, fired_rules = build_advisory_from_features(crop, features)

            # Compose response including legacy fields
            legacy_priority = "High" if advisory_fields["severity"] == "high" else ("Medium" if advisory_fields["severity"] == "medium" else "Low")
            response = {
                "crop": crop.capitalize(),
                "analysis": advisory_fields["summary"],
                "priority": legacy_priority,
                "severity": advisory_fields["severity"].capitalize(),
                "rule_score": max_score,
                "fired_rules": fired_rules,
                "recommendations": [],  # keep structure; real recs come from rules if needed
                "rule_breakdown": {},
                "data_sources": {"weather": "IMD", "satellite": "Bhuvan", "market": "Agmarknet"},
                "last_updated": "recently",
                # New fields for UI
                "summary": advisory_fields["summary"],
                "alerts": advisory_fields["alerts"],
                "metrics": advisory_fields["metrics"],
            }
            return JSONResponse(response)

        # Fallback to previous dynamic generation if no mock available
        advisory = await generate_advisory(crop)

        # Also attach new fields synthesized from features where possible (minimal)
        advisory.setdefault("summary", advisory.get("analysis", ""))
        advisory.setdefault("alerts", [])
        advisory.setdefault("metrics", {})

        return JSONResponse(advisory)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advisory: {str(e)}")


async def enhance_advisory_with_rules(advisory: Dict[str, Any], crop_name: str) -> Dict[str, Any]:
    """Enhance pre-generated advisory with real-time rule evaluation."""
    try:
        # Load current data
        weather = load_json_file(os.path.join(DATA_PATH, "weather_data.json"))
        crop_health_data = load_json_file(os.path.join(DATA_PATH, "crop_health.json"))
        market_data = load_json_file(os.path.join(DATA_PATH, "market_prices.json"))
        
        # Get crop-specific data
        crop_health = crop_health_data.get(crop_name, {})
        market = market_data.get(crop_name, {})
        
        # Combine features
        features = combine_features(weather, crop_health, market)
        
        # Evaluate all rule types
        pest_rules = load_rules("pest")
        irrigation_rules = load_rules("irrigation")
        market_rules = load_rules("market")
        
        fired_pest, pest_score = evaluate_rules(pest_rules, features)
        fired_irrigation, irrigation_score = evaluate_rules(irrigation_rules, features)
        fired_market, market_score = evaluate_rules(market_rules, features)
        
        # Combine all fired rules
        all_fired_rules = fired_pest + fired_irrigation + fired_market
        max_score = max(pest_score, irrigation_score, market_score, advisory.get("rule_score", 0.0))
        
        # Update advisory with rule evaluation
        advisory["fired_rules"] = all_fired_rules if all_fired_rules else advisory.get("fired_rules", [])
        advisory["rule_score"] = max_score
        advisory["rule_breakdown"] = {
            "pest": {"fired": fired_pest, "score": pest_score},
            "irrigation": {"fired": fired_irrigation, "score": irrigation_score},
            "market": {"fired": fired_market, "score": market_score}
        }
        
        return advisory
    except Exception:
        # If rule evaluation fails, return original advisory
        return advisory


async def generate_advisory(crop_name: str) -> Dict[str, Any]:
    """Generate advisory dynamically for crops without pre-generated files."""
    try:
        # Load data
        weather = load_json_file(os.path.join(DATA_PATH, "weather_data.json"))
        crop_health_data = load_json_file(os.path.join(DATA_PATH, "crop_health.json"))
        market_data = load_json_file(os.path.join(DATA_PATH, "market_prices.json"))
        
        crop_health = crop_health_data.get(crop_name, {})
        market = market_data.get(crop_name, {})
        
        # Combine features
        features = combine_features(weather, crop_health, market)
        
        # Evaluate rules
        pest_rules = load_rules("pest")
        irrigation_rules = load_rules("irrigation")
        market_rules = load_rules("market")
        
        fired_pest, pest_score = evaluate_rules(pest_rules, features)
        fired_irrigation, irrigation_score = evaluate_rules(irrigation_rules, features)
        fired_market, market_score = evaluate_rules(market_rules, features)
        
        # Determine priority and severity
        max_score = max(pest_score, irrigation_score, market_score, 0.0)
        
        if max_score >= 0.8:
            priority = "High"
            severity = "High"
        elif max_score >= 0.6:
            priority = "Medium"
            severity = "Medium"
        else:
            priority = "Low"
            severity = "Low"
        
        # Generate analysis text
        analysis_parts = []
        if fired_pest:
            analysis_parts.append("Pest risk detected based on environmental conditions.")
        if fired_irrigation:
            analysis_parts.append("Irrigation required based on temperature and soil moisture.")
        if fired_market:
            analysis_parts.append("Market conditions indicate price volatility.")
        
        analysis = " ".join(analysis_parts) if analysis_parts else "Crop conditions are normal. Continue monitoring."
        
        # Generate recommendations
        recommendations = []
        if fired_pest:
            recommendations.append({
                "title": "Apply pest control measures",
                "desc": "Based on detected pest risk indicators",
                "priority": "high" if pest_score >= 0.8 else "medium",
                "timeline": "immediate"
            })
        if fired_irrigation:
            recommendations.append({
                "title": "Schedule irrigation",
                "desc": "Based on temperature and soil moisture levels",
                "priority": "high" if irrigation_score >= 0.8 else "medium",
                "timeline": "within 24 hours"
            })
        if fired_market:
            recommendations.append({
                "title": "Review market timing",
                "desc": "Market conditions suggest price changes",
                "priority": "medium",
                "timeline": "1 week"
            })
        
        if not recommendations:
            recommendations.append({
                "title": "Continue monitoring",
                "desc": "Current conditions are favorable",
                "priority": "low",
                "timeline": "ongoing"
            })
        
        return {
            "crop": crop_name.capitalize(),
            "analysis": analysis,
            "priority": priority,
            "severity": severity,
            "rule_score": max_score,
            "fired_rules": fired_pest + fired_irrigation + fired_market,
            "recommendations": recommendations,
            "rule_breakdown": {
                "pest": {"fired": fired_pest, "score": pest_score},
                "irrigation": {"fired": fired_irrigation, "score": irrigation_score},
                "market": {"fired": fired_market, "score": market_score}
            },
            "data_sources": {
                "weather": "IMD",
                "satellite": "Bhuvan",
                "market": "Agmarknet"
            },
            "last_updated": weather.get("timestamp", "2025-11-10T16:00:00Z")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advisory: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the fusion engine."""
    return JSONResponse({
        "status": "healthy",
        "service": "Fusion Engine",
        "data_sources": ["IMD Weather", "Bhuvan Satellite", "Agmarknet Market"]
    })

