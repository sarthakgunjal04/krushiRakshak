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
from typing import Dict, Any, List

# Add backend directory to path for imports
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BACKEND_DIR)

from etl.make_features import evaluate_rules, load_rules, combine_features

router = APIRouter(prefix="/fusion", tags=["Fusion Engine"])

# Get the backend directory path (already set above)
DATA_PATH = os.path.join(BACKEND_DIR, "data")
RULES_PATH = os.path.join(BACKEND_DIR, "rules")


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {file_path}: {str(e)}")


@router.get("/dashboard")
async def get_dashboard_data():
    """
    Combine weather, market, and alert mock data for dashboard.
    
    Returns combined overview with:
    - Weather data (temperature, humidity, rainfall, wind)
    - Market prices (wheat, rice, cotton, etc.)
    - Active alerts (pest, irrigation, market)
    - Crop health summary
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
        
        return JSONResponse({
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
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard data: {str(e)}")


@router.get("/advisory/{crop_name}")
async def get_advisory(crop_name: str):
    """
    Fetch rule-based advisory for given crop.
    
    Combines weather, crop health, and market data to generate:
    - Analysis based on fired rules
    - Priority and severity
    - Actionable recommendations
    - Explainable results (which rules triggered)
    
    Args:
        crop_name: Name of the crop (e.g., "cotton", "wheat", "rice")
    
    Returns:
        Advisory JSON with recommendations and rule explanations
    """
    try:
        crop_name_lower = crop_name.lower()
        
        # Check if pre-generated advisory exists
        advisory_file = os.path.join(DATA_PATH, f"advisory_{crop_name_lower}.json")
        
        if os.path.exists(advisory_file):
            advisory = load_json_file(advisory_file)
            
            # Enhance with real-time rule evaluation
            advisory = await enhance_advisory_with_rules(advisory, crop_name_lower)
            
            return JSONResponse(advisory)
        
        # Generate advisory dynamically if no pre-generated file exists
        advisory = await generate_advisory(crop_name_lower)
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

