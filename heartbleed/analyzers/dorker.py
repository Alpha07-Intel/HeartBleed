from typing import List, Dict
import urllib.parse

def generate_dorks(value: str) -> List[Dict[str, str]]:
    """
    Generates specialized Google Dork links for a given target identifier.
    """
    encoded_value = urllib.parse.quote(f'"{value}"')
    
    dorks = [
        {
            "name": "Social Media Discovery",
            "description": "Searches for the identifier across major social platforms.",
            "url": f"https://www.google.com/search?q=site:linkedin.com+OR+site:facebook.com+OR+site:twitter.com+OR+site:instagram.com+{encoded_value}"
        },
        {
            "name": "Code & Technical",
            "description": "Checks for technical presence on GitHub, GitLab, and StackOverflow.",
            "url": f"https://www.google.com/search?q=site:github.com+OR+site:gitlab.com+OR+site:stackoverflow.com+{encoded_value}"
        },
        {
            "name": "Leaked Data & Pastes",
            "description": "Searches for the identifier on Pastebin and document sharing sites.",
            "url": f"https://www.google.com/search?q=site:pastebin.com+OR+site:ghostbin.com+OR+site:scribd.com+{encoded_value}"
        },
        {
            "name": "Files & Documents",
            "description": "Searches for PDFs, Docx, or XLS files mentioning the target.",
            "url": f"https://www.google.com/search?q={encoded_value}+filetype:pdf+OR+filetype:docx+OR+filetype:xls"
        },
        {
            "name": "Specific Domain Search",
            "description": "Finds mentions of the target on specific high-value domains.",
            "url": f"https://www.google.com/search?q=site:medium.com+OR+site:reddit.com+OR+site:quora.com+{encoded_value}"
        }
    ]
    return dorks
