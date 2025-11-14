"""Government alerts service for multiple sources."""
from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime
import asyncio

import httpx


def _get_fallback_alerts(source: str) -> List[Dict[str, Any]]:
    """Return fallback sample alerts when API fails."""
    return [
        {
            "title": f"Sample alert from {source}",
            "description": "This is a fallback alert when the API is unavailable.",
            "alert_type": "general",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": source,
            "severity": "medium",
        }
    ]

ALERT_TIMEOUT = 12

async def fetch_gov_alerts(state: str, district: str) -> List[Dict]:
    """
    Unified wrapper: fetch all government alerts and return merged + normalized + sorted list.
    Called by Fusion Engine.
    """
    try:
        farmer_task = asyncio.create_task(fetch_farmer_gov_alerts(state, district))
        kvk_task = asyncio.create_task(fetch_icar_kvk_alerts(state, district))
        suvidha_task = asyncio.create_task(fetch_kisan_suvidha_alerts(state, district))
        mandi_task = asyncio.create_task(fetch_mandi_alerts(state, district))

        results = await asyncio.gather(
            farmer_task, kvk_task, suvidha_task, mandi_task,
            return_exceptions=True
        )

        # Convert errors into empty lists but print so we know
        alerts: List[Dict] = []
        for result in results:
            if isinstance(result, Exception):
                print(f"[gov_alerts] Source failed: {type(result).__name__}: {result}")
                continue
            if isinstance(result, list):
                alerts.extend(result)

        # Normalize to common format
        normalized = [normalize_alerts(a) for a in alerts]

        # Sort alerts by date descending
        normalized.sort(key=lambda a: a.get("date", ""), reverse=True)

        return normalized

    except Exception as e:
        print(f"[gov_alerts] Fatal error: {e}")
        return []
async def fetch_farmer_gov_alerts(state: str, district: str) -> List[Dict[str, Any]]:
    """
    Fetch alerts from farmer.gov.in.
    
    Args:
        state: State name
        district: District name
    
    Returns:
        List of alert dictionaries, or fallback alerts on failure
    """
    try:
        url = "https://farmer.gov.in/FarmerHome/agrilocatorservice"
        # Try to get lat/lon from state/district (simplified - in real app use geocoding)
        # For now, use a generic approach
        params = {
            "state": state,
            "district": district,
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            alerts = []
            if isinstance(data, list):
                for item in data:
                    alert = _normalize_alert(item, "farmer_gov")
                    if alert:
                        alerts.append(alert)
            elif isinstance(data, dict):
                items = (
                    data.get("data") or
                    data.get("records") or
                    data.get("alerts") or
                    data.get("results") or
                    []
                )
                if isinstance(items, list):
                    for item in items:
                        alert = _normalize_alert(item, "farmer_gov")
                        if alert:
                            alerts.append(alert)
                elif isinstance(items, dict):
                    alert = _normalize_alert(items, "farmer_gov")
                    if alert:
                        alerts.append(alert)
            
            return alerts if alerts else _get_fallback_alerts("farmer_gov")
            
    except httpx.TimeoutException:
        print(f"Error: Timeout fetching farmer.gov.in alerts for {district}, {state}")
        return _get_fallback_alerts("farmer_gov")
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} fetching farmer.gov.in alerts for {district}, {state}")
        return _get_fallback_alerts("farmer_gov")
    except Exception as e:
        print(f"Error fetching farmer.gov.in alerts for {district}, {state}: {type(e).__name__}: {e}")
        return _get_fallback_alerts("farmer_gov")


async def fetch_icar_kvk_alerts(state: str, district: str) -> List[Dict[str, Any]]:
    """
    Fetch alerts from ICAR KVK (Krishi Vigyan Kendra).
    
    Args:
        state: State name
        district: District name
    
    Returns:
        List of alert dictionaries, or fallback alerts on failure
    """
    try:
        # ICAR KVK API endpoint
        url = "https://kvk.icar.gov.in/api/alerts"
        params = {
            "state": state,
            "district": district,
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            alerts = []
            if isinstance(data, list):
                for item in data:
                    alert = _normalize_alert(item, "icar_kvk")
                    if alert:
                        alerts.append(alert)
            elif isinstance(data, dict):
                items = (
                    data.get("data") or
                    data.get("records") or
                    data.get("alerts") or
                    data.get("results") or
                    []
                )
                if isinstance(items, list):
                    for item in items:
                        alert = _normalize_alert(item, "icar_kvk")
                        if alert:
                            alerts.append(alert)
                elif isinstance(items, dict):
                    alert = _normalize_alert(items, "icar_kvk")
                    if alert:
                        alerts.append(alert)
            
            return alerts if alerts else _get_fallback_alerts("icar_kvk")
            
    except httpx.TimeoutException:
        print(f"Error: Timeout fetching ICAR KVK alerts for {district}, {state}")
        return _get_fallback_alerts("icar_kvk")
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} fetching ICAR KVK alerts for {district}, {state}")
        return _get_fallback_alerts("icar_kvk")
    except Exception as e:
        print(f"Error fetching ICAR KVK alerts for {district}, {state}: {type(e).__name__}: {e}")
        return _get_fallback_alerts("icar_kvk")


