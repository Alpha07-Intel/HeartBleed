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
        response = fetch_url(url)
        
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Meta Tags
            meta_desc = soup.find("meta", property="og:description")
            meta_image = soup.find("meta", property="og:image")
            meta_title = soup.find("meta", property="og:title")
            
            description = meta_desc["content"] if meta_desc else ""
            avatar = meta_image["content"] if meta_image else None
            
            display_name = input_value
            if meta_title:
                # Meta title usually is "Name (@username) • Instagram photos and videos"
                title_text = meta_title["content"]
                if " (@" in title_text:
                    display_name = title_text.split(" (@")[0]

            return Profile(
                platform="Instagram",
                username=input_value,
                display_name=display_name,
                bio=description,
                avatar=avatar,
                url=url,
                raw_data={"html_found": True}
            )
        return None
