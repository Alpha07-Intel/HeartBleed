from typing import List, Dict
from ..core.models import Profile, CorrelationResult, ConfidenceLevel
from ..config import (
    MATCH_USERNAME_EXACT, MATCH_USERNAME_SIMILAR, MATCH_WEBSITE,
    MATCH_LOCATION, MATCH_BIO, MATCH_IMAGE,
    CONFIDENCE_VERY_HIGH, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
)

class CorrelationEngine:
    """Analyzes profiles to determine the likelihood they belong to the same person."""
    
    def __init__(self, input_value: str):
        self.input_value = input_value.lower()

    def correlate(self, profile: Profile) -> CorrelationResult:
        """Calculates a correlation score for a single profile against the initial input."""
        score = 0
        reasons = []
        
        # 1. Username Match
        username_lower = profile.username.lower()
        if username_lower == self.input_value:
            score += MATCH_USERNAME_EXACT
            reasons.append(f"Exact username match: {profile.username}")
        elif self.input_value in username_lower or username_lower in self.input_value:
            score += MATCH_USERNAME_SIMILAR
            reasons.append(f"Similar username: {profile.username}")
            
        # 2. Website Match (Placeholder logic - ideally compared against other found profiles)
        if profile.website:
            # For MVP, we just check if it exists; future versions will cross-reference
            pass

        # 3. Location/Bio (Basic keyword matching or existence check)
        if profile.location:
             # Basic boost for providing a location
             pass
             
        # Determine Confidence
        confidence = ConfidenceLevel.LOW
        if score >= CONFIDENCE_VERY_HIGH:
            confidence = ConfidenceLevel.VERY_HIGH
        elif score >= CONFIDENCE_HIGH:
            confidence = ConfidenceLevel.HIGH
        elif score >= CONFIDENCE_MEDIUM:
            confidence = ConfidenceLevel.MEDIUM
            
        return CorrelationResult(
            target_profile=profile,
            score=min(score, 100),
            confidence=confidence,
            match_reasons=reasons
        )

    def correlate_batch(self, profiles: List[Profile]) -> List[CorrelationResult]:
        """Correlates a list of profiles and cross-references them."""
        results = []
        for p in profiles:
            result = self.correlate(p)
            results.append(result)
            
        # Cross-correlation: Boost scores if profiles share metadata
        self._cross_correlate(results)
        return results

    def _cross_correlate(self, results: List[CorrelationResult]):
        """Internal method to boost scores based on shared attributes between profiles."""
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                p1 = results[i].target_profile
                p2 = results[j].target_profile
                
                # Shared Website
                if p1.website and p2.website and p1.website.lower() == p2.website.lower():
                    results[i].score += MATCH_WEBSITE
                    results[j].score += MATCH_WEBSITE
                    results[i].match_reasons.append(f"Shared website with {p2.platform}: {p1.website}")
                    results[j].match_reasons.append(f"Shared website with {p1.platform}: {p2.website}")

                # Shared Location
                if p1.location and p2.location and p1.location.lower() == p2.location.lower():
                    results[i].score += MATCH_LOCATION
                    results[j].score += MATCH_LOCATION
                    results[i].match_reasons.append(f"Shared location with {p2.platform}: {p1.location}")
                    results[j].match_reasons.append(f"Shared location with {p1.platform}: {p2.location}")

        # Recalculate confidence after boosts
        for res in results:
            res.score = min(res.score, 100)
            if res.score >= CONFIDENCE_VERY_HIGH:
                res.confidence = ConfidenceLevel.VERY_HIGH
            elif res.score >= CONFIDENCE_HIGH:
                res.confidence = ConfidenceLevel.HIGH
            elif res.score >= CONFIDENCE_MEDIUM:
                res.confidence = ConfidenceLevel.MEDIUM
