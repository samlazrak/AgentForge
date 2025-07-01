# 🚀 Getting Started with Agent Creator

This guide will help you set up and start using Agent Creator for AI-powered research and web scraping.

## 📋 Prerequisites

### System Requirements
- **Python 3.8 or higher**
- **macOS** (recommended for MLX optimization) or **Linux**
- **4GB+ RAM** (8GB+ recommended for large research tasks)
- **Internet connection** (for web search and scraping)

### Optional Requirements
- **Chrome/Chromium browser** (for Selenium web scraping)
- **ChromeDriver** (automatically managed by Selenium)

## 🛠️ Installation

### Method 1: Standard Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Agent-Creator
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv agent_creator_env
   source agent_creator_env/bin/activate  # On Windows: agent_creator_env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Development Installation

For contributors or advanced users:

```bash
pip install -e .
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock pytest-cov  # For testing
```

## 🏃‍♂️ Quick Start

### 1. Launch the Streamlit Interface

The easiest way to get started is through the web interface:

```bash
streamlit run app.py
```

This will open your browser to `http://localhost:8501` with the Agent Creator interface.

### 2. Initialize Agents

In the web interface:
1. Click **"🚀 Initialize Agents"** in the sidebar
2. Wait for the success message
3. You'll see both agents show as "Online" in the status panel

### 3. Your First Research Task

1. Navigate to the **"🔬 Research Agent"** tab
2. Enter a research query, for example:
   ```
   Recent developments in quantum computing applications
   ```
3. Click **"🚀 Start Research"**
4. Watch as the agent searches, analyzes, and generates reports

### 4. Your First Web Scraping Task

1. Navigate to the **"🕷️ Webscraper Agent"** tab
2. Enter a URL to scrape, for example:
   ```
   https://news.ycombinator.com
   ```
3. Click **"🕷️ Scrape URL"**
4. Review the extracted content, links, and metadata

## 🐍 Python API Usage

### Basic Research Example

```python
from agent_creator import ResearchAgent
from agent_creator.core.base_agent import AgentConfig

# Create and configure research agent
config = AgentConfig(
    name="MyResearchAgent",
    description="AI-powered research assistant",
    capabilities=["web_search", "content_analysis", "pdf_generation"]
)

research_agent = ResearchAgent(config)
research_agent.start()

# Perform research
result = research_agent.research_topic(
    query="Impact of artificial intelligence on healthcare",
    max_results=10,
    generate_pdf=True,
    generate_notebook=True
)

# Access results
print(f"Research Summary: {result['research_result'].summary}")
print(f"Sources Found: {len(result['research_result'].sources)}")
print(f"Generated Files: {result['files_generated']}")

# Stop the agent
research_agent.stop()
```

### Basic Web Scraping Example

```python
from agent_creator import WebscraperAgent
from agent_creator.agents.webscraper_agent import ScrapingConfig

# Configure scraping settings
scraping_config = ScrapingConfig(
    timeout=30,
    delay_between_requests=1.0,
    extract_links=True,
    extract_images=True
)

webscraper_agent = WebscraperAgent(scraping_config=scraping_config)
webscraper_agent.start()

# Scrape a single URL
result = webscraper_agent.scrape_url("https://example.com")

if result.success:
    print(f"Page Title: {result.title}")
    print(f"Content Length: {len(result.text)} characters")
    print(f"Links Found: {len(result.links)}")
    print(f"Images Found: {len(result.images)}")
else:
    print(f"Scraping failed: {result.error}")

# Scrape multiple URLs
urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]

results = webscraper_agent.scrape_multiple_urls(urls)
successful = sum(1 for r in results if r.success)
print(f"Successfully scraped {successful}/{len(urls)} URLs")

webscraper_agent.stop()
```

### Integrated Research with Web Scraping

```python
from agent_creator import ResearchAgent, WebscraperAgent

# Initialize both agents
research_agent = ResearchAgent()
webscraper_agent = WebscraperAgent()

# Connect them for enhanced functionality
research_agent.set_webscraper_agent(webscraper_agent)

# Start both agents
research_agent.start()
webscraper_agent.start()

# Perform enhanced research (will use webscraper for deeper content)
result = research_agent.research_topic(
    query="Machine learning trends in 2024",
    max_results=8,
    generate_pdf=True
)

# The research agent will automatically use the webscraper
# to extract full content from relevant sources

print(f"Enhanced research completed with {len(result['research_result'].sources)} sources")
```

## 🧠 Deep Researcher Agent

The **Deep Researcher Agent** is a specialized agent designed for advanced research workflows that involve extracting links from PDF documents and performing deep, multi-level web content scraping and analysis. It is ideal for scenarios where you want to start from a research paper or report (PDF), extract all referenced or embedded links, and then recursively analyze the content behind those links.

### Key Capabilities

- **PDF Link Extraction**: Automatically extracts hyperlinks from PDF files, including both annotated links and URLs found in the text. Each link includes context, page number, and optional bounding box information.
- **Content Scraping**: Scrapes the content of extracted links, optionally including images and metadata. Can use a connected `WebscraperAgent` for robust scraping.
- **Content Filtering**: Cleans and filters scraped content to remove noise, limit length, and focus on relevant information.
- **Deep Analysis**: Performs multi-level (recursive) scraping, following links found in the initially scraped pages, up to a configurable depth and breadth.
- **Link Validation**: Validates URLs for correctness and relevance, using heuristics and domain filtering.
- **Multi-level Scraping**: Supports recursive scraping with configurable depth, link limits per level, and domain restrictions.
- **Network Analysis**: Builds a network graph of parent and child links discovered during the scraping process, allowing for analysis of the link structure and content relationships.
- **Summary Generation**: Uses an LLM to generate a comprehensive summary of the research findings, including key themes, insights, and a quality assessment of the extracted content.
- **Convenience Methods**: Provides high-level methods for extracting links, scraping content, and performing the full deep research workflow with a single call.

