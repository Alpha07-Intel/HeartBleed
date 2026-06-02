import json
from pathlib import Path
from ..core.models import Investigation

def generate_html_report(investigation: Investigation, output_path: Path):
    """Generates an interactive HTML report with relationship graphs."""
    
    # Prepare data for Javascript Graph
    nodes = []
    edges = []
    
    # 1. Central Node (The Target)
    nodes.append({
        "id": "target",
        "label": f"Target: {investigation.input_value}",
        "color": "#e74c3c",
        "size": 30,
        "font": {"size": 20, "color": "#ffffff"}
    })
    
    # 2. Platform Nodes and Primary Edges
    for i, res in enumerate(investigation.correlations):
        p = res.target_profile
        node_id = f"profile_{i}"
        
        # Determine node color based on confidence
        color = "#95a5a6" # Low
        if res.score >= 81: color = "#2ecc71" # Very High
        elif res.score >= 61: color = "#3498db" # High
        elif res.score >= 31: color = "#f1c40f" # Medium
        
        nodes.append({
            "id": node_id,
            "label": f"{p.platform}\n({p.username})",
            "color": color,
            "title": f"Score: {res.score}<br>Confidence: {res.confidence.value}"
        })
        
        # Edge from target to profile (thickness based on score)
        edges.append({
            "from": "target",
            "to": node_id,
            "width": max(1, res.score / 10),
            "label": str(res.score)
        })

    # 3. Cross-Correlation Edges (Visualizing shared metadata)
    for i in range(len(investigation.correlations)):
        for j in range(i + 1, len(investigation.correlations)):
            p1 = investigation.correlations[i].target_profile
            p2 = investigation.correlations[j].target_profile
            
            shared = []
            if p1.website and p2.website and p1.website.lower() == p2.website.lower():
                shared.append("Website")
            if p1.location and p2.location and p1.location.lower() == p2.location.lower():
                shared.append("Location")
                
            if shared:
                edges.append({
                    "from": f"profile_{i}",
                    "to": f"profile_{j}",
                    "dashes": True,
                    "color": "#8e44ad",
                    "label": " & ".join(shared)
                })

    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HeartBleed Report - {investigation.input_value}</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f0f2f5; color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            header {{ background: #c0392b; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ margin: 0; font-size: 24px; }}
            .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat-item {{ border-left: 4px solid #c0392b; padding-left: 15px; }}
            .stat-value {{ font-size: 20px; font-weight: bold; color: #c0392b; }}
            #network-graph {{ height: 600px; border: 1px solid #ddd; background: #ffffff; border-radius: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background: #f8f9fa; color: #666; text-transform: uppercase; font-size: 12px; }}
            .high {{ color: #27ae60; font-weight: bold; }}
            .medium {{ color: #f39c12; }}
            .low {{ color: #e74c3c; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-bottom: 40px; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🩸 HeartBleed v0.1 - Intelligence Report</h1>
                <p>Identity Discovery & Correlation Analysis</p>
            </header>

            <div class="card">
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">Target Identifier</div>
                        <div class="stat-value">{investigation.input_value}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Input Type</div>
                        <div class="stat-value">{investigation.input_type.value}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Profiles Found</div>
                        <div class="stat-value">{len(investigation.profiles)}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Timestamp</div>
                        <div class="stat-value">{investigation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>🕸️ Identity Relationship Graph</h2>
                <div id="network-graph"></div>
            </div>
            
            <div class="card">
                <h2>📄 Discovery Details</h2>
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
                            <td><strong>{p.platform}</strong></td>
                            <td>{p.username}</td>
                            <td>{res.score}</td>
                            <td class="{conf_class}">{res.confidence.value}</td>
                            <td><a href="{p.url}" target="_blank">View Profile ↗</a></td>
                        </tr>
        """
        
    html_template += f"""
                    </tbody>
                </table>
            </div>

            <div class="footer">
                Generated by HeartBleed v0.1 • Developed by Alpha-07
            </div>
        </div>

        <script type="text/javascript">
            // Initialize Vis.js Network
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});

            var container = document.getElementById('network-graph');
            var data = {{
                nodes: nodes,
                edges: edges
            }};
            var options = {{
                nodes: {{
                    shape: 'dot',
                    font: {{ face: 'Segoe UI', size: 14 }}
                }},
                edges: {{
                    arrows: {{ to: {{ enabled: false }} }},
                    font: {{ align: 'middle', size: 10 }}
                }},
                physics: {{
                    stabilization: true,
                    barnesHut: {{
                        gravitationalConstant: -2000,
                        springLength: 150
                    }}
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return output_path
