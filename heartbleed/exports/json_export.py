import json
from pathlib import Path
from ..core.models import Investigation

def export_to_json(investigation: Investigation, output_path: Path):
    """Exports investigation results to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(investigation.json(indent=4))
    return output_path
