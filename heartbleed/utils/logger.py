import logging
import sys
from rich.logging import RichHandler

def setup_logger(name: str = "heartbleed", level: int = logging.INFO):
    """Sets up a standardized logger using Rich for beautiful terminal output."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger(name)

logger = setup_logger()