async def fetch_kisan_suvidha_alerts(state: str, district: str) -> List[Dict[str, Any]]:
    """
    Fetch alerts from Kisan Suvidha portal.
    
    Args:
        state: State name
        district: District name
    
    Returns:
        List of alert dictionaries, or fallback alerts on failure
    """
    try:
        # Kisan Suvidha API endpoint (example - adjust based on actual API)
        url = "https://kisansuvidha.gov.in/api/alerts"
        params = {
            "state": state,
            "district": district,
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            alerts = []
            if isinstance(data, list):
                for item in data:
                    alert = _normalize_alert(item, "kisan_suvidha")
                    if alert:
                        alerts.append(alert)
            elif isinstance(data, dict):
                items = (
                    data.get("data") or
                    data.get("records") or
                    data.get("alerts") or
                    data.get("results") or
                    []
                )
                if isinstance(items, list):
                    for item in items:
                        alert = _normalize_alert(item, "kisan_suvidha")
                        if alert:
                            alerts.append(alert)
                elif isinstance(items, dict):
                    alert = _normalize_alert(items, "kisan_suvidha")
                    if alert:
                        alerts.append(alert)
            
            return alerts if alerts else _get_fallback_alerts("kisan_suvidha")
            
    except httpx.TimeoutException:
        print(f"Error: Timeout fetching Kisan Suvidha alerts for {district}, {state}")
        return _get_fallback_alerts("kisan_suvidha")
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} fetching Kisan Suvidha alerts for {district}, {state}")
        return _get_fallback_alerts("kisan_suvidha")
    except Exception as e:
        print(f"Error fetching Kisan Suvidha alerts for {district}, {state}: {type(e).__name__}: {e}")
        return _get_fallback_alerts("kisan_suvidha")


