"""Natural language advisory explanation service."""
from __future__ import annotations

import os
from typing import Dict, List, Any, Optional

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

# Template directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEMPLATES_DIR = os.path.join(BACKEND_DIR, "templates", "explanations")

# Initialize Jinja2 environment if available
if JINJA2_AVAILABLE:
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    except Exception:
        env = None
else:
    env = None


def _get_severity_and_confidence(score: float) -> tuple[str, float]:
    """Map rule score to severity and confidence."""
    if score >= 0.8:
        return "high", 0.9
    elif score >= 0.6:
        return "medium", 0.75
    else:
        return "low", 0.5


def _boost_confidence(confidence: float, metrics: Dict[str, Any]) -> float:
    """Boost confidence based on available data sources."""
    boost = 0.0
    
    if metrics.get("ndvi") is not None:
        boost += 0.05
    if metrics.get("market_price") is not None:
        boost += 0.05
    if metrics.get("temperature") is not None:
        boost += 0.03
    
    return min(confidence + boost, 1.0)


def _extract_pest_name(rule_text: str) -> Optional[str]:
    """Extract pest name from rule description."""
    rule_lower = rule_text.lower()
    
    pests = ["bollworm", "aphid", "whitefly", "thrips", "mite", "rust", "blight", "wilt"]
    for pest in pests:
        if pest in rule_lower:
            return pest
    
    return None


def _generate_pest_action(rule_text: str, crop_name: str, severity: str) -> Dict[str, Any]:
    """Generate pest action from rule text."""
    pest_name = _extract_pest_name(rule_text) or "pests"
    
    if pest_name == "bollworm":
        return {
            "title": "Inspect for bollworm",
            "steps": [
                "Walk your field focusing on flowering zone, check underside of leaves for larvae",
                "Apply targeted biological control (Bt) if larvae found, avoid broad-spectrum pesticides"
            ]
        }
    elif pest_name == "aphid":
        return {
            "title": "Inspect for aphids",
            "steps": [
                "Check young leaves and undersides for colonies",
                "Spray neem oil 2% early morning if infestation confirmed"
            ]
        }
    elif pest_name == "whitefly":
        return {
            "title": "Monitor whitefly activity",
            "steps": [
                "Use yellow sticky traps placed at canopy height, check daily",
                "Apply neem-based sprays if trap counts exceed threshold"
            ]
        }
    else:
        return {
            "title": f"Inspect for {pest_name}",
            "steps": [
                "Check field for signs of pest damage",
                "Consult local extension officer for specific treatment recommendations"
            ]
        }


def _generate_irrigation_action(metrics: Dict[str, Any], crop_meta: Dict[str, Any]) -> Dict[str, Any]:
    """Generate irrigation action based on soil moisture and crop requirements."""
    soil_moisture = metrics.get("soil_moisture")
    temperature = metrics.get("temperature")
    rainfall = metrics.get("rainfall", 0)
    
    optimal_min = crop_meta.get("optimal_soil_moisture_min", 40)
    optimal_max = crop_meta.get("optimal_soil_moisture_max", 70)
    
    if soil_moisture is not None:
        if soil_moisture < optimal_min:
            return {
                "title": "Schedule irrigation",
                "steps": [
                    f"Soil moisture ({soil_moisture}%) is below optimal range ({optimal_min}-{optimal_max}%)",
                    "Irrigate within 24-48 hours, ensure even water distribution"
                ]
            }
        elif soil_moisture > optimal_max:
            return {
                "title": "Monitor waterlogging",
                "steps": [
                    f"Soil moisture ({soil_moisture}%) is above optimal range",
                    "Ensure proper drainage, avoid additional irrigation until moisture decreases"
                ]
            }
    
    if temperature is not None and temperature > 35 and rainfall < 5:
        return {
            "title": "Increase irrigation frequency",
            "steps": [
                "High temperature and low rainfall detected",
                "Consider additional irrigation to prevent heat stress"
            ]
        }
    
    return {
        "title": "Continue standard irrigation schedule",
        "steps": [
            "Monitor soil moisture regularly",
            "Adjust based on weather conditions and crop stage"
        ]
    }


def _generate_market_action(metrics: Dict[str, Any], price_change: Optional[float] = None) -> Dict[str, Any]:
    """Generate market action based on price trends."""
    if price_change is None:
        price_change = metrics.get("price_change_percent", 0)
    
    if price_change < -5:
        return {
            "title": "Consider holding produce",
            "steps": [
                f"Market price dropped {abs(price_change):.1f}% — prices may recover",
                "Check storage options, monitor market trends before selling"
            ]
        }
    elif price_change > 5:
        return {
            "title": "Consider selling opportunity",
            "steps": [
                f"Market price increased {price_change:.1f}% — favorable selling conditions",
                "Check nearest mandi prices, consider selling if harvest-ready"
            ]
        }
    else:
        return {
            "title": "Monitor market prices",
            "steps": [
                "Market prices are stable",
                "Continue monitoring for optimal selling window"
            ]
        }


