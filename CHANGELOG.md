# Changelog

All notable changes to the Deep Research project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-07

### Added
- 🎉 Initial release of Deep Research CLI
- 🔍 DuckDuckGo search integration for initial research
- 🕷️ Recursive web crawling with level 1 and level 2 link following
- 🧠 Intelligent content relevance analysis and scoring
- 📄 PDF report generation with comprehensive research findings
- 💻 Rich CLI interface with beautiful terminal output
- 📊 Progress indicators and real-time status updates
- 📦 Programmatic API for integration into other Python projects
- 🔧 Configurable crawling parameters (max results, max level 2 links)
- 📁 JSON export functionality for structured data
- 🎨 Color-coded output with tables, trees, and panels
- ⚡ Respectful web scraping with built-in delays
- 🛡️ Error handling and graceful failure recovery
- 📚 Comprehensive documentation and examples

### Features
- **CLI Commands**: `deep-research` and `dr` (short alias)
- **Output Formats**: Terminal display, PDF reports, JSON files
- **Search Engine**: DuckDuckGo integration (no API keys required)
- **Content Analysis**: Automatic relevance scoring
- **Report Generation**: Professional PDF reports with sources
- **Package Structure**: Proper Python package for easy installation
- **Dependencies**: Minimal core dependencies, optional extras

### Technical Details
- **Python Support**: 3.8+ compatibility
- **Package Management**: Modern pyproject.toml configuration
- **Code Quality**: Type hints, docstrings, and linting setup
- **Testing**: Test structure ready for expansion
- **Distribution**: Setuptools and pip compatible

### CLI Options
- `--max-results`: Control initial search result count
- `--max-level2`: Control recursive link following depth
- `--output-dir`: Specify output directory for reports
- `--pdf`: Generate PDF report
- `--json`: Save results as JSON
- `--verbose`: Enable detailed logging
- `--max-sources`: Control source display count

### API Components
- `DeepResearcher`: Main research orchestrator
- `WebCrawler`: Handles web scraping and URL management
- `ContentAnalyzer`: Performs relevance analysis
- `ReportGenerator`: Creates summaries and extracts findings
- `PDFGenerator`: Generates professional PDF reports
- Data classes: `SearchResult`, `ScrapedContent`, `ResearchResult`

### Removed
- ❌ Streamlit web interface (replaced with CLI)
- ❌ Jupyter notebook dependencies
- ❌ Heavy ML/AI dependencies (moved to optional extras)
- ❌ Selenium and Scrapy dependencies (simplified to requests + BeautifulSoup)

### Changed
- 🔄 Converted from web app to CLI-first tool
- 🔄 Streamlined dependencies for faster installation
- 🔄 Improved error handling and logging
- 🔄 Enhanced documentation and examples