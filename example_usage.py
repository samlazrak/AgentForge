#!/usr/bin/env python3
"""
Example usage of the Deep Research package for programmatic research.

This file demonstrates various ways to use the deep_research package
in your own Python projects.
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path for local development
sys.path.insert(0, '.')

def example_basic_research():
    """Basic research example"""
    print("🔍 Example 1: Basic Research")
    print("=" * 50)
    
    from deep_research import DeepResearcher
    
    # Create researcher instance
    researcher = DeepResearcher()
    
    # Perform research
    query = "Python async programming best practices"
    print(f"Researching: {query}")
    
    result = researcher.research(query, max_initial_results=5, max_level2_per_page=3)
    
    # Display results
    print(f"\n📊 Results:")
    print(f"  - Query: {result.query}")
    print(f"  - Pages crawled: {result.total_pages_crawled}")
    print(f"  - Links found: {result.total_links_found}")
    print(f"  - Research time: {result.research_time:.1f}s")
    print(f"  - Key findings: {len(result.key_findings)}")
    
    if result.key_findings:
        print(f"\n💡 Top 3 Key Findings:")
        for i, finding in enumerate(result.key_findings[:3], 1):
            # Truncate long findings
            short_finding = finding[:150] + "..." if len(finding) > 150 else finding
            print(f"  {i}. {short_finding}")
    
    return result


def example_convenience_functions():
    """Example using convenience functions"""
    print("\n🔍 Example 2: Convenience Functions")
    print("=" * 50)
    
    # Import convenience functions
    from deep_research import research, quick_research
    
    # Quick research function
    print("Using quick research function...")
    query = "machine learning interpretability"
    result = research(query, max_results=3)
    
    print(f"📊 Quick research completed:")
    print(f"  - Pages crawled: {result.total_pages_crawled}")
    print(f"  - Research time: {result.research_time:.1f}s")
    
    # Quick research with PDF
    print("\nGenerating PDF report...")
    result, pdf_path = quick_research("AI ethics", output_dir="example_output")
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"📄 PDF saved to: {pdf_path}")
    else:
        print("📄 PDF generation failed or disabled")
    
    return result


def example_detailed_analysis():
    """Example with detailed content analysis"""
    print("\n🔍 Example 3: Detailed Content Analysis")
    print("=" * 50)
    
    from deep_research import DeepResearcher
    
    researcher = DeepResearcher()
    
    # Research a specific topic
    query = "sustainable software development practices"
    result = researcher.research(query, max_initial_results=5)
    
    # Analyze content by relevance
    all_content = result.level_1_content + result.level_2_content
    relevant_content = [c for c in all_content if c.success and c.relevance_score > 0.1]
    relevant_content.sort(key=lambda x: x.relevance_score, reverse=True)
    
    print(f"📈 Content Analysis:")
    print(f"  - Total content pieces: {len(all_content)}")
    print(f"  - Relevant content: {len(relevant_content)}")
    
    if relevant_content:
        print(f"\n🏆 Top 3 Most Relevant Sources:")
        for i, content in enumerate(relevant_content[:3], 1):
            title = content.title or "Untitled"
            if len(title) > 60:
                title = title[:57] + "..."
            print(f"  {i}. {title}")
            print(f"     Relevance: {content.relevance_score:.2f}")
            print(f"     URL: {content.url}")
            
            # Show content preview
            if content.content:
                preview = content.content[:200].replace('\n', ' ')
                if len(content.content) > 200:
                    preview += "..."
                print(f"     Preview: {preview}")
            print()
    
    return result


def example_configuration():
    """Example showing different configuration options"""
    print("\n🔍 Example 4: Configuration Options")
    print("=" * 50)
    
    from deep_research import DeepResearcher
    import logging
    
    # Enable debug logging
    logging.getLogger('deep_researcher').setLevel(logging.INFO)
    
    researcher = DeepResearcher()
    
    # Research with custom parameters
    query = "blockchain scalability solutions"
    
    print("Performing research with custom parameters...")
    result = researcher.research(
        query=query,
        max_initial_results=10,    # More initial results
        max_level2_per_page=5      # More level 2 links per page
    )
    
    print(f"📊 Custom Configuration Results:")
    print(f"  - Initial results requested: 10")
    print(f"  - Initial results found: {len(result.initial_results)}")
    print(f"  - Level 1 pages: {len(result.level_1_content)}")
    print(f"  - Level 2 pages: {len(result.level_2_content)}")
    print(f"  - Total research time: {result.research_time:.1f}s")
    
    return result


def example_error_handling():
    """Example with error handling"""
    print("\n🔍 Example 5: Error Handling")
    print("=" * 50)
    
    from deep_research import DeepResearcher
    
    researcher = DeepResearcher()
    
    try:
        # Research with empty query (should handle gracefully)
        result = researcher.research("")
        print("Empty query handled gracefully")
        
    except Exception as e:
        print(f"Error with empty query: {e}")
    
    try:
        # Research with very specific query
        result = researcher.research("very specific technical query that might not have results")
        
        if result.total_pages_crawled == 0:
            print("No results found - this is handled gracefully")
        else:
            print(f"Found some results: {result.total_pages_crawled} pages")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print("Error handling examples completed")


def main():
    """Run all examples"""
    print("🚀 Deep Research Package Examples")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run examples
        example_basic_research()
        example_convenience_functions()
        example_detailed_analysis()
        example_configuration()
        example_error_handling()
        
        print("\n✅ All examples completed successfully!")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n❌ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()