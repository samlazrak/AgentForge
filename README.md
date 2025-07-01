# AgentForge

**An AI agent platform for research, web scraping, and data analysis**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MLX](https://img.shields.io/badge/MLX-optimized-green.svg)](https://ml-explore.github.io/mlx/)
[![Streamlit](https://img.shields.io/badge/Streamlit-web_app-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

I built AgentForge because I got tired of switching between different tools for research, web scraping, and data analysis. It's a platform that brings together three AI agents that actually talk to each other and share data - something I wish existed when I was doing my research.

## What's Inside

**Three agents that work together:**
- **Research Agent**: Searches the web, synthesizes information, and creates proper citations
- **Web Scraper**: Extracts content from websites (both simple and complex ones)  
- **Data Analyst**: Handles your data files and generates insights

**Built for real work:**
- Works great on Apple Silicon (thanks to MLX optimization)
- Clean web interface that doesn't make you want to pull your hair out
- Handles scientific data formats like ATF files (because apparently that's important to some of you)
- Actually generates readable reports and citations

## Why I Made This

I spent way too much time cobbling together different tools for research projects. Need to research a topic? Open five browser tabs. Want to scrape some websites? Fire up a separate script. Got data to analyze? Time for yet another tool. 

AgentForge puts it all in one place. The research agent can automatically use the web scraper to get deeper content, and you can feed that data straight into the analysis agent. It's the workflow I always wanted.

## What Each Agent Does

### Research Agent
Give it a topic and it'll research it properly:
- Searches multiple sources and actually reads them
- Synthesizes the information (no copy-paste nonsense)
- Creates proper citations because your professor/boss cares about that
- Outputs PDF reports and Jupyter notebooks
- Can work with the web scraper for more thorough content extraction

### Web Scraper  
Handles websites like a human would:
- Fast scraping for simple sites
- Selenium-based scraping for the fancy JavaScript-heavy ones
- Processes multiple URLs without breaking
- Finds all the links and images on a page
- Exports data however you want it

### Data Analyst
Takes your messy data and makes sense of it:
- Handles all the usual formats (CSV, Excel, JSON, TSV)
- **Also handles ATF files** (for all you electrophysiology folks)
- Creates charts that actually look good
- Runs statistical tests and explains what they mean
- Generates insights using AI (and they're usually pretty good)
- Tells you when your data is garbage

## Getting Started

**Install it:**
```bash
git clone https://github.com/yourusername/agentforge.git
cd agentforge
pip install -r requirements.txt
```

**Run it:**
```bash
streamlit run app.py
```
Then go to `http://localhost:8501` and start playing around.

**Use it from Python:**
```python
from agent_creator import ResearchAgent, DataAnalysisAgent

# Research something
research_agent = ResearchAgent()
research_agent.start()

result = research_agent.research_topic(
    query="What's new in AI healthcare applications",
    max_results=10,
    generate_pdf=True
)

# Analyze some data  
data_agent = DataAnalysisAgent()
data_agent.start()

analysis = data_agent.analyze_file("my_data.csv", analysis_type="comprehensive")
print(f"Found {len(analysis.insights)} interesting things in your data")
```

## The Web Interface

I tried to make this actually usable:

**Research Tab**: Type in what you want to research, configure how deep you want to go, watch it work in real-time

**Web Scraping Tab**: Paste URLs, choose between fast or thorough scraping, download results in whatever format makes sense

**Data Analysis Tab**: Drop in your data files, get instant insights, play with interactive charts

## Data Formats I Support

| Format | Why You'd Use It |
|--------|------------------|
| **CSV** | Because everything ends up as CSV eventually |
| **Excel** | For when your boss insists on spreadsheets |
| **JSON** | API data and modern web stuff |
| **TSV** | Scientific data that's too good for commas |
| **ATF** | Electrophysiology recordings (yes, really) |

### ATF Files (For the Scientists)
If you work with electrophysiology data, you know ATF files are a pain. AgentForge handles them properly:
- Keeps all your experimental metadata intact
- Figures out the file structure automatically
- Makes time-series plots that don't look terrible
- Plays nice with your other analysis tools

## How It's Built

```
┌─────────────────────────────────────────────────────────────┐
│                        AgentForge                           │
├─────────────────────────────────────────────────────────────┤
│                  Streamlit Web Interface                    │
│   Research Tab  │  Webscraper Tab  │  Data Analysis Tab    │
├─────────────────────────────────────────────────────────────┤
│                     The Three Agents                       │
│  🔬 Research    │  🕷️ Web Scraper   │  📊 Data Analyst    │
├─────────────────────────────────────────────────────────────┤
│                    Core Stuff                              │
│  BaseAgent  │  Config  │  Task Manager  │  LLM Interface   │
├─────────────────────────────────────────────────────────────┤
│                   The Tools                                │
│  MLX/HuggingFace │ DuckDuckGo │ Selenium │ Pandas/Matplotlib │
└─────────────────────────────────────────────────────────────┘
```

## Who This Is For

**Researchers**: Literature reviews, data analysis, citation management
**Business folks**: Market research, competitive analysis, data insights
**Scientists**: Lab data processing, especially electrophysiology 
**Data people**: Quick exploratory analysis, statistical testing, visualization

## What's Under the Hood

**AI stuff:**
- MLX for Apple Silicon (makes everything 3-5x faster if you have an M1/M2/M3)
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
git clone https://github.com/yourusername/agentforge.git
cd agentforge
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

I'd love help making this better. Here's how:

1. Fork the repo
2. Make a branch (`git checkout -b feature/cool-new-thing`)
3. Write some code (and tests, please)
4. Make sure tests pass (`pytest`)
5. Send a pull request

**Development setup:**
```bash
git clone https://github.com/yourusername/agentforge.git
cd agentforge
pip install -e .
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

Please write tests for new features and follow Python conventions. Documentation updates are always welcome too.

## What's Next

**Version 1.1.0:**
- REST API for programmatic access
- Docker container for easier deployment
- Better visualizations
- User accounts and project management

**Future plans:**
- Plugin system for custom agents
- Cloud deployment options
- More integrations with data platforms

## License

MIT License - do whatever you want with it, just don't blame me if something breaks.

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

**AgentForge** - *Because switching between tools is annoying*

[Get Started](docs/GETTING_STARTED.md) • [Documentation](docs/) • [Contribute](#contributing)