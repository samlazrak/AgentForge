#!/usr/bin/env python3
"""
Basic usage example for the Deep Research System package.

This example demonstrates how to use the deep-researcher package to perform
web research and generate reports.
"""

from deep_researcher import DeepResearcher, ResearchResult
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)


def main():
    """Demonstrate basic usage of the Deep Research System."""
    
    # Initialize the researcher
    researcher = DeepResearcher()
    
    # Define a research query
    query = "Python web scraping best practices 2024"
    
    print(f"🔍 Starting research for: {query}")
    print("="*60)
    
    # Perform research only (without PDF generation)
    print("📊 Performing research...")
    result = researcher.research(
        query=query,
        max_initial_results=10,  # Limit for demo purposes
        max_level2_per_page=5
    )
    
    # Display results
    print(f"\n✅ Research completed!")
    print(f"Search results found: {len(result.initial_results)}")
    print(f"Pages crawled: {result.total_pages_crawled}")
    print(f"Links discovered: {result.total_links_found}")
    print(f"Research time: {result.research_time:.1f} seconds")
    
    # Show summary
    if result.summary:
        print(f"\n📋 Summary:")
        print(result.summary[:500] + "..." if len(result.summary) > 500 else result.summary)
    
    # Show key findings
    if result.key_findings:
        print(f"\n💡 Key Findings:")
        for i, finding in enumerate(result.key_findings[:3], 1):
            print(f"   {i}. {finding[:150]}...")
    
    # Show top sources
    relevant_sources = [c for c in result.level_1_content + result.level_2_content 
                       if c.success and c.relevance_score > 0.1]
    
    if relevant_sources:
        print(f"\n🔗 Top Sources:")
        for i, source in enumerate(sorted(relevant_sources, 
                                        key=lambda x: x.relevance_score, 
                                        reverse=True)[:3], 1):
            print(f"   {i}. {source.title or 'Untitled'} (Score: {source.relevance_score:.2f})")
            print(f"      {source.url}")
    
    print(f"\n🎉 Research complete! Found {len(relevant_sources)} relevant sources.")


def advanced_example():
    """Demonstrate advanced usage with PDF generation."""
    
    researcher = DeepResearcher()
    query = "Machine learning deployment strategies"
    
    print(f"\n🔍 Advanced example: {query}")
    print("="*60)
    
    # Perform research and generate PDF
    result, pdf_path = researcher.research_and_generate_pdf(
        query=query,
        output_dir="./research_reports"
    )
    
    print(f"\n✅ Research and PDF generation completed!")
    if pdf_path:
        print(f"📁 PDF saved to: {pdf_path}")
    else:
        print("⚠️  PDF generation failed")


if __name__ == "__main__":
    # Run basic example
    main()
    
    # Uncomment to run advanced example
    # advanced_example()