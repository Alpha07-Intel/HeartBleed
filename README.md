# HeartBleed OSINT Toolkit 🩸 v0.1

HeartBleed is a modular, high-performance command-line OSINT toolkit designed to discover and correlate publicly available social media and online accounts belonging to a target individual.

**Developed by: Alpha-07**

## 🚀 Features

- **Concurrent Collection**: Parallelized platform scanning for maximum speed.
- **Identity Correlation**: Advanced scoring engine to determine profile ownership probability.
- **Platform Support**: GitHub, GitLab, Reddit, Instagram, and X (Twitter).
- **Interactive Visualization**: Network relationship graphs in HTML reports (via Vis.js).
- **Plugin Architecture**: Easily add new platform collectors as standalone modules.
- **Persistent History**: SQLite backend to store investigation results and metadata.
- **Polished CLI**: Beautiful terminal output with ASCII branding using Rich and Typer.
- **Reporting**: Generate JSON and interactive HTML reports.
- **Ethics-First**: Strictly operates on publicly accessible data (no auth bypassing).

## 🛠️ Architecture

HeartBleed follows **Clean Architecture** principles:

- **`heartbleed/core`**: Business logic, data models, and the search orchestrator.
- **`heartbleed/collectors`**: Platform-specific plugins (plugins for individual sites).
- **`heartbleed/analyzers`**: Correlation and scoring engine.
- **`heartbleed/reporters`**: Terminal, HTML (Interactive Graph), and JSON output formatters.
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

# Scan and generate all reports (including the Interactive Graph)
python3 -m heartbleed.main scan johndoe --json --html
```

### Manage History
```bash
# List recent investigations
python3 -m heartbleed.main list

# Clear all investigation history
python3 -m heartbleed.main clear
```

### View/Export Previous Report
```bash
# Display investigation ID 1 in terminal
python3 -m heartbleed.main report 1

# Export investigation ID 1 to Interactive HTML Graph
python3 -m heartbleed.main report 1 --format html
```

## 🛡️ Security & Ethics
HeartBleed is an OSINT tool. It must never be used for unauthorized access, credential harvesting, or bypassing authentication. All information collected originates from publicly accessible sources.

## 🗺️ Roadmap
- [x] Support for Reddit, X, and Instagram.
- [x] Graph-based visualization of correlations.
- [ ] Avatar similarity engine (image hashing).
- [ ] Search engine integration (Google/Bing).
- [ ] Multi-target workspace.
