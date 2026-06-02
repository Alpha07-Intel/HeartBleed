import re
from typing import Optional
from bs4 import BeautifulSoup
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url
from ..utils.logger import logger

class InstagramCollector(BaseCollector):
    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type != InputType.USERNAME:
            return None
            
        url = f"https://www.instagram.com/{input_value}/"
        # We try to fetch the page and extract meta tags
        response = fetch_url(url)
        
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Instagram often hides data, but OG tags might be present
            meta_desc = soup.find("meta", property="og:description")
            description = meta_desc["content"] if meta_desc else ""
            
            # Example description: "1,234 Followers, 567 Following, 89 Posts - See Instagram photos and videos from Name (@username)"
            display_name = input_value
            bio = description
            
            name_match = re.search(r"from (.*) \(@", description)
            if name_match:
                display_name = name_match.group(1)
            
            return Profile(
                platform="Instagram",
                username=input_value,
                display_name=display_name,
                bio=bio,
                url=url,
                raw_data={"html_found": True}
            )
        return None
