#!/usr/bin/env python3
"""
Test script for the Deep Research system
"""

import os
import sys
from datetime import datetime

# Import our deep researcher
try:
    from deep_researcher import DeepResearcher
    print("✅ Deep researcher imported successfully")
except ImportError as e:
    print(f"❌ Error importing deep researcher: {e}")
    print("Make sure to install required dependencies:")
    print("pip install requests beautifulsoup4 duckduckgo-search reportlab")
    sys.exit(1)

def test_basic_functionality():
    """Test basic deep research functionality"""
    print("\n🔍 Testing Deep Research System")
    print("=" * 50)
    
    # Create researcher
    researcher = DeepResearcher()
    
    # Test query (shorter for testing)
    test_query = "machine learning PhD programs"
    print(f"Query: {test_query}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Perform research with limited scope for testing
        result = researcher.research(
            query=test_query,
            max_initial_results=5,  # Smaller for testing
            max_level2_per_page=3   # Smaller for testing
        )
        
        # Display results
        print(f"\n📊 Research Results:")
        print(f"   Initial search results: {len(result.initial_results)}")
        print(f"   Level 1 pages crawled: {len(result.level_1_content)}")
        print(f"   Level 2 pages crawled: {len(result.level_2_content)}")
        print(f"   Total pages crawled: {result.total_pages_crawled}")
        print(f"   Total links found: {result.total_links_found}")
        print(f"   Research time: {result.research_time:.2f} seconds")
        
        # Show relevant content count
        relevant_l1 = [c for c in result.level_1_content if c.success and c.relevance_score > 0.1]
        relevant_l2 = [c for c in result.level_2_content if c.success and c.relevance_score > 0.1]
        
        print(f"   Relevant Level 1 sources: {len(relevant_l1)}")
        print(f"   Relevant Level 2 sources: {len(relevant_l2)}")
        
        # Show top findings
        if result.key_findings:
            print(f"\n💡 Top Key Findings:")
            for i, finding in enumerate(result.key_findings[:3], 1):
                print(f"   {i}. {finding[:100]}...")
        
        # Show summary preview
        if result.summary:
            print(f"\n📋 Summary Preview:")
            summary_lines = result.summary.split('\n')[:5]
            for line in summary_lines:
                if line.strip():
                    print(f"   {line}")
        
        print(f"\n✅ Research test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Research test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_generation():
    """Test PDF generation functionality"""
    print("\n📄 Testing PDF Generation")
    print("=" * 30)
    
    try:
        researcher = DeepResearcher()
        
        # Simple test query
        test_query = "python programming tutorials"
        print(f"Generating PDF for: {test_query}")
        
        # Research and generate PDF
        result, pdf_path = researcher.research_and_generate_pdf(
            query=test_query,
            output_dir="test_output"
        )
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF generated successfully!")
            print(f"   File: {pdf_path}")
            print(f"   Size: {file_size:,} bytes")
            return True
        else:
            print(f"❌ PDF generation failed - file not created")
            return False
            
    except Exception as e:
        print(f"❌ PDF generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Deep Research System Test Suite")
    print("=" * 60)
    
    # Check dependencies
    print("\n📦 Checking Dependencies:")
    
    dependencies = [
        ("requests", "Web requests"),
        ("bs4", "HTML parsing"),
        ("duckduckgo_search", "Search engine"),
        ("reportlab", "PDF generation")
    ]
    
    all_deps_ok = True
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {module:<20} - {description}")
        except ImportError:
            print(f"   ❌ {module:<20} - {description} (MISSING)")
            all_deps_ok = False
    
    if not all_deps_ok:
        print("\n❌ Some dependencies are missing. Install with:")
        print("   pip install requests beautifulsoup4 duckduckgo-search reportlab")
        return False
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_basic_functionality():
        tests_passed += 1
    
    if test_pdf_generation():
        tests_passed += 1
    
    # Final results
    print(f"\n🏁 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! The Deep Research system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)