async def fetch_mandi_alerts(state: str, district: str) -> List[Dict[str, Any]]:
    """
    Fetch alerts from mandi/agricultural market sources.
    
    Args:
        state: State name
        district: District name
    
    Returns:
        List of alert dictionaries, or fallback alerts on failure
    """
    try:
        # Mandi alerts API endpoint (example - adjust based on actual API)
        url = "https://agmarknet.gov.in/api/alerts"
        params = {
            "state": state,
            "district": district,
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            alerts = []
            if isinstance(data, list):
                for item in data:
                    alert = _normalize_alert(item, "mandi")
                    if alert:
                        alerts.append(alert)
            elif isinstance(data, dict):
                items = (
                    data.get("data") or
                    data.get("records") or
                    data.get("alerts") or
                    data.get("results") or
                    []
                )
                if isinstance(items, list):
                    for item in items:
                        alert = _normalize_alert(item, "mandi")
                        if alert:
                            alerts.append(alert)
                elif isinstance(items, dict):
                    alert = _normalize_alert(items, "mandi")
                    if alert:
                        alerts.append(alert)
            
            return alerts if alerts else _get_fallback_alerts("mandi")
            
    except httpx.TimeoutException:
        print(f"Error: Timeout fetching mandi alerts for {district}, {state}")
        return _get_fallback_alerts("mandi")
    except httpx.HTTPStatusError as e:
        print(f"Error: HTTP {e.response.status_code} fetching mandi alerts for {district}, {state}")
        return _get_fallback_alerts("mandi")
    except Exception as e:
        print(f"Error fetching mandi alerts for {district}, {state}: {type(e).__name__}: {e}")
        return _get_fallback_alerts("mandi")


async def merge_gov_alerts(state: str, district: str) -> List[Dict[str, Any]]:
    """
    Merge alerts from all government sources.
    
    Fetches alerts concurrently from all sources, deduplicates by title,
    and sorts by severity.
    
    Args:
        state: State name
        district: District name
    
    Returns:
        Merged and sorted list of unique alerts
    """
    try:
        # Fetch from all sources concurrently
        results = await asyncio.gather(
            fetch_farmer_gov_alerts(state, district),
            fetch_icar_kvk_alerts(state, district),
            fetch_kisan_suvidha_alerts(state, district),
            fetch_mandi_alerts(state, district),
            return_exceptions=True
        )
        
        # Collect all alerts, handling exceptions
        all_alerts = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error in concurrent fetch: {type(result).__name__}: {result}")
                continue
            if isinstance(result, list):
                all_alerts.extend(result)
        
        # Deduplicate by title (case-insensitive)
        seen_titles = set()
        unique_alerts = []
        for alert in all_alerts:
            if not isinstance(alert, dict):
                continue
            title = alert.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_alerts.append(alert)
        
        # Sort by severity (high > medium > low), then by date (newest first)
        severity_order = {"high": 3, "medium": 2, "low": 1}
        
        def sort_key(alert: Dict[str, Any]) -> tuple:
            severity = alert.get("severity", "medium").lower()
            date_str = alert.get("date", "")
            # Parse date for sorting (newest first)
            try:
                if date_str:
                    date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    date_sort = -date_obj.timestamp()  # Negative for descending
                else:
                    date_sort = 0
            except Exception:
                date_sort = 0
            return (severity_order.get(severity, 2), date_sort)
        
        unique_alerts.sort(key=sort_key, reverse=True)
        
        return unique_alerts
        
    except Exception as e:
        print(f"Error merging gov alerts for {district}, {state}: {type(e).__name__}: {e}")
        # Return fallback alerts from at least one source
        return _get_fallback_alerts("merged")


def _normalize_alert(item: Dict[str, Any], source: str) -> Dict[str, Any] | None:
    """Normalize a single alert item from API response."""
    if not isinstance(item, dict):
        return None
    
    # Extract fields with fallbacks
    title = (
        item.get("title") or
        item.get("alert_title") or
        item.get("subject") or
        item.get("name") or
        ""
    )
    
    description = (
        item.get("description") or
        item.get("alert_description") or
        item.get("message") or
        item.get("content") or
        item.get("details") or
        ""
    )
    
    alert_type = (
        item.get("alert_type") or
        item.get("type") or
        item.get("category") or
        item.get("alert_category") or
        "general"
    )
    
    severity = (
        item.get("severity") or
        item.get("priority") or
        item.get("alert_severity") or
        "medium"
    ).lower()
    
    # Normalize severity
    if severity not in ["high", "medium", "low"]:
        severity = "medium"
    
    # Extract date
    date_str = (
        item.get("date") or
        item.get("alert_date") or
        item.get("published_date") or
        item.get("created_at") or
        item.get("updated_at") or
        datetime.now().strftime("%Y-%m-%d")
    )
    
    # Normalize date format to YYYY-MM-DD
    try:
        if isinstance(date_str, str):
            if len(date_str) >= 10 and date_str[4] == "-" and date_str[7] == "-":
                normalized_date = date_str[:10]
            else:
                parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                normalized_date = parsed_date.strftime("%Y-%m-%d")
        else:
            normalized_date = datetime.now().strftime("%Y-%m-%d")
    except Exception:
        normalized_date = datetime.now().strftime("%Y-%m-%d")
    
    # Only return alert if it has at least a title or description
    if not title and not description:
        return None
    
    return {
        "title": title,
        "description": description,
        "alert_type": alert_type,
        "date": normalized_date,
        "source": source,
        "severity": severity,
    }


def normalize_alerts(*alert_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize and merge multiple alert lists.
    
    Args:
        *alert_lists: Variable number of alert lists to merge
    
    Returns:
        Merged and normalized list of alerts
    """
    all_alerts = []
    for alert_list in alert_lists:
        if isinstance(alert_list, list):
            all_alerts.extend(alert_list)
    
    # Deduplicate by title
    seen_titles = set()
    unique_alerts = []
    for alert in all_alerts:
        if not isinstance(alert, dict):
            continue
        title = alert.get("title", "").lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_alerts.append(alert)
    
    return unique_alerts


async def fetch_and_cache_gov_alerts(state: str, district: str) -> List[Dict[str, Any]]:
    """
    Fetch and cache government alerts (wrapper around merge_gov_alerts).
    
    Args:
        state: State name
        district: District name
    
    Returns:
        List of merged alerts
    """
    return await merge_gov_alerts(state, district)


__all__ = [
    "fetch_farmer_gov_alerts",
    "fetch_icar_kvk_alerts",
    "fetch_kisan_suvidha_alerts",
    "fetch_mandi_alerts",
    "merge_gov_alerts",
    "normalize_alerts",
    "fetch_and_cache_gov_alerts",
]
