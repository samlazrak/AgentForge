# Deep Research System

A focused, production-ready deep research tool that performs comprehensive web research using DuckDuckGo search and recursive web crawling.

## 🔍 What It Does

This system takes a research query and performs deep, multi-level web research:

1. **Initial Search**: Searches DuckDuckGo for relevant results
2. **Level 1 Crawling**: Scrapes content from initial search results
3. **Level 2 Recursive Crawling**: Follows links from initial pages and crawls them recursively
4. **Content Analysis**: Analyzes all content for relevance to your research query
5. **Report Generation**: Creates comprehensive reports in both web interface and PDF format

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### Run the Web Application
```bash
# Start the Streamlit web interface
streamlit run app.py
```

The web interface will be available at `http://localhost:8501`

### Run Tests
```bash
# Test the core functionality
python3 test_research.py
```

## 📋 Features

- **DuckDuckGo Integration**: Searches the web without API keys
- **Multi-Level Crawling**: Goes beyond surface-level results
- **Content Relevance Scoring**: Analyzes how relevant each page is to your query
- **PDF Report Generation**: Creates professional research reports
- **Real-time Progress Tracking**: See the research progress as it happens
- **Error Handling**: Robust handling of failed requests and timeouts
- **Research History**: Keep track of past research queries

## 🖥️ Web Interface

The Streamlit interface provides:
- Clean, modern design with intuitive controls
- Real-time progress bars and status updates
- Comprehensive results display with metrics
- Research summary and key findings
- Expandable source previews with relevance scores
- PDF download functionality
- Research history sidebar

## 🔧 Core Components

- **`deep_researcher.py`** (604 lines): Core research engine with web crawling, content analysis, and report generation
- **`app.py`** (393 lines): Streamlit web interface with modern UI and real-time updates
- **`test_research.py`** (165 lines): Comprehensive testing script for verification

## 📊 Example Output

A typical research session will:
- Find 5-20 initial search results
- Crawl 10-50 pages across two levels
- Generate relevance scores for all content
- Create a comprehensive PDF report
- Complete in 30-120 seconds depending on query complexity

## 🛠️ Dependencies

Key libraries used:
- **Web Scraping**: `duckduckgo-search`, `requests`, `beautifulsoup4`
- **PDF Generation**: `reportlab`
- **Web Interface**: `streamlit`
- **Content Analysis**: Built-in relevance scoring system

## 📄 License

MIT License - Feel free to use this system for your research needs.

---

*This system was built to provide deep, comprehensive web research capabilities with a focus on simplicity, reliability, and production readiness.*