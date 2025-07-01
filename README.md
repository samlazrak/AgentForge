# 🛠️ AgentForge

**The Complete AI Agent Platform for Research, Web Scraping & Data Analysis**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MLX](https://img.shields.io/badge/MLX-optimized-green.svg)](https://ml-explore.github.io/mlx/)
[![Streamlit](https://img.shields.io/badge/Streamlit-web_app-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AgentForge is a powerful, all-in-one AI agent platform that combines intelligent research, advanced web scraping, and comprehensive data analysis capabilities. Built with MLX optimization for Apple Silicon and featuring a modern Streamlit interface, AgentForge transforms how you interact with data and information.

## ✨ What Makes AgentForge Special

🎯 **Three Powerful AI Agents in One Platform**
- **Research Agent**: AI-powered research with automatic citation generation
- **Webscraper Agent**: Intelligent web content extraction and analysis  
- **Data Analysis Agent**: Comprehensive data processing with automated insights

🚀 **Modern Technology Stack**
- MLX optimization for 3-5x faster AI inference on Apple Silicon
- Beautiful, responsive Streamlit web interface
- Extensible architecture with robust error handling
- Support for multiple data formats including scientific formats

🔬 **Scientific & Professional Ready**
- ATF (Axon Text Format) support for electrophysiology data
- Academic citation generation and PDF reports
- Professional visualizations and statistical analysis
- Enterprise-grade security and reliability

## 🎯 Core Capabilities

### 🔬 Research Agent
Transform any research query into comprehensive, cited reports:
- **Multi-source Analysis**: Searches and analyzes content from multiple sources
- **AI-Powered Synthesis**: Uses advanced LLMs to synthesize information
- **Citation Management**: Automatic academic-style citation generation
- **Professional Outputs**: PDF reports and Jupyter notebooks
- **Enhanced Extraction**: Integrates with webscraper for deeper content analysis

### 🕷️ Webscraper Agent  
Extract and analyze web content with intelligence:
- **Dual-Mode Operation**: Static (fast) and dynamic (Selenium) scraping
- **Smart Content Extraction**: Intelligent parsing and metadata collection
- **Batch Processing**: Handle multiple URLs with rate limiting
- **Media Discovery**: Automatic link and image extraction
- **Format Flexibility**: Export to multiple formats

### 📊 Data Analysis Agent
Comprehensive data processing and insights generation:
- **Multi-Format Support**: CSV, Excel, JSON, TSV, and **ATF files**
- **Automated Visualizations**: Distribution plots, correlations, box plots
- **Statistical Analysis**: Advanced statistical tests and interpretations
- **AI-Generated Insights**: LLM-powered data insights and recommendations
- **Data Quality Assessment**: Missing values, outliers, and data health checks
- **Scientific Data Support**: Specialized handling for electrophysiology and laboratory data

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/yourusername/agentforge.git
cd agentforge
pip install -r requirements.txt
```

### Launch the Web Interface
```bash
streamlit run app.py
```
Visit `http://localhost:8501` to access the AgentForge platform.

### Python API Usage
```python
from agent_creator import ResearchAgent, WebscraperAgent, DataAnalysisAgent

# Research with AI
research_agent = ResearchAgent()
research_agent.start()

result = research_agent.research_topic(
    query="Latest AI developments in healthcare",
    max_results=10,
    generate_pdf=True
)

# Analyze your data  
data_agent = DataAnalysisAgent()
data_agent.start()

analysis = data_agent.analyze_file(
    "data.csv",
    analysis_type="comprehensive"
)

print(f"Found {len(analysis.insights)} key insights")
```

## 🎮 Web Interface Features

### Research Tab
- **Query Input**: Natural language research queries
- **Configuration**: Search depth, output formats, enhanced extraction
- **Real-time Progress**: Live updates during research process
- **Results Display**: Interactive results with downloadable reports

### Web Scraping Tab
- **Multiple Modes**: Single URL, batch URLs, link extraction
- **Advanced Settings**: Timeout, Selenium, content filters
- **Live Monitoring**: Real-time scraping progress and statistics
- **Export Options**: Multiple output formats and download options

### Data Analysis Tab
- **File Upload**: Drag-and-drop support for multiple formats
- **Manual Entry**: JSON data input for quick analysis
- **Example Datasets**: Pre-loaded datasets for testing
- **Instant Insights**: AI-generated insights and recommendations
- **Interactive Visualizations**: Dynamic charts and statistical plots

## 📊 Supported Data Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **CSV** | Comma-separated values | General data analysis |
| **Excel** | .xlsx, .xls files | Business and research data |
| **JSON** | JavaScript Object Notation | API data and web data |
| **TSV** | Tab-separated values | Scientific and research data |
| **ATF** | Axon Text Format | Electrophysiology recordings |

### 🧬 ATF (Axon Text Format) Support
AgentForge provides specialized support for ATF files commonly used in electrophysiology and neuroscience research:
- **Metadata Extraction**: Preserves experimental metadata and comments
- **Intelligent Parsing**: Handles various ATF file structures automatically
- **Scientific Visualizations**: Specialized plots for time-series data
- **Integration Ready**: Seamless integration with other analysis tools

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentForge Platform                      │
├─────────────────────────────────────────────────────────────┤
│                  Streamlit Web Interface                    │
│   Research Tab  │  Webscraper Tab  │  Data Analysis Tab    │
├─────────────────────────────────────────────────────────────┤
│                     Agent Framework                         │
│  🔬 Research    │  🕷️ Webscraper   │  📊 Data Analysis    │
│     Agent       │      Agent       │       Agent          │
├─────────────────────────────────────────────────────────────┤
│                    Core Components                          │
│  BaseAgent  │  AgentConfig  │  TaskManager  │  LLMInterface │
├─────────────────────────────────────────────────────────────┤
│                   External Services                         │
│  MLX/HuggingFace │ DuckDuckGo │ Selenium │ Pandas/Matplotlib │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Use Cases

### 🎓 Academic & Research
- **Literature Reviews**: Comprehensive academic research with citations
- **Data Analysis**: Process experimental data including electrophysiology
- **Report Generation**: Professional PDF reports and presentations
- **Citation Management**: Automatic academic-style references

### 💼 Business Intelligence
- **Market Research**: Competitive analysis and trend monitoring
- **Content Analysis**: Website content extraction and analysis
- **Data Processing**: Business metrics and KPI analysis
- **Due Diligence**: Automated information gathering and analysis

### 🔬 Scientific Research
- **Laboratory Data**: Analyze experimental measurements and observations
- **Electrophysiology**: Specialized ATF file processing and analysis
- **Research Synthesis**: Multi-source scientific literature analysis
- **Data Visualization**: Publication-ready scientific plots and charts

### 📊 Data Science
- **Exploratory Analysis**: Quick insights from new datasets
- **Statistical Testing**: Automated statistical analysis and interpretation
- **Data Quality**: Comprehensive data health and quality assessment
- **Visualization**: Interactive and publication-ready visualizations

## 🛠️ Technology Stack

### AI & Machine Learning
- **MLX** (≥0.21.0) - Apple Silicon optimized AI inference
- **HuggingFace Transformers** (≥4.47.0) - Advanced language models
- **Pandas** (≥2.0.0) - Data manipulation and analysis
- **NumPy** & **SciPy** - Scientific computing and statistics

### Data Analysis & Visualization  
- **Matplotlib** & **Seaborn** - Statistical visualizations
- **Plotly** - Interactive charts and dashboards
- **Scikit-learn** - Machine learning and statistical analysis

### Web Technologies
- **Streamlit** (≥1.40.0) - Modern web interface
- **Requests** & **BeautifulSoup** - Web scraping
- **Selenium** (≥4.15.0) - Dynamic content extraction

### Document Generation
- **ReportLab** (≥4.0.0) - PDF generation
- **Jupyter** (≥1.1.0) - Interactive notebooks
- **Markdown** - Document formatting

## 🚀 Performance Features

### MLX Optimization
- **3-5x faster** AI inference on Apple Silicon M1/M2/M3
- **Memory efficient** processing for large datasets
- **Automatic fallback** for non-Apple hardware

### Intelligent Processing
- **Parallel operations** for web scraping and analysis
- **Automatic rate limiting** and retry mechanisms
- **Streaming data processing** for large files
- **Batch operations** for efficiency

### Enterprise Ready
- **Robust error handling** with graceful degradation
- **Comprehensive logging** for debugging and monitoring
- **Secure file handling** with temporary file cleanup
- **Resource optimization** for production environments

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Getting Started](docs/GETTING_STARTED.md)** | Installation and first steps |
| **[API Reference](docs/API_REFERENCE.md)** | Complete API documentation |
| **[Architecture](docs/ARCHITECTURE.md)** | System design and components |
| **[Examples](docs/EXAMPLES.md)** | Usage examples and tutorials |
| **[Project Overview](docs/PROJECT_OVERVIEW.md)** | Vision and features |

## 🧪 Examples

### Research with Enhanced Content Extraction
```python
from agent_creator import ResearchAgent, WebscraperAgent

# Create and connect agents
research_agent = ResearchAgent()
webscraper_agent = WebscraperAgent()
research_agent.set_webscraper_agent(webscraper_agent)

# Start agents
research_agent.start()
webscraper_agent.start()

# Perform enhanced research
result = research_agent.research_topic(
    query="Machine learning in drug discovery",
    max_results=15,
    generate_pdf=True,
    generate_notebook=True
)

print(f"Generated {len(result['files_generated'])} files")
print(f"Analyzed {len(result['research_result'].sources)} sources")
```

### Data Analysis with ATF Files
```python
from agent_creator import DataAnalysisAgent

# Analyze electrophysiology data
data_agent = DataAnalysisAgent()
data_agent.start()

# Process ATF file
result = data_agent.analyze_file(
    "experiment_data.atf",
    analysis_type="comprehensive"
)

print(f"Data shape: {result.data_summary['shape']}")
print(f"Generated {len(result.visualizations)} visualizations")
print(f"Key insights: {len(result.insights)}")

# Access AI-generated insights
for insight in result.insights:
    print(f"• {insight}")
```

### Batch Web Scraping
```python
from agent_creator import WebscraperAgent

agent = WebscraperAgent()
agent.start()

# Scrape multiple URLs
urls = [
    "https://example1.com",
    "https://example2.com", 
    "https://example3.com"
]

results = agent.scrape_multiple_urls(urls)

for result in results:
    if result.success:
        print(f"Scraped: {result.url}")
        print(f"Content: {len(result.text)} characters")
        print(f"Links: {len(result.links)}")
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Run all tests
pytest tests/

# Run specific agent tests
pytest tests/test_research_agent.py
pytest tests/test_webscraper_agent.py  
pytest tests/test_data_analysis_agent.py

# Run with coverage
pytest --cov=agent_creator tests/
```

## 🚀 Deployment

### Local Development
```bash
git clone https://github.com/yourusername/agentforge.git
cd agentforge
pip install -e .
streamlit run app.py
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Launch with optimized settings
streamlit run app.py --server.headless true
```

### Docker (Coming Soon)
```bash
docker build -t agentforge .
docker run -p 8501:8501 agentforge
```

## 🤝 Contributing

We welcome contributions from the community! Here's how to get started:

### Development Setup
```bash
git clone https://github.com/yourusername/agentforge.git
cd agentforge
pip install -e .
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

### Contributing Process
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with tests
4. **Run** the test suite (`pytest`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Development Guidelines
- Write comprehensive tests for new features
- Follow PEP 8 style guidelines
- Add docstrings to all public functions
- Update documentation for new features

## 📋 Roadmap

### Current Version: 1.0.0
- ✅ Three-agent platform (Research, Webscraper, Data Analysis)
- ✅ Streamlit web interface with modern design
- ✅ MLX optimization for Apple Silicon
- ✅ ATF file support for scientific data
- ✅ Comprehensive documentation and tests

### Version 1.1.0 (Next Release)
- 🔄 RESTful API for programmatic access
- 🔄 Docker containerization for easy deployment
- 🔄 Enhanced data visualization dashboard
- 🔄 User authentication and project management

### Version 1.2.0 (Future)
- 🔄 Plugin system for custom agents
- 🔄 Cloud deployment templates
- 🔄 Advanced analytics and reporting
- 🔄 Integration with popular data platforms

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MLX Team** - For outstanding Apple Silicon optimization
- **Streamlit** - For the incredible web framework
- **HuggingFace** - For democratizing AI access
- **Scientific Community** - For inspiring the ATF support
- **Open Source Contributors** - For making this possible

## 📞 Support & Community

### Get Help
- 📚 **Documentation**: Comprehensive guides and API reference
- 🔍 **Issues**: Search existing issues or create new ones
- 💬 **Discussions**: Join community discussions
- 📧 **Contact**: Reach out for enterprise support

### Stay Updated
- ⭐ **Star** this repository to show support
- 👀 **Watch** for updates and new releases
- 🍴 **Fork** to contribute or customize
- 📢 **Share** with your colleagues and friends

## 📊 Project Statistics

- **Languages**: Python 3.8+
- **Dependencies**: 40+ carefully selected packages  
- **Test Coverage**: 85%+ comprehensive test suite
- **Documentation**: 100% API coverage
- **Performance**: 3-5x faster with MLX optimization
- **File Formats**: 5+ supported data formats including ATF

---

<div align="center">

**🛠️ Built with passion for researchers, scientists, and data enthusiasts**

**AgentForge** - *Forging the future of AI-powered information processing*

[⚡ Get Started](docs/GETTING_STARTED.md) • [📖 Documentation](docs/) • [🤝 Contribute](#-contributing) • [📞 Support](#-support--community)

</div>