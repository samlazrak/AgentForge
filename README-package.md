# Deep Research System 🔍

A comprehensive Python package for performing deep web research with recursive crawling capabilities. This tool goes beyond simple web searches by following links, analyzing content relevance, and generating detailed research reports.

## Features

- **Intelligent Search**: Uses DuckDuckGo search API for initial results
- **Recursive Crawling**: Follows links from initial pages to discover deeper content
- **Relevance Analysis**: Automatically scores content based on research query relevance
- **PDF Report Generation**: Creates comprehensive PDF reports with findings and sources
- **Streamlit Web Interface**: Beautiful web UI for interactive research
- **Command Line Interface**: CLI tool for automated research workflows
- **Modular Design**: Import and use individual components in your own applications

## Installation

### Core Package
```bash
pip install deep-researcher
```

### With Web Interface
```bash
pip install deep-researcher[web]
```

### Full Installation (All Features)
```bash
pip install deep-researcher[full]
```

### Development Installation
```bash
git clone https://github.com/your-username/deep-researcher.git
cd deep-researcher
pip install -e .[dev]
```

## Quick Start

### Python API

```python
from deep_researcher import DeepResearcher

# Initialize the researcher
researcher = DeepResearcher()

# Perform research
result = researcher.research("Python machine learning libraries 2024")

# Access results
print(f"Found {len(result.initial_results)} search results")
print(f"Crawled {result.total_pages_crawled} pages")
print(f"Relevance score of top result: {result.level_1_content[0].relevance_score}")

# Generate PDF report
result, pdf_path = researcher.research_and_generate_pdf(
    "Your research query here",
    output_dir="./reports"
)
```

### Command Line Interface

```bash
# Basic research
deep-research "Python web scraping best practices"

# Advanced options
deep-research "Machine learning trends 2024" \
  --max-results 30 \
  --output ./reports \
  --log-level INFO

# Research without PDF generation
deep-research "AI ethics considerations" --no-pdf
```

### Web Interface

```bash
# Install with web dependencies
pip install deep-researcher[web]

# Run the Streamlit app
streamlit run -m deep_researcher.web.app
```

## API Reference

### Core Classes

#### `DeepResearcher`
Main orchestrator class for research operations.

```python
researcher = DeepResearcher()

# Basic research
result = researcher.research(
    query="Your research query",
    max_initial_results=20,      # Number of initial search results
    max_level2_per_page=10       # Links to follow per page
)

# Research with PDF generation
result, pdf_path = researcher.research_and_generate_pdf(
    query="Your research query",
    output_dir="output_directory"
)
```

#### `ResearchResult`
Contains all research findings and metadata.

```python
# Access research data
result.query                    # Original query
result.initial_results         # Initial search results
result.level_1_content         # Content from initial pages  
result.level_2_content         # Content from recursive crawl
result.summary                 # Generated summary
result.key_findings           # Extracted key findings
result.total_pages_crawled    # Number of pages processed
result.research_time          # Time taken in seconds
```

#### Individual Components

```python
from deep_researcher import WebCrawler, ContentAnalyzer, PDFGenerator

# Use components individually
crawler = WebCrawler()
search_results = crawler.search_duckduckgo("your query")
content = crawler.scrape_url("https://example.com")

analyzer = ContentAnalyzer()
relevance = analyzer.calculate_relevance(content.content, "your query")

pdf_gen = PDFGenerator()
pdf_gen.generate_pdf(result, "report.pdf")
```

## Configuration

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Custom Settings
The package respects web scraping best practices:
- Automatic delays between requests
- Respectful crawling with proper headers  
- Error handling and retry logic
- Content filtering for relevance

## Examples

See the [`examples/`](examples/) directory for complete examples:

- [`basic_usage.py`](examples/basic_usage.py) - Basic research workflow
- [`advanced_features.py`](examples/advanced_features.py) - Advanced usage patterns
- [`integration_example.py`](examples/integration_example.py) - Integration with other tools

## Use Cases

- **Academic Research**: Gather information on research topics
- **Market Research**: Analyze trends and competitor information  
- **Content Creation**: Research topics for articles and reports
- **Due Diligence**: Investigate companies, technologies, or topics
- **Competitive Analysis**: Understand market landscapes
- **Information Gathering**: Compile comprehensive information on any topic

## Supported Data Sources

- **DuckDuckGo Search**: Primary search engine for initial results
- **Web Pages**: Any publicly accessible HTML content
- **Following Links**: Recursive discovery of related content
- **Multiple Formats**: HTML, text content extraction
- **PDF Output**: Generated reports in PDF format

## Requirements

- Python 3.8+
- Internet connection for web searches and crawling
- Required packages (automatically installed):
  - `duckduckgo-search>=3.9.0`
  - `requests>=2.31.0`
  - `beautifulsoup4>=4.12.0`
  - `reportlab>=4.0.0`

## Development

### Setup Development Environment
```bash
git clone https://github.com/your-username/deep-researcher.git
cd deep-researcher
pip install -e .[dev]
```

### Run Tests
```bash
pytest
```

### Package Structure
```
deep_researcher/
├── __init__.py              # Main package exports
├── core/                    # Core functionality
│   ├── researcher.py        # Main DeepResearcher class
│   ├── crawler.py          # Web crawling logic
│   ├── analyzer.py         # Content analysis
│   └── report.py           # Report generation
├── models/                  # Data models
│   └── data_models.py      # Dataclasses for results
├── web/                     # Web interface
│   └── app.py              # Streamlit application
└── cli/                     # Command line interface
    └── main.py             # CLI entry point
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Core research functionality
- PDF report generation
- Web and CLI interfaces
- Modular package design

## Support

- **Issues**: [GitHub Issues](https://github.com/your-username/deep-researcher/issues)
- **Documentation**: [README](https://github.com/your-username/deep-researcher/blob/main/README.md)
- **Source Code**: [GitHub Repository](https://github.com/your-username/deep-researcher)

## Acknowledgments

- DuckDuckGo for providing search API
- Beautiful Soup for HTML parsing
- ReportLab for PDF generation
- Streamlit for web interface framework