from typing import Optional
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url

class GitHubCollector(BaseCollector):
    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type != InputType.USERNAME:
            return None
            
        url = f"https://api.github.com/users/{input_value}"
        response = fetch_url(url)
        
        if response:
            data = response.json()
            return Profile(
                platform="GitHub",
                username=data.get("login"),
                display_name=data.get("name"),
                bio=data.get("bio"),
                location=data.get("location"),
                website=data.get("blog"),
                avatar=data.get("avatar_url"),
                followers=data.get("followers"),
                url=data.get("html_url"),
                raw_data=data
            )
        return None