def _generate_actions(
    rule_breakdown: Dict[str, Any],
    fired_rules: List[str],
    metrics: Dict[str, Any],
    crop_meta: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate prioritized actions from rule breakdown."""
    actions = []
    
    # Priority order: pest -> irrigation -> market
    pest_fired = rule_breakdown.get("pest", {}).get("fired", [])
    irrigation_fired = rule_breakdown.get("irrigation", {}).get("fired", [])
    market_fired = rule_breakdown.get("market", {}).get("fired", [])
    
    # Pest actions (max 2)
    if pest_fired:
        for rule in pest_fired[:2]:
            action = _generate_pest_action(rule, crop_meta.get("name", "crop"), "medium")
            actions.append(action)
            if len(actions) >= 3:
                break
    
    # Irrigation actions
    if irrigation_fired and len(actions) < 3:
        action = _generate_irrigation_action(metrics, crop_meta)
        actions.append(action)
    
    # Market actions
    if market_fired and len(actions) < 3:
        price_change = metrics.get("price_change_percent")
        action = _generate_market_action(metrics, price_change)
        actions.append(action)
    
    return actions[:3]  # Return max 3 actions


def _generate_summary(
    crop_meta: Dict[str, Any],
    severity: str,
    fired_rules: List[str],
    metrics: Dict[str, Any],
    district: Optional[str] = None,
) -> str:
    """Generate short summary sentence."""
    crop_name = crop_meta.get("name", "Crop")
    location_part = f" near {district}" if district else ""
    
    # Determine top reason
    top_reason = "normal conditions"
    if fired_rules:
        first_rule = fired_rules[0].lower()
        if "pest" in first_rule or any(p in first_rule for p in ["aphid", "bollworm", "whitefly"]):
            pest_name = _extract_pest_name(first_rule) or "pests"
            top_reason = f"{pest_name} risk"
        elif "irrigation" in first_rule or "moisture" in first_rule:
            top_reason = "irrigation needed"
        elif "market" in first_rule or "price" in first_rule:
            top_reason = "market opportunity"
    
    # Add supporting metrics
    metric_parts = []
    if metrics.get("humidity") is not None:
        metric_parts.append(f"humidity {metrics['humidity']}%")
    if metrics.get("ndvi") is not None and metrics.get("ndvi") < 0.5:
        metric_parts.append("NDVI drop")
    
    metric_text = f" due to {', '.join(metric_parts)}" if metric_parts else ""
    
    severity_text = severity.capitalize()
    
    return f"{severity_text} risk for {crop_name}{location_part} — {top_reason}{metric_text}."


def _generate_why(
    fired_rules: List[str],
    metrics: Dict[str, Any],
    top_metric: Optional[str] = None,
) -> str:
    """Generate 'why we say this' explanation."""
    if not fired_rules:
        return "No significant risks detected based on current data."
    
    # Get top contributing metrics
    metric_parts = []
    if metrics.get("humidity") is not None:
        metric_parts.append(f"humidity ({metrics['humidity']}%)")
    if metrics.get("temperature") is not None:
        metric_parts.append(f"temperature ({metrics['temperature']}°C)")
    if metrics.get("ndvi") is not None:
        metric_parts.append(f"NDVI ({metrics['ndvi']:.2f})")
    if metrics.get("soil_moisture") is not None:
        metric_parts.append(f"soil moisture ({metrics['soil_moisture']}%)")
    
    metric_text = " and ".join(metric_parts[:2]) if metric_parts else "available data"
    
    # Get top rule
    top_rule = fired_rules[0] if fired_rules else "conditions"
    
    return f"{metric_text.capitalize()} indicates stress — matching rule '{top_rule}'."


def _get_data_sources(metrics: Dict[str, Any]) -> List[str]:
    """Determine data sources from available metrics."""
    sources = []
    
    if metrics.get("ndvi") is not None:
        sources.append("Bhuvan")
    if metrics.get("temperature") is not None:
        sources.append("Open-Meteo")
    if metrics.get("market_price") is not None:
        sources.append("Agmarknet")
    
    if not sources:
        sources = ["Fusion Engine"]
    
    return sources


def explain_advisory(
    rule_breakdown: Dict[str, Any],
    fired_rules: List[str],
    metrics: Dict[str, Any],
    crop_meta: Dict[str, Any],
    score: float,
    district: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate natural language explanation for advisory.
    
    Args:
        rule_breakdown: Dictionary with pest/irrigation/market rule results
        fired_rules: List of fired rule descriptions
        metrics: Dictionary of metrics (ndvi, temperature, etc.)
        crop_meta: Crop metadata dictionary
        score: Rule score (0.0-1.0)
        district: Optional district name
    
    Returns:
        Dictionary with summary, actions, why, severity, confidence, data_sources
    """
    # Get severity and confidence
    severity, confidence = _get_severity_and_confidence(score)
    confidence = _boost_confidence(confidence, metrics)
    
    # Generate summary
    summary = _generate_summary(crop_meta, severity, fired_rules, metrics, district)
    
    # Generate actions
    actions = _generate_actions(rule_breakdown, fired_rules, metrics, crop_meta)
    
    # Generate why explanation
    top_metric = None
    if metrics.get("ndvi") is not None:
        top_metric = "ndvi"
    elif metrics.get("humidity") is not None:
        top_metric = "humidity"
    
    why = _generate_why(fired_rules, metrics, top_metric)
    
    # Get data sources
    data_sources = _get_data_sources(metrics)
    
    return {
        "summary": summary,
        "actions": actions,
        "why": why,
        "severity": severity,
        "confidence": round(confidence, 2),
        "data_sources": data_sources,
    }


__all__ = ["explain_advisory"]


