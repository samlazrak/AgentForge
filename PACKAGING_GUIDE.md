# Deep Research System - Packaging Guide

This guide explains how the Deep Research System has been packaged for distribution and how to install it in other Python applications.

## Package Structure

The application has been reorganized into a proper Python package structure:

```
deep_researcher/                 # Main package directory
├── __init__.py                 # Package exports and metadata
├── core/                       # Core functionality modules
│   ├── __init__.py
│   ├── researcher.py          # Main DeepResearcher orchestrator
│   ├── crawler.py             # Web crawling and search
│   ├── analyzer.py            # Content relevance analysis
│   └── report.py              # Report and PDF generation
├── models/                     # Data models and structures
│   ├── __init__.py
│   └── data_models.py         # SearchResult, ScrapedContent, ResearchResult
├── web/                        # Web interface
│   ├── __init__.py
│   └── app.py                 # Streamlit application
└── cli/                        # Command line interface
    ├── __init__.py
    └── main.py                # CLI entry point

# Package configuration files
setup.py                        # Traditional setup configuration
pyproject.toml                  # Modern packaging configuration
requirements-core.txt           # Core dependencies only
MANIFEST.in                     # Files to include in distribution
LICENSE                         # MIT license
README-package.md              # Package documentation

# Examples and documentation
examples/
└── basic_usage.py             # Usage examples
```

## Installation Options

### 1. Install from Source (Current Method)

From the current directory:

```bash
# Install in development mode (editable)
pip install -e .

# Or install normally
pip install .
```

### 2. Install with Optional Dependencies

```bash
# Core package only
pip install .

# With web interface support
pip install .[web]

# With all optional features
pip install .[full]

# With development tools
pip install .[dev]
```

### 3. Build Distribution Packages

To create distributable packages:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# dist/deep_researcher-1.0.0-py3-none-any.whl
# dist/deep_researcher-1.0.0.tar.gz
```

### 4. Install from Distribution

```bash
# Install from wheel
pip install dist/deep_researcher-1.0.0-py3-none-any.whl

# Install from source distribution
pip install dist/deep_researcher-1.0.0.tar.gz
```

## Usage in Other Applications

Once installed, you can import and use the package in your Python applications:

### Basic Import and Usage

```python
# Import the main class
from deep_researcher import DeepResearcher

# Initialize and use
researcher = DeepResearcher()
result = researcher.research("Your research query")

# Access results
print(f"Found {result.total_pages_crawled} pages")
print(f"Research took {result.research_time:.1f} seconds")
```

### Import Individual Components

```python
# Import specific components
from deep_researcher import WebCrawler, ContentAnalyzer, PDFGenerator
from deep_researcher.models import SearchResult, ScrapedContent, ResearchResult

# Use components individually
crawler = WebCrawler()
analyzer = ContentAnalyzer()
pdf_gen = PDFGenerator()
```

### Web Interface

```python
# Run the web interface programmatically
import subprocess
subprocess.run(["streamlit", "run", "-m", "deep_researcher.web.app"])
```

### Command Line Usage

After installation, the CLI command is available globally:

```bash
deep-research "Your research query"
deep-research "Python web scraping" --max-results 30 --output ./reports
```

## Dependencies

### Core Dependencies (Required)
- `duckduckgo-search>=3.9.0` - Web search functionality
- `requests>=2.31.0` - HTTP requests
- `beautifulsoup4>=4.12.0` - HTML parsing
- `reportlab>=4.0.0` - PDF generation
- `urllib3>=2.0.0` - Network handling

### Optional Dependencies
- `streamlit>=1.28.0` - Web interface (install with `[web]`)
- `selenium>=4.15.0` - Advanced crawling (install with `[full]`)
- `pytest>=7.4.0` - Testing (install with `[dev]`)

## Configuration

The package includes several configuration options:

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Research Parameters
```python
researcher = DeepResearcher()
result = researcher.research(
    query="Your query",
    max_initial_results=20,     # Number of initial search results
    max_level2_per_page=10      # Links to follow per page
)
```

## Integration Examples

### Simple Research Integration

```python
from deep_researcher import DeepResearcher

def research_topic(topic):
    """Simple function to research a topic and return findings."""
    researcher = DeepResearcher()
    result = researcher.research(topic)
    
    return {
        'summary': result.summary,
        'key_findings': result.key_findings,
        'sources': len(result.level_1_content + result.level_2_content),
        'time_taken': result.research_time
    }

# Usage
findings = research_topic("Python machine learning libraries")
print(findings['summary'])
```

### Automated Research Pipeline

```python
from deep_researcher import DeepResearcher
import json

def research_pipeline(queries, output_dir="research_output"):
    """Research multiple topics and generate reports."""
    researcher = DeepResearcher()
    results = {}
    
    for query in queries:
        print(f"Researching: {query}")
        result, pdf_path = researcher.research_and_generate_pdf(
            query=query,
            output_dir=output_dir
        )
        
        results[query] = {
            'pdf_path': pdf_path,
            'pages_crawled': result.total_pages_crawled,
            'research_time': result.research_time,
            'key_findings_count': len(result.key_findings)
        }
    
    return results

# Usage
topics = [
    "Python web scraping best practices",
    "Machine learning deployment strategies",
    "API design principles 2024"
]

results = research_pipeline(topics)
print(json.dumps(results, indent=2))
```

## Publishing to PyPI (Optional)

To publish the package to PyPI for public distribution:

```bash
# Build the package
python -m build

# Upload to PyPI (requires account and token)
python -m twine upload dist/*
```

Then others can install with:
```bash
pip install deep-researcher
```

## Troubleshooting

### Import Errors
If you encounter import errors, ensure the package is properly installed:
```bash
pip list | grep deep-researcher
```

### Missing Dependencies
Install missing optional dependencies:
```bash
pip install deep-researcher[full]
```

### Permission Errors
If you get permission errors during installation:
```bash
pip install --user .
```

## Development Setup

For development work on the package:

```bash
# Clone/navigate to the package directory
cd deep-researcher

# Install in development mode with all dependencies
pip install -e .[dev,web,full]

# Run tests
pytest

# Check package structure
python -c "import deep_researcher; print(deep_researcher.__file__)"
```

## Summary

The Deep Research System is now packaged as a proper Python package that can be:

1. **Installed via pip** in any Python environment
2. **Imported and used** in other Python applications
3. **Used via command line** with the `deep-research` command
4. **Run as a web app** with Streamlit
5. **Extended and customized** by importing individual components

The modular design allows you to use the entire system or just specific components as needed in your applications.