from typing import Optional
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url

class GitHubCollector(BaseCollector):
    def supports(self, input_type: InputType) -> bool:
        return input_type in [InputType.USERNAME, InputType.EMAIL]

    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type == InputType.USERNAME:
            url = f"https://api.github.com/users/{input_value}"
        elif input_type == InputType.EMAIL:
            # GitHub API allows searching users by email
            url = f"https://api.github.com/search/users?q={input_value}"
        else:
            return None
            
        response = fetch_url(url)
        
        if response:
            data = response.json()
            
            if input_type == InputType.EMAIL:
                if data.get("total_count", 0) > 0:
                    # Get the first match
                    user_login = data["items"][0]["login"]
                    # Fetch full profile for the login
                    return self.fetch(InputType.USERNAME, user_login)
                return None

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
