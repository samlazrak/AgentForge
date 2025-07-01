# 🤖 Agent Creator

**AI-Powered Research & Web Scraping Platform with MLX Integration**

Agent Creator is a comprehensive framework that combines the power of artificial intelligence with advanced web scraping capabilities to create intelligent research assistants. Built with MLX integration for optimized performance on Apple Silicon and featuring a beautiful Streamlit interface.

## 🌟 Key Features

### 🔬 Research Agent
- **AI-Powered Research**: Leverage advanced language models for comprehensive topic analysis
- **Automated Citation Generation**: Proper academic citation formatting
- **Multi-Source Analysis**: Intelligent synthesis of information from multiple web sources
- **Report Generation**: Automatic PDF and Jupyter notebook creation
- **MLX Integration**: Optimized performance with Apple's MLX framework

### 🕷️ Webscraper Agent
- **Intelligent Content Extraction**: Advanced parsing of web content
- **Dynamic Content Support**: Both static (requests/BeautifulSoup) and dynamic (Selenium) scraping
- **Batch Processing**: Efficient multi-URL scraping capabilities
- **Metadata Extraction**: Comprehensive page metadata collection
- **Link and Image Extraction**: Automatic extraction of media and navigation elements

### 🤝 Agent Integration
- **Seamless Collaboration**: Research and webscraper agents work together
- **Task Management**: Built-in task tracking and status monitoring
- **Error Handling**: Robust error handling with graceful fallbacks
- **Extensible Architecture**: Easy to add new agent types

### 🎨 User Interface
- **Streamlit Web App**: Beautiful, intuitive web interface
- **Real-time Progress**: Live updates during research and scraping operations
- **Results Analytics**: Comprehensive visualization of results
- **Export Options**: Multiple format exports (PDF, Jupyter, JSON)

## 🏗️ Architecture

Agent Creator follows a modular architecture with three main components:

1. **Core Framework** (`agent_creator/core/`)
   - `BaseAgent`: Abstract base class for all agents
   - `AgentConfig`: Configuration management
   - `AgentTask`: Task representation and tracking

2. **Specialized Agents** (`agent_creator/agents/`)
   - `ResearchAgent`: AI-powered research capabilities
   - `WebscraperAgent`: Advanced web scraping functionality

3. **Utilities** (`agent_creator/utils/`)
   - `LLMInterface`: MLX-based language model integration

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Agent-Creator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

### Basic Usage

```python
from agent_creator import ResearchAgent, WebscraperAgent
from agent_creator.core.base_agent import AgentConfig

# Initialize Research Agent
research_agent = ResearchAgent()
research_agent.start()

# Perform research
result = research_agent.research_topic(
    query="Latest developments in artificial intelligence",
    max_results=10,
    generate_pdf=True
)

print(f"Summary: {result['research_result'].summary}")
```

## 📋 Requirements

### Core Dependencies
- **Python 3.8+**
- **MLX** >= 0.21.0 (Apple Silicon optimization)
- **Streamlit** >= 1.40.0 (Web interface)
- **Transformers** >= 4.47.0 (HuggingFace models)

### Research Capabilities
- **duckduckgo-search** >= 6.1.0 (Web search)
- **requests** >= 2.31.0 (HTTP requests)
- **beautifulsoup4** >= 4.12.0 (HTML parsing)

### Web Scraping
- **selenium** >= 4.15.0 (Dynamic content)
- **fake-useragent** >= 1.4.0 (User agent rotation)

### Document Generation
- **reportlab** >= 4.0.0 (PDF generation)
- **jupyter** >= 1.1.0 (Notebook generation)

See `requirements.txt` for complete dependency list.

## 📚 Documentation

- **[Getting Started](GETTING_STARTED.md)** - Installation and setup guide
- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
- **[API Reference](API_REFERENCE.md)** - Detailed API documentation
- **[Examples](EXAMPLES.md)** - Usage examples and tutorials

## 🔧 Configuration

### Research Agent Configuration
```python
from agent_creator.core.base_agent import AgentConfig

config = AgentConfig(
    name="MyResearchAgent",
    description="Custom research agent",
    capabilities=["web_search", "content_analysis"],
    max_retries=3,
    timeout=30
)
```

### Webscraper Configuration
```python
from agent_creator.agents.webscraper_agent import ScrapingConfig

scraping_config = ScrapingConfig(
    timeout=30,
    delay_between_requests=1.0,
    use_selenium=False,
    max_content_length=1000000
)
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run specific agent tests:

```bash
pytest tests/test_research_agent.py
pytest tests/test_webscraper_agent.py
```

## 📊 Examples

### Research Example
```python
# Initialize and start research agent
research_agent = ResearchAgent()
research_agent.start()

# Perform comprehensive research
result = research_agent.research_topic(
    query="Climate change impacts on biodiversity",
    max_results=15,
    generate_pdf=True,
    generate_notebook=True
)

# Access results
print(f"Sources found: {len(result['research_result'].sources)}")
print(f"Files generated: {result['files_generated']}")
```

### Web Scraping Example
```python
# Initialize webscraper agent
webscraper_agent = WebscraperAgent()
webscraper_agent.start()

# Scrape single URL
result = webscraper_agent.scrape_url("https://example.com")

if result.success:
    print(f"Title: {result.title}")
    print(f"Content length: {len(result.text)}")
    print(f"Links found: {len(result.links)}")
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:

- Code style and standards
- Testing requirements
- Documentation updates
- Feature proposals

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **MLX Team**: For the excellent MLX framework
- **Streamlit**: For the amazing web app framework
- **HuggingFace**: For the transformers library
- **Open Source Community**: For all the wonderful libraries that make this possible

## 📞 Support

For questions, issues, or feature requests:

1. Check the [documentation](docs/)
2. Search existing [issues](../../issues)
3. Create a new [issue](../../issues/new)

---

**Built with ❤️ and powered by AI**