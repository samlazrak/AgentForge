# Deep Research CLI

A comprehensive, production-ready deep research tool that performs advanced web research using DuckDuckGo search and recursive web crawling with a beautiful command-line interface.

## 🔍 What It Does

This system takes a research query and performs deep, multi-level web research:

1. **Initial Search**: Searches DuckDuckGo for relevant results
2. **Level 1 Crawling**: Scrapes content from initial search results  
3. **Level 2 Recursive Crawling**: Follows links from initial pages and crawls them recursively
4. **Content Analysis**: Analyzes all content for relevance to your research query
5. **Report Generation**: Creates comprehensive reports in JSON and PDF formats
6. **Rich CLI Output**: Beautiful terminal output with progress indicators and formatted results

## ✨ Features

- 🔍 **DuckDuckGo Integration**: Searches without API keys or rate limits
- 🕷️ **Recursive Web Crawling**: Follows links for deeper research
- 🧠 **Intelligent Content Analysis**: Scores content relevance automatically
- 📄 **PDF Report Generation**: Creates professional research reports
- 💻 **Rich CLI Interface**: Beautiful terminal output with colors and formatting
- 📦 **Importable Package**: Use programmatically in your own Python projects
- ⚡ **Fast & Respectful**: Built-in delays and proper web scraping etiquette

## 🚀 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/deep-research.git
cd deep-research

# Install in development mode
pip install -e .

# Or install directly
pip install .
```

### Using pip (when published)

```bash
pip install deep-research
```

## 🎯 Quick Start

### Command Line Usage

```bash
# Basic research
deep-research "How to transition from software engineering to PhD?"

# Generate PDF report
deep-research "machine learning trends 2024" --pdf

# Save results as JSON
deep-research "climate change solutions" --json

# Full example with all options
deep-research "startup funding strategies" \
    --max-results 30 \
    --max-level2 15 \
    --output-dir ./reports \
    --pdf \
    --json \
    --verbose

# Use short alias
dr "AI ethics in healthcare" --pdf
```

### Programmatic Usage

```python
# Basic usage
from deep_research import DeepResearcher

researcher = DeepResearcher()
result = researcher.research("your research query")

print(f"Found {result.total_pages_crawled} pages")
print(f"Key findings: {len(result.key_findings)}")

# Quick research with PDF
from deep_research import quick_research

result, pdf_path = quick_research("AI trends 2024")
print(f"Report saved to: {pdf_path}")

# Convenience function
import deep_research

result = deep_research.research("machine learning", max_results=10)
```

## 📖 CLI Options

```
positional arguments:
  query                 Research query to investigate

optional arguments:
  --max-results N       Maximum initial search results (default: 20)
  --max-level2 N        Maximum level 2 links per page (default: 10)
  --output-dir DIR      Output directory for reports (default: research_output)
  --pdf                 Generate PDF report
  --json                Save results as JSON file
  --max-sources N       Maximum sources to display (default: 10)
  --verbose             Enable verbose logging
  --version             Show version information
  --help                Show help message
```

## 🎨 Example Output

When you run a research query, you'll see beautiful formatted output:

```
🔍 Deep Research CLI
Advanced web crawling and research with recursive link following

🛠️ Research Configuration
┌─────────────────────┬─────────────────────────────────────┐
│ Setting             │ Value                               │
├─────────────────────┼─────────────────────────────────────┤
│ Query               │ machine learning trends             │
│ Max Initial Results │ 20                                  │
│ Max Level 2 per Page│ 10                                  │
│ Output Directory    │ research_output                     │
│ Generate PDF        │ Yes                                 │
│ Save JSON           │ No                                  │
└─────────────────────┴─────────────────────────────────────┘

🚀 Starting deep research...

🔍 Searching DuckDuckGo... ██████████ 100%
🕷️ Crawling Level 1 pages... ██████████ 100%
🔗 Extracting links... ██████████ 100%
📄 Crawling Level 2 pages... ██████████ 100%
📊 Analyzing content... ██████████ 100%

✅ Research completed!

📊 Research Summary
┌─────────────────────┬────────┐
│ Metric              │ Value  │
├─────────────────────┼────────┤
│ Query               │ ml...  │
│ Total Pages Crawled │ 45     │
│ Total Links Found   │ 234    │
│ Research Time       │ 23.4s  │
└─────────────────────┴────────┘
```

## 📁 Project Structure

```
deep-research/
├── deep_research/           # Main package
│   ├── __init__.py         # Package initialization
│   └── deep_researcher.py  # Core research functionality
├── cli.py                  # Command-line interface
├── setup.py               # Package setup (legacy)
├── pyproject.toml         # Modern package configuration
├── requirements.txt       # Dependencies
├── README.md             # This file
├── LICENSE              # MIT License
├── CHANGELOG.md        # Version history
├── MANIFEST.in         # Package manifest
└── example_usage.py    # Usage examples
```

## 🔧 Development

### Setting up for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/deep-research.git
cd deep-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all extras
pip install -e .[dev,full]

# Run tests
pytest

# Format code
black .

# Check types
mypy deep_research/
```

### Building and Distribution

```bash
# Build the package
python -m build

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Format your code (`black .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DuckDuckGo](https://duckduckgo.com/) for providing search capabilities
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [ReportLab](https://www.reportlab.com/) for PDF generation

## 📧 Support

- 🐛 [Report bugs](https://github.com/yourusername/deep-research/issues)
- 💡 [Request features](https://github.com/yourusername/deep-research/issues)
- 📖 [View documentation](https://github.com/yourusername/deep-research#readme)
- 💬 [Discussions](https://github.com/yourusername/deep-research/discussions)

---

**Deep Research CLI** - Turn any research question into comprehensive insights with just one command! 🚀