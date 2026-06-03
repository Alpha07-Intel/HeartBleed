import requests
from typing import List, Set
from ...utils.network import fetch_url
from ...utils.logger import logger

def get_subdomains(domain: str) -> List[str]:
    """
    Identifies subdomains using public Certificate Transparency logs (crt.sh).
    """
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    
    subdomains: Set[str] = set()
    response = fetch_url(url)
    
    if response and response.status_code == 200:
        try:
            data = response.json()
            for entry in data:
                name_value = entry.get("name_value")
                if name_value:
                    # crt.sh can return multiple names in one field
                    for name in name_value.split('\n'):
                        name = name.strip().lower()
                        if name.endswith(domain) and "*" not in name:
                            subdomains.add(name)
        except Exception as e:
            logger.debug(f"Error parsing crt.sh data: {e}")
            
    return sorted(list(subdomains))
