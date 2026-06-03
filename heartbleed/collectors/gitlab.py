from typing import Optional
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url

class GitLabCollector(BaseCollector):
    def supports(self, input_type: InputType) -> bool:
        return input_type in [InputType.USERNAME, InputType.EMAIL]

    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type == InputType.USERNAME:
            url = f"https://gitlab.com/api/v4/users?username={input_value}"
        elif input_type == InputType.EMAIL:
            # GitLab API allows searching users by email
            url = f"https://gitlab.com/api/v4/users?search={input_value}"
        else:
            return None
            
        response = fetch_url(url)
        
        if response:
            users = response.json()
            if not users:
                return None
            
            # Get full profile for the first match
            user_data = users[0]
            user_id = user_data.get("id")
            detail_url = f"https://gitlab.com/api/v4/users/{user_id}"
            detail_response = fetch_url(detail_url)
            
            if detail_response:
                data = detail_response.json()
                return Profile(
                    platform="GitLab",
                    username=data.get("username"),
                    display_name=data.get("name"),
                    bio=data.get("bio"),
                    location=data.get("location"),
                    website=data.get("website_url"),
                    avatar=data.get("avatar_url"),
                    followers=0,
                    url=data.get("web_url"),
                    raw_data=data
                )
        return None
