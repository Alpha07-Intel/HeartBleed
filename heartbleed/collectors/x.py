from typing import Optional
from bs4 import BeautifulSoup
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url
from ..utils.logger import logger

class XCollector(BaseCollector):
    """
    Collector for X (formerly Twitter).
    """
    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type != InputType.USERNAME:
            return None
            
        url = f"https://x.com/{input_value}"
        response = fetch_url(url)
        
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find OG tags
            og_title = soup.find("meta", property="og:title")
            og_image = soup.find("meta", property="og:image")
            og_desc = soup.find("meta", property="og:description")
            
            display_name = og_title["content"] if og_title else input_value
            # Remove "on X" from title if present
            if " on X" in display_name:
                display_name = display_name.replace(" on X", "")

            return Profile(
                platform="X",
                username=input_value,
                display_name=display_name,
                bio=og_desc["content"] if og_desc else None,
                avatar=og_image["content"] if og_image else None,
                url=url,
                raw_data={"status": "discovered"}
            )
        return None
