import re
from typing import List, Dict, Set

def extract_keywords(bios: List[str]) -> Dict[str, List[str]]:
    """
    Rule-based extraction of interests, roles, and tech from a list of bio strings.
    """
    results = {
        "Roles": set(),
        "Tech Stack": set(),
        "Social/Interests": set()
    }

    # Pre-defined keyword lists
    rules = {
        "Roles": ["developer", "engineer", "founder", "ceo", "cto", "student", "researcher", "analyst", "designer", "architect", "hacker"],
        "Tech Stack": ["python", "rust", "javascript", "golang", "java", "c++", "linux", "docker", "cloud", "aws", "cybersecurity", "ai", "machine learning"],
        "Social/Interests": ["gamer", "traveler", "photography", "crypto", "web3", "osint", "fitness", "music", "art"]
    }

    for bio in bios:
        if not bio: continue
        bio_lower = bio.lower()
        
        for category, keywords in rules.items():
            for kw in keywords:
                # Use word boundaries for accurate matching
                if re.search(rf'\b{kw}\b', bio_lower):
                    results[category].add(kw.capitalize())

    # Convert sets to sorted lists for stability
    return {k: sorted(list(v)) for k, v in results.items()}
