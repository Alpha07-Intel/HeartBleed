from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class InputType(str, Enum):
    USERNAME = "username"
    EMAIL = "email"
    FULL_NAME = "full_name"

class ConfidenceLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"

class Profile(BaseModel):
    platform: str
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    avatar: Optional[str] = None
    followers: Optional[int] = 0
    url: str
    raw_data: Optional[Dict[str, Any]] = None

class CorrelationResult(BaseModel):
    target_profile: Profile
    score: int = 0
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    match_reasons: List[str] = []

class Investigation(BaseModel):
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    input_type: InputType
    input_value: str
    profiles: List[Profile] = []
    correlations: List[CorrelationResult] = []
    dorks: List[Dict[str, str]] = []
    persona_profile: Dict[str, List[str]] = {}
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "input_type": self.input_type,
            "input_value": self.input_value,
            "results_count": len(self.profiles)
        }

class Workspace(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    investigation_ids: List[int] = []
