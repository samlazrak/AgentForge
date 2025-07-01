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