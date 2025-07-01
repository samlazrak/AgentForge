"""
Tests for the advanced PDF processor and URL validator
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
import asyncio

from agent_creator.core.pdf_processor import (
    HyperlinkExtractor, DOIExtractor, URLTextExtractor, CitationExtractor,
    AdvancedPDFProcessor, URLValidator
)
from agent_creator.core.research_models import ExtractedReference, URLValidationResult

class TestReferenceExtractors:
    """Test individual reference extractors"""
    
    def test_hyperlink_extractor_initialization(self):
        """Test HyperlinkExtractor initialization"""
        extractor = HyperlinkExtractor()
        assert extractor.name == "HyperlinkExtractor"
        assert hasattr(extractor, 'logger')
    
    def test_doi_extractor_initialization(self):
        """Test DOIExtractor initialization"""
        extractor = DOIExtractor()
        assert extractor.name == "DOIExtractor"
        assert len(extractor.doi_patterns) > 0
    
    def test_url_text_extractor_initialization(self):
        """Test URLTextExtractor initialization"""
        extractor = URLTextExtractor()
        assert extractor.name == "URLTextExtractor"
        assert len(extractor.url_patterns) > 0
    
    def test_citation_extractor_initialization(self):
        """Test CitationExtractor initialization"""
        extractor = CitationExtractor()
        assert extractor.name == "CitationExtractor"
        assert len(extractor.citation_patterns) > 0
    
    @patch('agent_creator.core.pdf_processor.PDFPLUMBER_AVAILABLE', False)
    def test_extractors_without_pdfplumber(self):
        """Test extractors when pdfplumber is not available"""
        extractors = [
            HyperlinkExtractor(),
            DOIExtractor(),
            URLTextExtractor(),
            CitationExtractor()
        ]
        
        for extractor in extractors:
            result = extractor.extract("fake_path.pdf")
            assert result == []
    
    def test_doi_extractor_clean_doi(self):
        """Test DOI cleaning functionality"""
        extractor = DOIExtractor()
        
        test_cases = [
            ("10.1234/example.doi.,", "10.1234/example.doi"),
            ("  10.5678/test.doi  ", "10.5678/test.doi"),
            ("10.9999/sample.doi;", "10.9999/sample.doi"),
        ]
        
        for input_doi, expected in test_cases:
            result = extractor._clean_doi(input_doi)
            assert result == expected
    
    def test_doi_extractor_validation(self):
        """Test DOI validation"""
        extractor = DOIExtractor()
        
        valid_dois = [
            "10.1234/example.doi",
            "10.5678/test.doi.2020.123",
            "10.9999/complex-doi_with.chars"
        ]
        
        invalid_dois = [
            "not.a.doi",
            "10.123",  # Too short prefix
            "http://example.com",
            ""
        ]
        
        for doi in valid_dois:
            assert extractor._is_valid_doi(doi), f"Should be valid: {doi}"
        
        for doi in invalid_dois:
            assert not extractor._is_valid_doi(doi), f"Should be invalid: {doi}"
    
    def test_url_text_extractor_clean_url(self):
        """Test URL cleaning functionality"""
        extractor = URLTextExtractor()
        
        test_cases = [
            ("https://example.com.,", "https://example.com"),
            ("www.example.com", "http://www.example.com"),
            ("https://test.org;", "https://test.org"),
        ]
        
        for input_url, expected in test_cases:
            result = extractor._clean_url(input_url)
            assert result == expected
    
    def test_url_text_extractor_validation(self):
        """Test URL validation"""
        extractor = URLTextExtractor()
        
        valid_urls = [
            "https://example.com",
            "http://test.org",
            "ftp://files.example.com"
        ]
        
        invalid_urls = [
            "not-a-url",
            "example.com",  # No protocol
            "https://",  # No domain
            ""
        ]
        
        for url in valid_urls:
            assert extractor._is_valid_url_format(url), f"Should be valid: {url}"
        
        for url in invalid_urls:
            assert not extractor._is_valid_url_format(url), f"Should be invalid: {url}"

class TestAdvancedPDFProcessor:
    """Test the advanced PDF processor"""
    
    def test_initialization(self):
        """Test AdvancedPDFProcessor initialization"""
        processor = AdvancedPDFProcessor()
        assert len(processor.extractors) == 4
        assert hasattr(processor, 'logger')
    
    def test_normalize_reference_value(self):
        """Test reference value normalization"""
        processor = AdvancedPDFProcessor()
        
        # URL normalization
        url_cases = [
            ("https://example.com/", "https://example.com"),
            ("https://example.com#section", "https://example.com"),
            ("HTTPS://EXAMPLE.COM", "https://example.com"),
        ]
        
        for input_val, expected in url_cases:
            result = processor._normalize_reference_value(input_val, "url")
            assert result == expected
        
        # DOI normalization
        doi_cases = [
            ("doi:10.1234/example", "10.1234/example"),
            ("https://doi.org/10.5678/test", "10.5678/test"),
            ("http://dx.doi.org/10.9999/sample", "10.9999/sample"),
        ]
        
        for input_val, expected in doi_cases:
            result = processor._normalize_reference_value(input_val, "doi")
            assert result == expected
    
    def test_deduplicate_references(self):
        """Test reference deduplication"""
        processor = AdvancedPDFProcessor()
        
        # Create test references with duplicates
        refs = [
            ExtractedReference(
                value="https://example.com",
                reference_type="url",
                confidence=0.8
            ),
            ExtractedReference(
                value="https://example.com/",  # Duplicate (normalized)
                reference_type="url",
                confidence=0.9
            ),
            ExtractedReference(
                value="https://different.com",
                reference_type="url",
                confidence=0.7
            ),
            ExtractedReference(
                value="10.1234/example",
                reference_type="doi",
                confidence=0.85
            )
        ]
        
        unique_refs = processor._deduplicate_references(refs)
        
        # Should have 3 unique references (2 URLs deduplicated to 1)
        assert len(unique_refs) == 3
        
        # Should keep the higher confidence duplicate
        url_refs = [r for r in unique_refs if r.reference_type == "url" and "example.com" in r.value]
        assert len(url_refs) == 1
        assert url_refs[0].confidence == 0.9
    
    @patch('agent_creator.core.pdf_processor.PDFPLUMBER_AVAILABLE', False)
    def test_extract_without_pdfplumber(self):
        """Test extraction when pdfplumber is not available"""
        processor = AdvancedPDFProcessor()
        
        with patch.object(processor, 'logger') as mock_logger:
            refs = processor.extract_all_references("fake_path.pdf")
            assert refs == []
            # Should log info about each extractor finding 0 references
            assert mock_logger.info.call_count == 4

class TestURLValidator:
    """Test the URL validator"""
    
    def test_initialization_with_requests(self):
        """Test URLValidator initialization when requests is available"""
        with patch('agent_creator.core.pdf_processor.REQUESTS_AVAILABLE', True), \
             patch('requests.Session') as mock_session:
            
            validator = URLValidator()
            assert validator.session is not None
            mock_session.assert_called_once()
    
    def test_initialization_without_requests(self):
        """Test URLValidator initialization when requests is not available"""
        with patch('agent_creator.core.pdf_processor.REQUESTS_AVAILABLE', False):
            validator = URLValidator()
            assert validator.session is None
    
    def test_extract_html_metadata(self):
        """Test HTML metadata extraction"""
        validator = URLValidator()
        
        html_content = """
        <html>
        <head>
            <title>Test Article Title</title>
            <meta name="description" content="This is a test description">
            <meta name="keywords" content="test, article, research">
            <meta name="author" content="John Doe">
            <meta property="article:published_time" content="2024-01-01T12:00:00Z">
        </head>
        <body>Content</body>
        </html>
        """
        
        metadata = validator._extract_html_metadata(html_content)
        
        assert metadata['title'] == "Test Article Title"
        assert metadata['description'] == "This is a test description"
        assert metadata['keywords'] == "test, article, research"
        assert metadata['author'] == "John Doe"
        assert metadata['published_date'] == "2024-01-01T12:00:00Z"
    
    @pytest.mark.asyncio
    async def test_validate_url_without_requests(self):
        """Test URL validation when requests is not available"""
        with patch('agent_creator.core.pdf_processor.REQUESTS_AVAILABLE', False):
            validator = URLValidator()
            
            result = await validator.validate_and_enhance_url("https://example.com")
            
            assert result.original_url == "https://example.com"
            assert not result.is_accessible
            assert result.error == "Requests library not available"
    
    @pytest.mark.asyncio
    async def test_validate_url_success(self):
        """Test successful URL validation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.headers = {
            'content-type': 'text/html',
            'last-modified': 'Wed, 01 Jan 2024 12:00:00 GMT'
        }
        mock_response.history = []
        
        with patch('agent_creator.core.pdf_processor.REQUESTS_AVAILABLE', True):
            validator = URLValidator()
            validator.session = MagicMock()
            validator.session.head.return_value = mock_response
            validator.session.get.return_value = mock_response
            
            # Mock HTML content
            mock_response.text = "<title>Test Page</title>"
            
            result = await validator.validate_and_enhance_url("https://example.com")
            
            assert result.original_url == "https://example.com"
            assert result.is_accessible
            assert result.status_code == 200
            assert result.content_type == "text/html"
            assert result.last_modified == "Wed, 01 Jan 2024 12:00:00 GMT"
    
    @pytest.mark.asyncio
    async def test_validate_url_timeout(self):
        """Test URL validation timeout"""
        with patch('agent_creator.core.pdf_processor.REQUESTS_AVAILABLE', True):
            validator = URLValidator()
            validator.session = MagicMock()
            validator.session.head.side_effect = Exception("Request timeout")
            
            result = await validator.validate_and_enhance_url("https://example.com")
            
            assert result.original_url == "https://example.com"
            assert not result.is_accessible
            assert result.error is not None and "Unexpected error" in result.error
    
    @pytest.mark.asyncio
    async def test_validate_multiple_urls(self):
        """Test validating multiple URLs concurrently"""
        urls = ["https://example1.com", "https://example2.com", "https://example3.com"]
        
        with patch('agent_creator.core.pdf_processor.REQUESTS_AVAILABLE', False):
            validator = URLValidator()
            
            results = await validator.validate_multiple_urls(urls)
            
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result.original_url == urls[i]
                assert not result.is_accessible
                assert result.error == "Requests library not available"

class TestIntegration:
    """Integration tests for PDF processing components"""
    
    def test_complete_workflow_mock(self):
        """Test complete workflow with mocked components"""
        # Test that all components work together
        processor = AdvancedPDFProcessor()
        
        # Mock each extractor to return test data
        mock_refs = [
            ExtractedReference(
                value="https://example.com",
                reference_type="url",
                confidence=0.9,
                extraction_method="test"
            ),
            ExtractedReference(
                value="10.1234/test.doi",
                reference_type="doi", 
                confidence=0.85,
                extraction_method="test"
            )
        ]
        
        with patch.object(processor.extractors[0], 'extract', return_value=[mock_refs[0]]), \
             patch.object(processor.extractors[1], 'extract', return_value=[mock_refs[1]]), \
             patch.object(processor.extractors[2], 'extract', return_value=[]), \
             patch.object(processor.extractors[3], 'extract', return_value=[]):
            
            refs = processor.extract_all_references("test.pdf")
            
            assert len(refs) == 2
            assert refs[0].confidence >= refs[1].confidence  # Should be sorted by confidence

if __name__ == "__main__":
    pytest.main([__file__]) 