### Example Usage

```python
from agent_creator import DeepResearcherAgent

agent = DeepResearcherAgent()
result = agent.deep_research(
    pdf_path="path/to/your.pdf",
    max_links=15,
    filter_domains=["arxiv.org", "nature.com"],
    include_images=True,
    max_depth=2,
    use_multi_level=True
)

print(result.summary)
print(f"Total links found: {result.total_links_found}")
print(f"Successful scrapes: {result.successful_scrapes}")
print(f"Max depth reached: {result.max_depth_reached}")
```

### Typical Workflow

1. **Extract Links**: Parse a PDF to extract all hyperlinks and referenced URLs.
2. **Filter Links**: Optionally filter links by allowed or blocked domains.
3. **Scrape Content**: Visit each link and extract the main content, images, and metadata.
4. **Recursive Scraping**: For each scraped page, extract further links and repeat the process up to the specified depth.
5. **Analyze Network**: Build a network graph of all discovered links and their relationships.
6. **Summarize Findings**: Generate a summary of the research, highlighting key insights and statistics.

### Configuration Options

- `max_depth`: Maximum recursion depth for multi-level scraping.
- `max_links_per_level`: Maximum number of links to follow per level.
- `max_total_links`: Global cap on the number of links to scrape.
- `delay_between_requests`: Delay between HTTP requests to avoid rate limiting.
- `allowed_domains` / `blocked_domains`: Restrict scraping to certain domains.
- `relevance_threshold`: Heuristic threshold for determining if a link is relevant.

### When to Use

- When you need to analyze all references in a PDF and their web content.
- For building a networked map of research sources and their interconnections.
- For deep, automated literature or web reviews starting from a single document.

## 🎯 Jupyter Notebook Demo

Explore the interactive demo:

```bash
jupyter notebook demo_notebook.ipynb
```

This notebook contains:
- Step-by-step agent initialization
- Research examples
- Web scraping demonstrations
- Result visualization
- Best practices

## ⚙️ Configuration Options

### Research Agent Configuration

```python
from agent_creator.core.base_agent import AgentConfig
from agent_creator.utils.llm_interface import LLMConfig

# LLM configuration
llm_config = LLMConfig(
    model_name="microsoft/DialoGPT-medium",  # or any HuggingFace model
    max_tokens=512,
    temperature=0.7,
    top_p=0.9
)

# Agent configuration
agent_config = AgentConfig(
    name="CustomResearchAgent",
    description="Specialized research agent",
    capabilities=["web_search", "content_analysis", "citation_generation"],
    llm_config=llm_config,
    max_retries=3,
    timeout=30
)
```

### Webscraper Configuration

```python
from agent_creator.agents.webscraper_agent import ScrapingConfig

scraping_config = ScrapingConfig(
    timeout=30,                    # Request timeout in seconds
    max_retries=3,                 # Max retry attempts
    delay_between_requests=1.0,    # Delay between requests
    use_selenium=False,            # Use Selenium for dynamic content
    headless=True,                 # Headless browser mode
    follow_redirects=True,         # Follow HTTP redirects
    extract_links=True,            # Extract page links
    extract_images=True,           # Extract image URLs
    max_content_length=1000000     # Max content size (1MB)
)
```

## 🔧 Troubleshooting

### Common Issues

#### 1. MLX Not Available
**Symptom**: Warning about MLX not being available
**Solution**: MLX is optimized for Apple Silicon. On other platforms, the system will use fallback mode.

#### 2. ChromeDriver Issues
**Symptom**: Selenium WebDriver errors
**Solution**: 
```bash
# Install/update ChromeDriver
pip install --upgrade selenium
```

#### 3. Permission Errors on File Generation
**Symptom**: Cannot write PDF or notebook files
**Solution**: Ensure write permissions in the current directory

#### 4. Rate Limiting from Search APIs
**Symptom**: Search requests failing or returning fewer results
**Solution**: Increase `delay_between_requests` in scraping configuration

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Checking Agent Status

```python
# Check if agents are running
print(f"Research Agent Running: {research_agent.is_running}")
print(f"Webscraper Agent Running: {webscraper_agent.is_running}")

# Get agent information
print(research_agent.get_agent_info())
print(webscraper_agent.get_agent_info())

# List active tasks
print(research_agent.list_tasks())
```

## 🎓 Next Steps

1. **Explore the Examples**: Check out `docs/EXAMPLES.md` for more advanced usage patterns
2. **Read the Architecture**: Understand the system design in `docs/ARCHITECTURE.md`
3. **API Reference**: Dive deep into the API with `docs/API_REFERENCE.md`
4. **Contribute**: Help improve the project by contributing code or documentation

## 💡 Tips for Success

1. **Start Small**: Begin with simple queries and single URLs
2. **Monitor Resources**: Large research tasks can be memory-intensive
3. **Use Appropriate Delays**: Respect websites' rate limits
4. **Fallback Gracefully**: The system handles missing dependencies well
5. **Experiment**: Try different configuration options to optimize for your use case

---

**Happy researching and scraping! 🎉**