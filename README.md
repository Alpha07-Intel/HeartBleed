# HeartBleed OSINT Toolkit 🩸 v0.2

HeartBleed is a modular, high-performance command-line OSINT toolkit designed to discover and correlate publicly available social media and online accounts belonging to a target individual.

**Developed by: Alpha-07**

## 🚀 Features

- **Concurrent Collection**: Parallelized platform scanning for maximum speed.
- **Identity Correlation**: Advanced scoring engine to determine profile ownership probability.
- **Platform Support**: GitHub, GitLab, Reddit, Instagram, and X (Twitter).
- **Username Mutation**: Automatically check variations like `user_`, `user123`, `realuser` (`--mutate`).
- **Digital Footprint Dorker**: Instant clickable links for Pastebin, data leaks, and tech forums.
- **Persona Profiler**: Local, rule-based extraction of Job Titles, Tech Stacks, and Interests from bios.
- **Multi-Target Workspaces**: Group related scans into projects and map overlaps between targets.
- **Interactive Visualization**: High-tech relationship graphs in HTML reports (via Vis.js).
- **Persistent History**: SQLite backend to store investigation results and metadata.
- **Polished CLI**: Beautiful terminal output with ASCII branding using Rich and Typer.
- **Ethics-First**: Strictly operates on publicly accessible data (no auth bypassing).

## 🛠️ Architecture

HeartBleed follows **Clean Architecture** principles:

- **`heartbleed/core`**: Business logic, data models, and the search orchestrator.
- **`heartbleed/collectors`**: Platform-specific plugins.
- **`heartbleed/analyzers`**: Correlation, Dorking, and Persona Profiling.
- **`heartbleed/reporters`**: Terminal and Interactive HTML formatters.
- **`heartbleed/database`**: SQLite persistence layer.

## 📦 Installation

### Prerequisites
- Python 3.11+
- Pip

### Quick Setup (Linux & Termux)
```bash
git clone https://github.com/Alpha07-Intel/HeartBleed.git
cd HeartBleed
chmod +x install.sh
./install.sh
```

## 📖 Usage

### Basic Scan
```bash
# Scan by username
python3 -m heartbleed.main scan johndoe

# Scan with Username Mutation enabled
python3 -m heartbleed.main scan johndoe --mutate
```

### 🕸️ Multi-Target Workspaces
```bash
# 1. Create a workspace
python3 -m heartbleed.main workspace create "Suspect Group A"

# 2. Add targets to the workspace
python3 -m heartbleed.main scan alias_1 --workspace 1
python3 -m heartbleed.main scan alias_2 --workspace 1

# 3. View the consolidated Relationship Map
python3 -m heartbleed.main workspace report 1
```

### Manage History
```bash
# List investigations
python3 -m heartbleed.main list

# Clear all data
python3 -m heartbleed.main clear
```

## 🛡️ Security & Ethics
HeartBleed is an OSINT tool. It must never be used for unauthorized access. All information collected originates from publicly accessible sources.

## 🗺️ Roadmap
- [x] Support for Reddit, X, and Instagram.
- [x] Graph-based visualization of correlations.
- [x] Multi-target workspace mapping.
- [x] Username mutation engine.
- [x] Local bio persona profiling.
- [ ] Email-to-Account discovery.
- [ ] Domain-specific intelligence modules.
- [ ] Export to PDF report.
