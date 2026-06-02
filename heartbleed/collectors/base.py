from abc import ABC, abstractmethod
from typing import List, Optional
from ..core.models import Profile, InputType

class BaseCollector(ABC):
    """Abstract Base Class for all platform collectors."""
    
    def __init__(self):
        self.platform_name = self.__class__.__name__.replace("Collector", "").lower()

    @abstractmethod
    def fetch(self, input_type: InputType, input_value: str) -> Optional[Profile]:
        """
        Fetches public profile data from the platform.
        Must be implemented by subclasses.
        """
        pass

    def supports(self, input_type: InputType) -> bool:
        """Checks if the collector supports the given input type. Default is Username."""
        return input_type == InputType.USERNAME
