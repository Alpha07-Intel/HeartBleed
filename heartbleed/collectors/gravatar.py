import hashlib
from typing import Optional
from .base import BaseCollector
from ..core.models import Profile, InputType
from ..utils.network import fetch_url
from ..utils.logger import logger

class GravatarCollector(BaseCollector):
    """
    Collector for Gravatar profiles using email hashing.
    """
    def supports(self, input_type: InputType) -> bool:
        return input_type == InputType.EMAIL

    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        if input_type != InputType.EMAIL:
            return None
            
        # Gravatar uses MD5 hash of the email
        email_hash = hashlib.md5(input_value.lower().strip().encode('utf-8')).hexdigest()
        url = f"https://en.gravatar.com/{email_hash}.json"
        
        response = fetch_url(url)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                entry = data.get("entry", [{}])[0]
                
                return Profile(
                    platform="Gravatar",
                    username=entry.get("preferredUsername", input_value.split("@")[0]),
                    display_name=entry.get("displayName"),
                    bio=entry.get("aboutMe"),
                    location=entry.get("currentLocation"),
                    website=entry.get("urls", [{}])[0].get("value") if entry.get("urls") else None,
                    avatar=entry.get("thumbnailUrl"),
                    url=entry.get("profileUrl"),
                    raw_data=entry
                )
            except Exception as e:
                logger.debug(f"Error parsing Gravatar response: {e}")
        return None
