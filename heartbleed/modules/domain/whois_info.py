import requests
from typing import Dict, Any, Optional
from ...utils.network import fetch_url
from ...utils.logger import logger

def get_whois_data(domain: str) -> Optional[Dict[str, Any]]:
    """
    Fetches basic WHOIS data for a domain using a public API.
    """
    # Using a public unauthenticated WHOIS API
    url = f"https://rdap.org/domain/{domain}"
    
    response = fetch_url(url)
    if response and response.status_code == 200:
        try:
            data = response.json()
            # Extract basic info from RDAP
            results = {
                "Domain": domain,
                "Registrar": data.get("entities", [{}])[0].get("vcardArray", [None, [["", "", "text", "Unknown"]]])[1][1][3],
                "Created": None,
                "Status": data.get("status", ["Unknown"])[0]
            }
            # Attempt to find creation date
            for event in data.get("events", []):
                if event.get("eventAction") == "registration":
                    results["Created"] = event.get("eventDate")
            return results
        except Exception as e:
            logger.debug(f"Error parsing WHOIS/RDAP data: {e}")
    return None
