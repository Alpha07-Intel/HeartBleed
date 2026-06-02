from typing import Optional
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url
from ..utils.logger import logger

class RedditCollector(BaseCollector):
    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type != InputType.USERNAME:
            return None
            
        # Reddit allows public JSON access to user info
        url = f"https://www.reddit.com/user/{input_value}/about.json"
        
        # Reddit is aggressive with bot detection, we rely on our USER_AGENT in network.py
        response = fetch_url(url)
        
        if response:
            try:
                data = response.json().get("data", {})
                if not data:
                    return None
                    
                return Profile(
                    platform="Reddit",
                    username=data.get("name"),
                    display_name=data.get("display_name"),
                    bio=data.get("public_description"),
                    location=None, # Reddit doesn't have a standard location field
                    website=None,
                    avatar=data.get("icon_img"),
                    followers=data.get("subscribers", 0),
                    url=f"https://www.reddit.com/user/{input_value}",
                    raw_data=data
                )
            except Exception as e:
                logger.debug(f"Error parsing Reddit response: {e}")
        return None
