import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
from ..config import DEFAULT_TIMEOUT, MAX_RETRIES, USER_AGENT
from .logger import logger

def get_session() -> requests.Session:
    """Creates a requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": USER_AGENT})
    return session

def fetch_url(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT) -> Optional[requests.Response]:
    """Fetches a URL with error handling and logging."""
    session = get_session()
    try:
        response = session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.debug(f"Profile not found at {url}")
        else:
            logger.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    return None
