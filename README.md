# Agent Creator

A toolkit for building specialized AI agents focused on research, web scraping, and data analysis. I built this because I got tired of switching between different tools for research projects - it handles the tedious parts of information gathering and analysis so you don't have to.

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

I spent way too much time cobbling together different tools for research projects. Need to research a topic? Open five browser tabs. Want to scrape some websites? Fire up a separate script. Got data to analyze? Time for yet another tool.

Agent Creator puts it all in one place. The research agent can automatically use the web scraper to get deeper content, and you can feed that data straight into the analysis agent. It's the workflow I always wanted.

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

The Streamlit interface has three tabs that mirror the three agents:

**Research Tab**: Type in what you want to research, configure how deep you want to go, watch it work in real-time

**Web Scraping Tab**: Paste URLs, choose between fast or thorough scraping, download results in whatever format makes sense

**Data Analysis Tab**: Drop in your data files, get instant insights, play with interactive charts

The interface shows progress in real-time, so you can see what's happening when the agents are working through large tasks.

## File Format Support

**Standard formats**: CSV, Excel (.xlsx/.xls), JSON, TSV

**ATF files**: These are common in neuroscience labs for electrophysiology recordings. Most tools can't read them properly, but this handles the metadata and multiple data columns correctly. If you work with electrophysiology data, you know ATF files are a pain - Agent Creator handles them properly:
- Keeps all your experimental metadata intact
- Figures out the file structure automatically
- Makes time-series plots that don't look terrible
- Plays nice with your other analysis tools

## Performance Notes

If you're on Apple Silicon (M1/M2/M3), the MLX optimization makes AI inference 3-5x faster. On other hardware, it falls back to standard methods automatically.

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

**Research**: Literature reviews, competitive analysis, fact-checking - the research agent is particularly useful for academic work since it generates proper citations

**Web Scraping**: Content migration, price monitoring, data collection - handles both simple and complex JavaScript-heavy sites

**Data Analysis**: Exploratory analysis, report generation, statistical testing - works well for lab data since it understands scientific file formats and creates publication-ready plots

## What's Under the Hood

**AI stuff:**
- MLX for Apple Silicon (makes everything faster if you have an M1/M2/M3)
- HuggingFace transformers for the language models
- Pandas and friends for data wrangling

**Web stuff:**
- Streamlit for the interface (because it actually works)
- Requests and BeautifulSoup for simple scraping
- Selenium when websites get fancy

**Output stuff:**
- ReportLab for PDFs that don't look like they came from 1995
- Jupyter notebooks for interactive analysis
- Matplotlib/Seaborn for charts that won't embarrass you

## Examples

**Research with web scraper integration:**
```python
from agent_creator import ResearchAgent, WebscraperAgent

# Set up the agents to work together
research_agent = ResearchAgent()
webscraper_agent = WebscraperAgent()
research_agent.set_webscraper_agent(webscraper_agent)

research_agent.start()
webscraper_agent.start()

# Do some actual research
result = research_agent.research_topic(
    query="Machine learning in drug discovery",
    max_results=15,
    generate_pdf=True,
    generate_notebook=True
)

print(f"Created {len(result['files_generated'])} files")
print(f"Looked at {len(result['research_result'].sources)} sources")
```

**Analyze electrophysiology data:**
```python
from agent_creator import DataAnalysisAgent

data_agent = DataAnalysisAgent()
data_agent.start()

# Process that ATF file you've been putting off
result = data_agent.analyze_file(
    "patch_clamp_experiment.atf",
    analysis_type="comprehensive"
)

print(f"Your data: {result.data_summary['shape']}")
print(f"Made {len(result.visualizations)} charts")
print("Here's what I found interesting:")
for insight in result.insights:
    print(f"• {insight}")
```

## Installation Details

Core requirements:
- Python 3.8+
- About 2GB of dependencies (mostly for the AI models)
- Optional: MLX for Apple Silicon optimization

Full dependency list is in `requirements.txt`. The setup script (`setup.sh`) handles some of the trickier installations if you run into issues.

## Testing

```bash
# Run all tests
pytest tests/

# Test specific agents
pytest tests/test_research_agent.py
pytest tests/test_webscraper_agent.py  
pytest tests/test_data_analysis_agent.py

# Check coverage
pytest --cov=agent_creator tests/
```

## Running in Production

**Local setup:**
```bash
git clone https://github.com/yourusername/agent-creator.git
cd agent-creator
pip install -e .
streamlit run app.py
```

**For real deployment:**
```bash
pip install -r requirements.txt
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
streamlit run app.py --server.headless true
```

## Contributing

The codebase is pretty straightforward - each agent is in its own file, with shared functionality in the core module. Tests are in the `tests/` directory and documentation is in `docs/`.

If you want to add a new agent, extend the `BaseAgent` class and follow the same pattern as the existing ones. The Streamlit interface automatically picks up new agents if you follow the naming conventions.

I'd love help making this better. Here's how:

1. Fork the repo
2. Make a branch (`git checkout -b feature/cool-new-thing`)
3. Write some code (and tests, please)
4. Make sure tests pass (`pytest`)
5. Send a pull request

**Development setup:**
```bash
git clone https://github.com/yourusername/agent-creator.git
cd agent-creator
pip install -e .
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

Please write tests for new features and follow Python conventions. Documentation updates are always welcome too.

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

## Thanks

- The MLX team for making Apple Silicon actually useful for AI
- Streamlit for building a web framework that doesn't make me cry
- HuggingFace for democratizing access to good language models
- All the scientists who convinced me ATF support was worth the headache
- Everyone who's contributed code, bug reports, or just used this thing

## Questions?

- Check the [documentation](docs/) first
- Look through existing [issues](../../issues) 
- Start a [discussion](../../discussions) if you want to chat
- Email me if you need enterprise support

If this helps with your work, give it a star ⭐ and maybe tell a colleague about it.

---

This started as a personal project to automate my own research workflow. If it's useful to you, great! If you find bugs or have ideas for improvements, pull requests are welcome.

**Agent Creator** - *Because switching between tools is annoying*

[Get Started](docs/GETTING_STARTED.md) • [Documentation](docs/) • [Contribute](#contributing)