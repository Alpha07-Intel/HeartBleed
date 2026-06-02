# HeartBleed OSINT Toolkit

HeartBleed is a modular, high-performance command-line OSINT toolkit designed to discover and correlate publicly available social media and online accounts belonging to a target individual.

## 🚀 Features

- **Concurrent Collection**: Parallelized platform scanning for maximum speed.
- **Identity Correlation**: Advanced scoring engine to determine profile ownership probability.
- **Plugin Architecture**: Easily add new platform collectors as standalone modules.
- **Persistent History**: SQLite backend to store investigation results and metadata.
- **Polished CLI**: Beautiful terminal output using Rich and Typer.
- **Reporting**: Generate JSON and interactive HTML reports.
- **Ethics-First**: Strictly operates on publicly accessible data (no auth bypassing).

## 🛠️ Architecture

HeartBleed follows **Clean Architecture** principles:

- **`heartbleed/core`**: Business logic, data models, and the search orchestrator.
- **`heartbleed/collectors`**: Platform-specific plugins (GitHub, GitLab, etc.).
- **`heartbleed/analyzers`**: Correlation and scoring engine.
- **`heartbleed/reporters`**: Terminal, HTML, and JSON output formatters.
- **`heartbleed/database`**: SQLite persistence layer.

## 📦 Installation

### Prerequisites
- Python 3.11+
- Pip

### Setup
```bash
git clone https://github.com/yourusername/HeartBleed.git
cd HeartBleed
pip install -e .
```

Alternatively, install dependencies directly:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Basic Scan
```bash
# Scan by username
python -m heartbleed.main scan johndoe

# Scan and generate all reports
python -m heartbleed.main scan johndoe --json --html
```

### List Investigations
```bash
python -m heartbleed.main list
```

### View/Export Previous Report
```bash
# Display ID 1 in terminal
python -m heartbleed.main report 1

# Export ID 1 to HTML
python -m heartbleed.main report 1 --format html
```

## 🛡️ Security & Ethics
HeartBleed is an OSINT tool. It must never be used for unauthorized access, credential harvesting, or bypassing authentication. All information collected is from publicly available sources.

## 🗺️ Roadmap
- [ ] Avatar similarity engine (image hashing).
- [ ] Support for Reddit, X, and Instagram.
- [ ] Search engine integration (Google/Bing).
- [ ] Graph-based visualization of correlations.
