from typing import Optional
from bs4 import BeautifulSoup
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url
from ..utils.logger import logger

class XCollector(BaseCollector):
    """
    Collector for X (formerly Twitter).
    Note: X is highly restrictive and often blocks unauthenticated scraping.
    """
    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type != InputType.USERNAME:
            return None
            
        url = f"https://x.com/{input_value}"
        # We attempt a fetch, though X often redirects to login
        response = fetch_url(url)
        
        if response and response.status_code == 200:
            # If we get a 200, the profile likely exists
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find OG title for the name
            og_title = soup.find("meta", property="og:title")
            display_name = og_title["content"] if og_title else input_value
            
            return Profile(
                platform="X",
                username=input_value,
                display_name=display_name,
                url=url,
                raw_data={"status": "discovered"}
            )
        
        # Fallback existence check via a different method if possible, 
        # but for OSINT standards, a 200/404 is the primary unauthenticated signal.
        return None
