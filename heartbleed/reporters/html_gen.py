import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from ..core.models import Investigation, Workspace

def generate_html_report(investigation: Investigation, output_path: Path):
    """Generates an interactive HTML report for a single target."""
    nodes = []
    edges = []
    
    # Central Node
    nodes.append({
        "id": "target",
        "label": f"Target: {investigation.input_value}",
        "color": "#e74c3c",
        "shape": "star",
        "size": 30,
        "font": {"size": 20, "color": "#ffffff"}
    })
    
    for i, res in enumerate(investigation.correlations):
        p = res.target_profile
        node_id = f"profile_{i}"
        
        color = "#95a5a6"
        if res.score >= 81: color = "#2ecc71"
        elif res.score >= 61: color = "#3498db"
        elif res.score >= 31: color = "#f1c40f"
        
        nodes.append({
            "id": node_id,
            "label": f"{p.platform}\n({p.username})",
            "color": color,
            "title": f"Score: {res.score}<br>Confidence: {res.confidence.value}"
        })
        
        edges.append({
            "from": "target",
            "to": node_id,
            "width": max(1, res.score / 10),
            "label": str(res.score)
        })

    # Shared Metadata Edges (Intra-target)
    for i in range(len(investigation.correlations)):
        for j in range(i + 1, len(investigation.correlations)):
            p1 = investigation.correlations[i].target_profile
            p2 = investigation.correlations[j].target_profile
            shared = []
            if p1.website and p2.website and p1.website.lower() == p2.website.lower(): shared.append("Website")
            if p1.location and p2.location and p1.location.lower() == p2.location.lower(): shared.append("Location")
            if shared:
                edges.append({
                    "from": f"profile_{i}", "to": f"profile_{j}",
                    "dashes": True, "color": "#8e44ad", "label": " & ".join(shared)
                })

    html_template = _get_html_template(
        title=f"HeartBleed Report - {investigation.input_value}",
        header_title=f"🩸 HeartBleed v0.1 - Intelligence Report",
        header_subtitle=f"Target: {investigation.input_value}",
        stats=[
            ("Target", investigation.input_value),
            ("Profiles", str(len(investigation.profiles))),
            ("Timestamp", investigation.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        ],
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps(edges),
        results_html=_generate_results_table(investigation.correlations)
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return output_path

def generate_workspace_report(workspace: Workspace, investigations: List[Investigation], output_path: Path):
    """Generates an advanced consolidated report with Hub Mapping for workspaces."""
    nodes = []
    edges = []
    unique_profiles = {} # Key: (platform, username) -> node_id
    all_correlations = []
    
    # 1. Add Target Nodes
    for inv in investigations:
        target_node_id = f"target_{inv.id}"
        nodes.append({
            "id": target_node_id,
            "label": f"TARGET\n{inv.input_value}",
            "color": "#e74c3c",
            "shape": "star",
            "size": 25,
            "font": {"size": 16, "color": "#ffffff"}
        })
        
        # 2. Add Profile Nodes (with deduplication / Hub logic)
        for i, res in enumerate(inv.correlations):
            all_correlations.append(res)
            p = res.target_profile
            profile_key = (p.platform.lower(), p.username.lower())
            
            if profile_key not in unique_profiles:
                # Create a new node for this unique account
                node_id = f"profile_unique_{len(unique_profiles)}"
                unique_profiles[profile_key] = node_id
                
                color = "#95a5a6"
                if res.score >= 81: color = "#2ecc71"
                elif res.score >= 61: color = "#3498db"
                elif res.score >= 31: color = "#f1c40f"
                
                nodes.append({
                    "id": node_id,
                    "label": f"{p.platform}\n({p.username})",
                    "color": color,
                    "title": f"Discovery Details:<br>Platform: {p.platform}<br>User: {p.username}"
                })
            
            # Draw edge from THIS target to the (possibly shared) profile node
            edges.append({
                "from": target_node_id,
                "to": unique_profiles[profile_key],
                "width": max(1, res.score / 10),
                "label": str(res.score),
                "title": f"Correlation for {inv.input_value}: {res.score}"
            })

    # 3. Cross-Target Metadata Edges (Shared Location/Website across targets)
    # Get flat list of all unique profile objects we have
    profile_list = []
    for inv in investigations:
        for res in inv.correlations:
            p = res.target_profile
            profile_list.append({"p": p, "node_id": unique_profiles[(p.platform.lower(), p.username.lower())]})

    for i in range(len(profile_list)):
        for j in range(i + 1, len(profile_list)):
            p1_data, p2_data = profile_list[i], profile_list[j]
            p1, p2 = p1_data["p"], p2_data["p"]
            
            # Only connect DIFFERENT nodes (don't connect a node to itself)
            if p1_data["node_id"] == p2_data["node_id"]:
                continue
                
            shared = []
            if p1.website and p2.website and p1.website.lower() == p2.website.lower(): shared.append("Website")
            if p1.location and p2.location and p1.location.lower() == p2.location.lower(): shared.append("Location")
            
            if shared:
                edges.append({
                    "from": p1_data["node_id"],
                    "to": p2_data["node_id"],
                    "dashes": True,
                    "color": "#8e44ad",
                    "width": 2,
                    "label": " & ".join(shared)
                })

    html_template = _get_html_template(
        title=f"HeartBleed Workspace Report - {workspace.name}",
        header_title=f"🩸 Workspace Hub: {workspace.name}",
        header_subtitle=workspace.description or "Consolidated Identity Mapping",
        stats=[
            ("Targets", str(len(investigations))),
            ("Shared Profiles", str(len(unique_profiles))),
            ("Created", workspace.created_at.strftime('%Y-%m-%d'))
        ],
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps(edges),
        results_html=_generate_results_table(all_correlations)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return output_path

def _generate_results_table(correlations) -> str:
    html = "<table><thead><tr><th>Platform</th><th>Username</th><th>Score</th><th>Confidence</th><th>URL</th></tr></thead><tbody>"
    for res in correlations:
        p = res.target_profile
        conf_class = res.confidence.value.lower().replace(" ", "-")
        html += f"""<tr><td><strong>{p.platform}</strong></td><td>{p.username}</td><td>{res.score}</td><td class="{conf_class}">{res.confidence.value}</td><td><a href="{p.url}" target="_blank">View Profile ↗</a></td></tr>"""
    html += "</tbody></table>"
    return html

def _get_html_template(title, header_title, header_subtitle, stats, nodes_json, edges_json, results_html) -> str:
    stats_html = "".join([f'<div class="stat-item"><div class="stat-label">{l}</div><div class="stat-value">{v}</div></div>' for l, v in stats])
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f2f5; color: #333; }}
            .container {{ max-width: 1300px; margin: 0 auto; padding: 20px; }}
            header {{ background: #c0392b; color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
            h1 {{ margin: 0; font-size: 28px; }}
            .card {{ background: white; padding: 25px; margin-bottom: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat-item {{ border-left: 5px solid #c0392b; padding-left: 20px; background: #fff8f8; padding: 15px; border-radius: 0 8px 8px 0; }}
            .stat-value {{ font-size: 22px; font-weight: bold; color: #c0392b; }}
            #network-graph {{ height: 700px; border: 1px solid #ddd; background: #ffffff; border-radius: 12px; }}
            .legend {{ display: flex; gap: 20px; margin-top: 15px; font-size: 13px; justify-content: center; }}
            .legend-item {{ display: flex; align-items: center; gap: 8px; }}
            .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background: #f8f9fa; color: #666; font-size: 12px; }}
            .very-high {{ color: #27ae60; font-weight: bold; }} .high {{ color: #2980b9; }} .medium {{ color: #f39c12; }} .low {{ color: #e74c3c; }}
            .footer {{ text-align: center; color: #999; font-size: 13px; margin: 40px 0; }}
            a {{ color: #3498db; text-decoration: none; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{header_title}</h1>
                <p>{header_subtitle}</p>
            </header>
            <div class="card"><div class="stats-grid">{stats_html}</div></div>
            <div class="card">
                <h2>🕸️ Identity Intelligence Graph</h2>
                <div id="network-graph"></div>
                <div class="legend">
                    <div class="legend-item"><div class="dot" style="background: #e74c3c; border-radius: 2px;"></div> Target</div>
                    <div class="legend-item"><div class="dot" style="background: #2ecc71;"></div> Very High Confidence</div>
                    <div class="legend-item"><div class="dot" style="background: #3498db;"></div> High Confidence</div>
                    <div class="legend-item"><div class="dot" style="background: #f1c40f;"></div> Medium Confidence</div>
                    <div class="legend-item"><div class="dot" style="background: #95a5a6;"></div> Low Confidence</div>
                </div>
            </div>
            <div class="card"><h2>📄 Discovery Details</h2>{results_html}</div>
            <div class="footer">Generated by HeartBleed v0.1 • Developed by Alpha-07</div>
        </div>
        <script type="text/javascript">
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});
            var container = document.getElementById('network-graph');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{ shape: 'dot', font: {{ face: 'Segoe UI', size: 14 }} }},
                edges: {{ arrows: {{ to: {{ enabled: false }} }}, font: {{ align: 'middle', size: 10 }}, color: {{ color: '#bdc3c7', highlight: '#c0392b' }} }},
                physics: {{ stabilization: true, barnesHut: {{ gravitationalConstant: -3000, springLength: 150 }} }},
                interaction: {{ hover: true, tooltipDelay: 200 }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
