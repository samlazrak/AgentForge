# Agent Creator

A toolkit for building specialized AI agents focused on research, web scraping, and data analysis. This project grew out of the need for better automated research tools and has evolved into a platform that handles the tedious parts of information gathering and analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MLX](https://img.shields.io/badge/MLX-optimized-green.svg)](https://ml-explore.github.io/mlx/)
[![Streamlit](https://img.shields.io/badge/Streamlit-web_app-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What It Does

This is essentially three different tools rolled into one:

1. **Research Agent** - Takes a question, searches the web, reads through results, and writes up a summary with proper citations
2. **Web Scraper** - Pulls content from websites (both simple and JavaScript-heavy ones) and organizes it
3. **Data Analysis Agent** - Loads your data files, runs analysis, creates visualizations, and explains what it found

There's a web interface built with Streamlit that makes everything point-and-click, plus a Python API if you want to integrate it into your own code.

## Why This Exists

I got tired of spending hours doing literature reviews and data analysis by hand. The research agent can read through dozens of sources and synthesize them faster than I can, the web scraper handles the boring work of extracting content from websites, and the data analysis agent catches patterns I might miss.

If you're working with electrophysiology data, it also handles ATF files (those weird formats from lab equipment that nothing else seems to read properly).

## Quick Start

```bash
git clone https://github.com/yourusername/agent-creator.git
cd agent-creator
pip install -r requirements.txt
streamlit run app.py
```

Open your browser to `http://localhost:8501` and you're ready to go.

## Using the Agents

### Research Agent

```python
from agent_creator import ResearchAgent

agent = ResearchAgent()
agent.start()

result = agent.research_topic(
    query="What's new in AI for drug discovery?",
    max_results=10,
    generate_pdf=True
)
```

This will search multiple sources, read through them, and give you a coherent summary with citations. You can get the results as text, PDF, or Jupyter notebook.

### Web Scraper

```python
from agent_creator import WebscraperAgent

agent = WebscraperAgent()
agent.start()

# Scrape a single page
result = agent.scrape_url("https://example.com")

# Or scrape multiple pages
urls = ["https://site1.com", "https://site2.com"]
results = agent.scrape_multiple_urls(urls)
```

It handles both simple pages and JavaScript-heavy sites (using Selenium when needed). You can extract just text, get all the links, or pull out images and other media.

### Data Analysis Agent

```python
from agent_creator import DataAnalysisAgent

agent = DataAnalysisAgent()
agent.start()

# Analyze any data file
analysis = agent.analyze_file("your_data.csv")

# Works with Excel, JSON, CSV, TSV, and ATF files
analysis = agent.analyze_file("lab_recording.atf")
```

It'll figure out what kind of data you have, create appropriate visualizations, run statistical tests, and explain what the results mean in plain English.

## Web Interface

The Streamlit interface has three tabs that mirror the three agents. Upload files by dragging and dropping, enter URLs or search queries, and everything runs in the browser. Results can be downloaded in various formats.

The interface shows progress in real-time, so you can see what's happening when the agents are working through large tasks.

## File Format Support

- **Standard formats**: CSV, Excel (.xlsx/.xls), JSON, TSV
- **ATF files**: These are common in neuroscience labs for electrophysiology recordings. Most tools can't read them properly, but this handles the metadata and multiple data columns correctly.

## Performance Notes

If you're on Apple Silicon (M1/M2/M3), the MLX optimization makes AI inference significantly faster. On other hardware, it falls back to standard methods automatically.

The web scraper includes rate limiting so you don't hammer servers, and the data analysis can handle reasonably large files without running out of memory.

## Architecture

```
Web Interface (Streamlit)
├── Research Tab
├── Web Scraping Tab
└── Data Analysis Tab

Agent Layer
├── ResearchAgent
├── WebscraperAgent
└── DataAnalysisAgent

Core Components
├── BaseAgent (shared functionality)
├── LLMInterface (AI model handling)
└── Various utilities

External Dependencies
├── MLX (Apple Silicon optimization)
├── HuggingFace Transformers
├── Selenium (for complex sites)
└── Standard data science stack
```

## Common Use Cases

**Research**: Literature reviews, competitive analysis, fact-checking
**Web Scraping**: Content migration, price monitoring, data collection
**Data Analysis**: Exploratory analysis, report generation, statistical testing

The research agent is particularly useful for academic work since it generates proper citations. The data analysis agent works well for lab data since it understands scientific file formats and creates publication-ready plots.

## Installation Details

Core requirements:
- Python 3.8+
- About 2GB of dependencies (mostly for the AI models)
- Optional: MLX for Apple Silicon optimization

Full dependency list is in `requirements.txt`. The setup script (`setup.sh`) handles some of the trickier installations if you run into issues.

## Contributing

The codebase is pretty straightforward - each agent is in its own file, with shared functionality in the core module. Tests are in the `tests/` directory and documentation is in `docs/`.

If you want to add a new agent, extend the `BaseAgent` class and follow the same pattern as the existing ones. The Streamlit interface automatically picks up new agents if you follow the naming conventions.

## Known Issues

- Selenium can be finicky on some systems (check the docs for troubleshooting)
- Very large data files (>1GB) might run into memory limits
- Some websites actively block scraping (this is expected behavior)

## Documentation

- `docs/GETTING_STARTED.md` - More detailed setup instructions
- `docs/API_REFERENCE.md` - Complete function documentation
- `docs/EXAMPLES.md` - More code examples and use cases
- `docs/ARCHITECTURE.md` - How everything fits together

## License

MIT License - use it however you want, just include the license file.

---

This started as a personal project to automate my own research workflow. If it's useful to you, great! If you find bugs or have ideas for improvements, pull requests are welcome.