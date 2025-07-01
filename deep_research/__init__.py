"""
Deep Research - Advanced Web Crawling and Research Tool

A comprehensive research automation tool that performs deep web research using
DuckDuckGo search and recursive web crawling with intelligent content analysis.

Key Features:
- DuckDuckGo search integration
- Recursive web crawling
- Content relevance analysis
- PDF report generation
- Command-line interface
- Rich terminal output
- Programmatic API

Basic Usage:
    from deep_research import DeepResearcher
    
    researcher = DeepResearcher()
    result = researcher.research("your research query")
    print(f"Found {result.total_pages_crawled} pages")

CLI Usage:
    deep-research "your research query" --pdf --json
    dr "your research query" --output-dir ./reports

For more information, see the README.md file or visit:
https://github.com/yourusername/deep-research
"""

from .deep_researcher import (
    DeepResearcher,
    WebCrawler,
    ContentAnalyzer,
    ReportGenerator,
    PDFGenerator,
    SearchResult,
    ScrapedContent,
    ResearchResult,
)

# Version information
__version__ = "1.0.0"
__author__ = "Deep Research Team"
__email__ = "research@example.com"
__license__ = "MIT"

# Public API
__all__ = [
    # Main classes
    "DeepResearcher",
    "WebCrawler", 
    "ContentAnalyzer",
    "ReportGenerator",
    "PDFGenerator",
    
    # Data structures
    "SearchResult",
    "ScrapedContent", 
    "ResearchResult",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# Convenience functions for quick usage
def research(query: str, max_results: int = 20, max_level2: int = 10) -> "ResearchResult":
    """
    Convenience function to perform research with default settings.
    
    Args:
        query: Research question or topic
        max_results: Maximum number of initial search results
        max_level2: Maximum level 2 links per page
        
    Returns:
        ResearchResult containing all findings
        
    Example:
        >>> import deep_research
        >>> result = deep_research.research("machine learning trends")
        >>> print(f"Found {len(result.key_findings)} key findings")
    """
    researcher = DeepResearcher()
    return researcher.research(query, max_results, max_level2)


def quick_research(query: str, output_dir: str = "research_output") -> tuple["ResearchResult", str]:
    """
    Convenience function to perform research and generate PDF report.
    
    Args:
        query: Research question or topic
        output_dir: Directory to save PDF report
        
    Returns:
        Tuple of (ResearchResult, pdf_path)
        
    Example:
        >>> import deep_research
        >>> result, pdf_path = deep_research.quick_research("AI ethics")
        >>> print(f"Report saved to: {pdf_path}")
    """
    researcher = DeepResearcher()
    return researcher.research_and_generate_pdf(query, output_dir)


# Module-level configuration
import logging

# Set up basic logging configuration
logging.basicConfig(
    level=logging.WARNING,  # Default to WARNING level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger for this package
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def set_log_level(level: str):
    """
    Set the logging level for the deep_research package.
    
    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        
    Example:
        >>> import deep_research
        >>> deep_research.set_log_level("DEBUG")
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    logger.setLevel(numeric_level)
    logging.getLogger('deep_researcher').setLevel(numeric_level)


# Validate dependencies on import
def _check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import bs4
    except ImportError:
        missing_deps.append("beautifulsoup4")
    
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        missing_deps.append("duckduckgo-search")
    
    try:
        import reportlab
    except ImportError:
        missing_deps.append("reportlab")
    
    if missing_deps:
        logger.warning(
            f"Missing optional dependencies: {', '.join(missing_deps)}. "
            f"Some features may not work. Install with: pip install {' '.join(missing_deps)}"
        )

# Check dependencies when module is imported
_check_dependencies()