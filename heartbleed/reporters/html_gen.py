import json
from datetime import datetime
from pathlib import Path
from typing import List
from ..core.models import Investigation, Workspace

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

    html_template = _get_html_template(
        title=f"HeartBleed Report - {investigation.input_value}",
        header_title=f"🩸 HeartBleed v0.1 - Intelligence Report",
        header_subtitle="Identity Discovery & Correlation Analysis",
        stats=[
            ("Target Identifier", investigation.input_value),
            ("Input Type", investigation.input_type.value),
            ("Profiles Found", str(len(investigation.profiles))),
            ("Timestamp", investigation.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        ],
        nodes_json=nodes_json,
        edges_json=edges_json,
        results_html=_generate_results_table(investigation.correlations)
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return output_path

def generate_workspace_report(workspace: Workspace, investigations: List[Investigation], output_path: Path):
    """Generates a consolidated report for an entire workspace."""
    
    nodes = []
    edges = []
    all_correlations = []
    
    # 1. Target Nodes
    for inv in investigations:
        target_id = f"target_{inv.id}"
        nodes.append({
            "id": target_id,
            "label": f"Target: {inv.input_value}",
            "color": "#e74c3c",
            "size": 25,
            "font": {"size": 16, "color": "#ffffff"}
        })
        
        # 2. Profile Nodes for each target
        for i, res in enumerate(inv.correlations):
            all_correlations.append(res)
            p = res.target_profile
            # Global unique ID for profiles in the workspace
            node_id = f"profile_{inv.id}_{i}"
            
            color = "#95a5a6"
            if res.score >= 81: color = "#2ecc71"
            elif res.score >= 61: color = "#3498db"
            elif res.score >= 31: color = "#f1c40f"
            
            nodes.append({
                "id": node_id,
                "label": f"{p.platform}\n({p.username})",
                "color": color,
                "title": f"Target: {inv.input_value}<br>Score: {res.score}"
            })
            
            edges.append({
                "from": target_id,
                "to": node_id,
                "width": max(1, res.score / 10),
                "label": str(res.score)
            })

    # 3. Cross-Target Metadata Correlation
    # We compare every profile against every other profile in the workspace
    total_profiles = []
    for inv in investigations:
        for i, res in enumerate(inv.correlations):
            total_profiles.append({
                "id": f"profile_{inv.id}_{i}",
                "profile": res.target_profile,
                "target": inv.input_value
            })

    for i in range(len(total_profiles)):
        for j in range(i + 1, len(total_profiles)):
            tp1 = total_profiles[i]
            tp2 = total_profiles[j]
            p1, p2 = tp1["profile"], tp2["profile"]
            
            shared = []
            if p1.website and p2.website and p1.website.lower() == p2.website.lower():
                shared.append("Website")
            if p1.location and p2.location and p1.location.lower() == p2.location.lower():
                shared.append("Location")
            # If same username across different targets!
            if p1.username.lower() == p2.username.lower() and tp1["target"] != tp2["target"]:
                shared.append("Username")
                
            if shared:
                edges.append({
                    "from": tp1["id"],
                    "to": tp2["id"],
                    "dashes": True,
                    "color": "#8e44ad",
                    "width": 2,
                    "label": " & ".join(shared)
                })

    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    html_template = _get_html_template(
        title=f"HeartBleed Workspace Report - {workspace.name}",
        header_title=f"🩸 Workspace: {workspace.name}",
        header_subtitle=workspace.description or "Consolidated Identity Intelligence",
        stats=[
            ("Targets Analyzed", str(len(investigations))),
            ("Total Profiles", str(len(total_profiles))),
            ("Workspace ID", str(workspace.id)),
            ("Generated At", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ],
        nodes_json=nodes_json,
        edges_json=edges_json,
        results_html=_generate_results_table(all_correlations)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return output_path

def _generate_results_table(correlations) -> str:
    html = """
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
    for res in correlations:
        p = res.target_profile
        conf_class = res.confidence.value.lower().replace(" ", "-")
        html += f"""
            <tr>
                <td><strong>{p.platform}</strong></td>
                <td>{p.username}</td>
                <td>{res.score}</td>
                <td class="{conf_class}">{res.confidence.value}</td>
                <td><a href="{p.url}" target="_blank">View Profile ↗</a></td>
            </tr>
        """
    html += "</tbody></table>"
    return html

def _get_html_template(title, header_title, header_subtitle, stats, nodes_json, edges_json, results_html) -> str:
    stats_html = ""
    for label, value in stats:
        stats_html += f"""
            <div class="stat-item">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
            </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
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
            .very-high {{ color: #27ae60; font-weight: bold; }}
            .high {{ color: #2980b9; }}
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
                <h1>{header_title}</h1>
                <p>{header_subtitle}</p>
            </header>

            <div class="card">
                <div class="stats-grid">
                    {stats_html}
                </div>
            </div>

            <div class="card">
                <h2>🕸️ Identity Relationship Graph</h2>
                <div id="network-graph"></div>
            </div>
            
            <div class="card">
                <h2>📄 Discovery Details</h2>
                {results_html}
            </div>

            <div class="footer">
                Generated by HeartBleed v0.1 • Developed by Alpha-07
            </div>
        </div>

        <script type="text/javascript">
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});

            var container = document.getElementById('network-graph');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{ shape: 'dot', font: {{ face: 'Segoe UI', size: 14 }} }},
                edges: {{ arrows: {{ to: {{ enabled: false }} }}, font: {{ align: 'middle', size: 10 }} }},
                physics: {{
                    stabilization: true,
                    barnesHut: {{ gravitationalConstant: -2000, springLength: 150 }}
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
