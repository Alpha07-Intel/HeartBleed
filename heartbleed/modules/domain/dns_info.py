import requests
from typing import Dict, List, Any, Optional
from ...utils.network import fetch_url
from ...utils.logger import logger

def get_dns_records(domain: str) -> Dict[str, List[str]]:
    """
    Fetches key DNS records (MX, TXT) for a domain via Cloudflare DoH API.
    """
    results = {
        "MX": [],
        "TXT": []
    }
    
    # Types to fetch
    for record_type in ["MX", "TXT"]:
        url = f"https://cloudflare-dns.com/query?name={domain}&type={record_type}"
        headers = {"Accept": "application/dns-json"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for answer in data.get("Answer", []):
                    results[record_type].append(answer.get("data").strip('"'))
        except Exception as e:
            logger.debug(f"Error fetching {record_type} records: {e}")
            
    return results
