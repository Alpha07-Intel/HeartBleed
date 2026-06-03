from typing import List
import re

def get_mutations(username: str, limit: int = 5) -> List[str]:
    """
    Generates common variations of a username to expand the search surface.
    """
    if not username:
        return []

    username = username.lower()
    mutations = []
    
    # 1. Underscore / Dot insertions (if not already there)
    if "_" not in username and "." not in username:
        # Split names if camelCase or similar (simplified check)
        parts = re.findall(r'[a-z]+|\d+', username)
        if len(parts) > 1:
            mutations.append("_".join(parts))
            mutations.append(".".join(parts))
    
    # 2. Suffixes
    mutations.append(f"{username}_")
    mutations.append(f"{username}123")
    
    # 3. Prefixes
    mutations.append(f"real{username}")
    mutations.append(f"iam{username}")
    
    # 4. Year patterns (current and common)
    mutations.append(f"{username}2024")
    
    # Filter unique and return limited set
    seen = set()
    seen.add(username)
    final_mutations = []
    for m in mutations:
        if m not in seen:
            final_mutations.append(m)
            seen.add(m)
            if len(final_mutations) >= limit:
                break
                
    return final_mutations
