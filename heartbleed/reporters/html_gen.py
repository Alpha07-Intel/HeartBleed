from pathlib import Path
from ..core.models import Investigation

def generate_html_report(investigation: Investigation, output_path: Path):
    """Generates a simple standalone HTML report."""
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>HeartBleed Report - {investigation.input_value}</title>
        <style>
            body {{ font-family: sans-serif; margin: 40px; background: #f4f4f9; }}
            .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            .high {{ color: green; font-weight: bold; }}
            .medium {{ color: orange; }}
            .low {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>HeartBleed Investigation Report</h1>
        <div class="card">
            <p><strong>Target:</strong> {investigation.input_value} ({investigation.input_type.value})</p>
            <p><strong>Timestamp:</strong> {investigation.timestamp}</p>
        </div>
        
        <div class="card">
            <h2>Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Platform</th>
                        <th>Username</th>
                        <th>Score</th>
                        <th>Confidence</th>
                        <th>URL</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for res in investigation.correlations:
        p = res.target_profile
        conf_class = res.confidence.value.lower().replace(" ", "-")
        html_template += f"""
                    <tr>
                        <td>{p.platform}</td>
                        <td>{p.username}</td>
                        <td>{res.score}</td>
                        <td class="{conf_class}">{res.confidence.value}</td>
                        <td><a href="{p.url}" target="_blank">{p.url}</a></td>
                    </tr>
        """
        
    html_template += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return output_path
