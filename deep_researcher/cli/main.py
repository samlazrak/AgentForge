#!/usr/bin/env python3
"""Command line interface for the Deep Research System."""

import argparse
import logging
import os
import sys
from typing import Optional

try:
    from ..core.researcher import DeepResearcher
except ImportError:
    # Fallback for when running as standalone script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.researcher import DeepResearcher


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Deep Research System - Comprehensive web research with recursive crawling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "How to transition from software engineering to PhD?"
  %(prog)s "Machine learning trends 2024" --max-results 30 --output ./reports
  %(prog)s "Python web scraping libraries" --log-level DEBUG
        """
    )
    
    parser.add_argument(
        "query",
        help="Research query to investigate"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of initial search results to process (default: 20)"
    )
    
    parser.add_argument(
        "--max-links-per-page",
        type=int,
        default=10,
        help="Maximum number of links to follow from each page (default: 10)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        default="research_output",
        help="Output directory for research reports (default: research_output)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF generation and only perform research"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Deep Research System 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting deep research for query: {args.query}")
        logger.info(f"Configuration: max_results={args.max_results}, max_links_per_page={args.max_links_per_page}")
        
        # Initialize researcher
        researcher = DeepResearcher()
        
        if args.no_pdf:
            # Just perform research without PDF generation
            result = researcher.research(
                query=args.query,
                max_initial_results=args.max_results,
                max_level2_per_page=args.max_links_per_page
            )
            
            print(f"\n🎉 Research completed!")
            print(f"📊 Results Summary:")
            print(f"   Search results found: {len(result.initial_results)}")
            print(f"   Pages crawled: {result.total_pages_crawled}")
            print(f"   Links discovered: {result.total_links_found}")
            print(f"   Research time: {result.research_time:.1f} seconds")
            print(f"   Key findings: {len(result.key_findings)}")
            
            if result.summary:
                print(f"\n📋 Summary:")
                print(result.summary)
                
            if result.key_findings:
                print(f"\n💡 Key Findings:")
                for i, finding in enumerate(result.key_findings[:5], 1):
                    print(f"   {i}. {finding}")
        else:
            # Perform research and generate PDF
            result, pdf_path = researcher.research_and_generate_pdf(
                query=args.query,
                output_dir=args.output
            )
            
            print(f"\n🎉 Research completed and PDF generated!")
            print(f"📊 Results Summary:")
            print(f"   Search results found: {len(result.initial_results)}")
            print(f"   Pages crawled: {result.total_pages_crawled}")
            print(f"   Links discovered: {result.total_links_found}")
            print(f"   Research time: {result.research_time:.1f} seconds")
            print(f"   Key findings: {len(result.key_findings)}")
            
            if pdf_path:
                print(f"📁 PDF Report: {pdf_path}")
            else:
                print("⚠️  PDF generation failed")
    
    except KeyboardInterrupt:
        logger.info("Research interrupted by user")
        print("\n❌ Research interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Research failed: {e}")
        print(f"\n❌ Research failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()