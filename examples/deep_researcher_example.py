#!/usr/bin/env python3
"""
Example usage of the Deep Researcher Agent

This example demonstrates how to use the Deep Researcher Agent to:
1. Extract links from PDF documents
2. Scrape content from those links  
3. Filter and clean the scraped content
4. Generate research summaries
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent_creator.agents.deep_researcher_agent import DeepResearcherAgent
from agent_creator.agents.webscraper_agent import WebscraperAgent

def main():
    """Main example function"""
    print("🔍 Deep Researcher Agent Example")
    print("=" * 40)
    
    # Step 1: Initialize the agents
    print("\n1. Initializing agents...")
    deep_researcher = DeepResearcherAgent()
    webscraper = WebscraperAgent()
    
    # Step 2: Connect the webscraper to the deep researcher
    deep_researcher.set_webscraper_agent(webscraper)
    print("   ✓ Agents initialized and connected")
    
    # Step 3: Example - Extract links from a PDF
    print("\n2. Example: Extract links from PDF")
    try:
        # In a real scenario, you would provide the path to your research PDF
        pdf_path = "path/to/your/research_report.pdf"
        
        # For this example, we'll show how it would work with mock data
        print(f"   Extracting links from: {pdf_path}")
        
        # This will use mock links since the file doesn't exist
        links = deep_researcher.extract_links_from_pdf(pdf_path, max_links=5)
        
        print(f"   ✓ Found {len(links)} links:")
        for i, link in enumerate(links, 1):
            print(f"     {i}. {link.url}")
            print(f"        Text: {link.text}")
            if link.context:
                print(f"        Context: {link.context[:60]}...")
        
    except Exception as e:
        print(f"   Note: Using mock data since PDF not found ({e})")
        
    # Step 4: Example - Perform complete deep research
    print("\n3. Example: Complete deep research workflow")
    try:
        # This performs the full workflow: extract links + scrape content + summarize
        result = deep_researcher.deep_research(
            pdf_path="mock_research.pdf",  # Will use mock data
            max_links=3,
            filter_domains=None,  # No domain filtering
            include_images=True
        )
        
        print(f"   ✓ Research completed!")
        print(f"     - Total links found: {result.total_links_found}")
        print(f"     - Successfully scraped: {result.successful_scrapes}")
        print(f"     - Summary: {result.summary[:100]}...")
        
        # Show scraped content
        print(f"\n   Scraped content samples:")
        for i, content in enumerate(result.scraped_content[:2], 1):
            if content.success:
                print(f"     {i}. {content.title}")
                print(f"        URL: {content.url}")
                print(f"        Clean text: {content.clean_text[:80]}...")
                print(f"        Images found: {len(content.images)}")
        
    except Exception as e:
        print(f"   Error in deep research: {e}")
    
    # Step 5: Example - Content filtering
    print("\n4. Example: Content filtering")
    
    # Sample dirty content with navigation and advertising elements
    dirty_content = """
    Main article content starts here. This is valuable information about the topic.
    
    Newsletter signup for daily updates!
    Cookie policy - we use cookies for better experience.
    
    The article continues with more useful details and insights.
    
    Footer navigation links
    Contact us for more information
    Copyright 2024 All rights reserved
    """
    
    clean_content = deep_researcher._filter_and_clean_content(dirty_content)
    
    print("   Original content:")
    print(f"     {dirty_content.strip()}")
    print("\n   Filtered content:")
    print(f"     {clean_content}")
    
    # Step 6: Example - URL extraction from text
    print("\n5. Example: URL extraction from text")
    
    text_with_urls = """
    For more information, visit https://example.com/research or 
    check the documentation at www.docs.example.org.
    You can also find the code repository at https://github.com/user/project.
    """
    
    extracted_urls = deep_researcher._extract_urls_from_text(text_with_urls)
    
    print("   Text content:")
    print(f"     {text_with_urls.strip()}")
    print(f"\n   Extracted URLs:")
    for url in extracted_urls:
        print(f"     - {url}")
    
    print("\n" + "=" * 40)
    print("✅ Example completed successfully!")
    print("\nNext steps:")
    print("- Replace 'path/to/your/research_report.pdf' with actual PDF path")
    print("- Ensure PDF contains hyperlinks or URLs in text")
    print("- Install web scraping dependencies for full functionality")
    print("- Consider adding domain filtering for focused research")

if __name__ == "__main__":
    main()