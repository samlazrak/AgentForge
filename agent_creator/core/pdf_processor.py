"""
Advanced PDF processing for comprehensive reference extraction
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import asyncio
from dataclasses import dataclass

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available - using mock functionality")

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests not available - URL validation disabled")

from .research_models import ExtractedReference, URLValidationResult

class ReferenceExtractor:
    """Base class for reference extractors"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    def extract(self, pdf_path: str) -> List[ExtractedReference]:
        """Extract references from PDF"""
        raise NotImplementedError

class HyperlinkExtractor(ReferenceExtractor):
    """Extract hyperlinks from PDF annotations"""
    
    def __init__(self):
        super().__init__("HyperlinkExtractor")
    
    def extract(self, pdf_path: str) -> List[ExtractedReference]:
        """Extract hyperlinks from PDF annotations"""
        if not PDFPLUMBER_AVAILABLE:
            return []
        
        references = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract hyperlinks from annotations
                    if hasattr(page, 'hyperlinks') and page.hyperlinks:
                        for hyperlink in page.hyperlinks:
                            url = hyperlink.get('uri', '')
                            if url and self._is_valid_url_format(url):
                                # Extract surrounding text for context
                                bbox = hyperlink.get('bbox')
                                context = self._extract_context_around_link(page, bbox) if bbox else ""
                                
                                ref = ExtractedReference(
                                    value=url,
                                    reference_type="url",
                                    page_number=page_num + 1,
                                    context=context,
                                    confidence=0.9,  # High confidence for annotated links
                                    bbox=bbox,
                                    extraction_method="annotation_hyperlink"
                                )
                                references.append(ref)
        
        except Exception as e:
            self.logger.error(f"Error extracting hyperlinks: {e}")
        
        return references
    
    def _is_valid_url_format(self, url: str) -> bool:
        """Basic URL format validation"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False
    
    def _extract_context_around_link(self, page, bbox: Tuple[float, float, float, float]) -> str:
        """Extract text context around a link"""
        try:
            x1, y1, x2, y2 = bbox
            expanded_bbox = (
                max(0, x1 - 50),
                max(0, y1 - 20), 
                x2 + 50,
                y2 + 20
            )
            
            cropped = page.crop(expanded_bbox)
            context = cropped.extract_text() or ""
            context = ' '.join(context.split())
            return context[:200] + "..." if len(context) > 200 else context
            
        except Exception as e:
            self.logger.warning(f"Error extracting context: {e}")
            return ""

class DOIExtractor(ReferenceExtractor):
    """Extract DOI references from text"""
    
    def __init__(self):
        super().__init__("DOIExtractor")
        # DOI regex patterns
        self.doi_patterns = [
            r'(?:doi:?\s*)(10\.\d{4,}\/[^\s\]]+)',
            r'(?:https?:\/\/(?:dx\.)?doi\.org\/)(10\.\d{4,}\/[^\s\]]+)',
            r'(?:DOI:?\s*)(10\.\d{4,}\/[^\s\]]+)',
            r'\b(10\.\d{4,}\/[^\s\]<>"\'()]+)\b'
        ]
    
    def extract(self, pdf_path: str) -> List[ExtractedReference]:
        """Extract DOI references from PDF text"""
        if not PDFPLUMBER_AVAILABLE:
            return []
        
        references = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    
                    for pattern in self.doi_patterns:
                        matches = re.finditer(pattern, page_text, re.IGNORECASE)
                        
                        for match in matches:
                            doi = match.group(1) if match.lastindex else match.group(0)
                            doi = self._clean_doi(doi)
                            
                            if self._is_valid_doi(doi):
                                context = self._extract_context_from_text(page_text, match.start(), match.end())
                                
                                ref = ExtractedReference(
                                    value=doi,
                                    reference_type="doi",
                                    page_number=page_num + 1,
                                    context=context,
                                    confidence=0.85,
                                    extraction_method="regex_pattern",
                                    metadata={"pattern_used": pattern}
                                )
                                references.append(ref)
        
        except Exception as e:
            self.logger.error(f"Error extracting DOIs: {e}")
        
        return references
    
    def _clean_doi(self, doi: str) -> str:
        """Clean and normalize DOI"""
        # Remove common trailing characters
        doi = doi.rstrip('.,;!?)')
        # Remove any leading/trailing whitespace
        doi = doi.strip()
        return doi
    
    def _is_valid_doi(self, doi: str) -> bool:
        """Validate DOI format"""
        # Basic DOI validation
        pattern = r'^10\.\d{4,}\/[^\s]+$'
        return bool(re.match(pattern, doi))
    
    def _extract_context_from_text(self, text: str, start: int, end: int) -> str:
        """Extract context around DOI in text"""
        context_start = max(0, start - 100)
        context_end = min(len(text), end + 100)
        context = text[context_start:context_end]
        return ' '.join(context.split())

class URLTextExtractor(ReferenceExtractor):
    """Extract URLs from text content"""
    
    def __init__(self):
        super().__init__("URLTextExtractor")
        # URL regex patterns
        self.url_patterns = [
            r'https?://[^\s<>"\'()]+',
            r'www\.[^\s<>"\'()]+',
            r'ftp://[^\s<>"\'()]+'
        ]
    
    def extract(self, pdf_path: str) -> List[ExtractedReference]:
        """Extract URLs from PDF text content"""
        if not PDFPLUMBER_AVAILABLE:
            return []
        
        references = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    
                    for pattern in self.url_patterns:
                        matches = re.finditer(pattern, page_text, re.IGNORECASE)
                        
                        for match in matches:
                            url = match.group(0)
                            url = self._clean_url(url)
                            
                            if self._is_valid_url_format(url):
                                context = self._extract_context_from_text(page_text, match.start(), match.end())
                                
                                ref = ExtractedReference(
                                    value=url,
                                    reference_type="url",
                                    page_number=page_num + 1,
                                    context=context,
                                    confidence=0.7,  # Lower confidence for text-extracted URLs
                                    extraction_method="text_regex",
                                    metadata={"pattern_used": pattern}
                                )
                                references.append(ref)
        
        except Exception as e:
            self.logger.error(f"Error extracting URLs from text: {e}")
        
        return references
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        # Remove trailing punctuation
        url = url.rstrip('.,;!?)')
        
        # Add protocol if missing
        if url.startswith('www.') and not url.startswith('http'):
            url = 'http://' + url
        
        return url
    
    def _is_valid_url_format(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https', 'ftp'], result.netloc])
        except Exception:
            return False
    
    def _extract_context_from_text(self, text: str, start: int, end: int) -> str:
        """Extract context around URL in text"""
        context_start = max(0, start - 100)
        context_end = min(len(text), end + 100)
        context = text[context_start:context_end]
        return ' '.join(context.split())

class CitationExtractor(ReferenceExtractor):
    """Extract academic citations from text"""
    
    def __init__(self):
        super().__init__("CitationExtractor")
        # Citation patterns
        self.citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\(([A-Za-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}[a-z]?)\)',  # (Author, 2020)
            r'([A-Za-z]+(?:\s+et\s+al\.?)?\s+\(\d{4}[a-z]?\))',  # Author (2020)
        ]
    
    def extract(self, pdf_path: str) -> List[ExtractedReference]:
        """Extract citation references from PDF"""
        if not PDFPLUMBER_AVAILABLE:
            return []
        
        references = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    
                    for pattern in self.citation_patterns:
                        matches = re.finditer(pattern, page_text, re.IGNORECASE)
                        
                        for match in matches:
                            citation = match.group(0)
                            context = self._extract_context_from_text(page_text, match.start(), match.end())
                            
                            ref = ExtractedReference(
                                value=citation,
                                reference_type="citation",
                                page_number=page_num + 1,
                                context=context,
                                confidence=0.6,  # Lower confidence for citations
                                extraction_method="citation_pattern",
                                metadata={"pattern_used": pattern}
                            )
                            references.append(ref)
        
        except Exception as e:
            self.logger.error(f"Error extracting citations: {e}")
        
        return references
    
    def _extract_context_from_text(self, text: str, start: int, end: int) -> str:
        """Extract context around citation in text"""
        context_start = max(0, start - 150)
        context_end = min(len(text), end + 150)
        context = text[context_start:context_end]
        return ' '.join(context.split())

class AdvancedPDFProcessor:
    """Advanced PDF processor with multiple extraction methods"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.extractors = [
            HyperlinkExtractor(),
            DOIExtractor(),
            URLTextExtractor(),
            CitationExtractor()
        ]
    
    def extract_all_references(self, pdf_path: str, max_references: int = 100) -> List[ExtractedReference]:
        """Extract all types of references from PDF"""
        all_references = []
        
        for extractor in self.extractors:
            try:
                refs = extractor.extract(pdf_path)
                all_references.extend(refs)
                self.logger.info(f"{extractor.name} found {len(refs)} references")
            except Exception as e:
                self.logger.error(f"Error in {extractor.name}: {e}")
        
        # Deduplicate references
        unique_references = self._deduplicate_references(all_references)
        
        # Sort by confidence and limit
        unique_references.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_references[:max_references]
    
    def _deduplicate_references(self, references: List[ExtractedReference]) -> List[ExtractedReference]:
        """Remove duplicate references"""
        seen_values = set()
        unique_refs = []
        
        for ref in references:
            # Create a normalized key for comparison
            normalized_value = self._normalize_reference_value(ref.value, ref.reference_type)
            
            if normalized_value not in seen_values:
                seen_values.add(normalized_value)
                unique_refs.append(ref)
            else:
                # If duplicate found, keep the one with higher confidence
                for i, existing_ref in enumerate(unique_refs):
                    existing_normalized = self._normalize_reference_value(
                        existing_ref.value, existing_ref.reference_type
                    )
                    if existing_normalized == normalized_value:
                        if ref.confidence > existing_ref.confidence:
                            unique_refs[i] = ref
                        break
        
        return unique_refs
    
    def _normalize_reference_value(self, value: str, ref_type: str) -> str:
        """Normalize reference value for comparison"""
        normalized = value.lower().strip()
        
        if ref_type == "url":
            # Remove trailing slashes and fragments
            normalized = normalized.rstrip('/')
            if '#' in normalized:
                normalized = normalized.split('#')[0]
        
        elif ref_type == "doi":
            # Normalize DOI format
            normalized = normalized.replace('doi:', '').replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
        
        return normalized

class URLValidator:
    """Advanced URL validation and enhancement"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            
            # Set user agent
            self.session.headers.update({
                'User-Agent': 'Academic Research Bot 1.0 (Research Validation)'
            })
    
    async def validate_and_enhance_url(self, url: str, timeout: int = 10) -> URLValidationResult:
        """Validate URL and extract metadata"""
        result = URLValidationResult(original_url=url)
        
        if not REQUESTS_AVAILABLE or not self.session:
            result.error = "Requests library not available"
            return result
        
        try:
            # First try HEAD request for basic validation
            response = self.session.head(url, timeout=timeout, allow_redirects=True)
            
            result.is_accessible = response.status_code < 400
            result.status_code = response.status_code
            result.final_url = response.url if response.url != url else None
            result.content_type = response.headers.get('content-type', '')
            result.last_modified = response.headers.get('last-modified')
            
            # Track redirect chain
            if hasattr(response, 'history'):
                result.redirect_chain = [r.url for r in response.history]
            
            # If accessible, try to get more metadata
            if result.is_accessible and result.content_type.startswith('text/html'):
                try:
                    full_response = self.session.get(url, timeout=timeout)
                    result.metadata = self._extract_html_metadata(full_response.text)
                except Exception as e:
                    self.logger.warning(f"Could not extract metadata from {url}: {e}")
            
        except requests.exceptions.Timeout:
            result.error = "Request timeout"
        except requests.exceptions.ConnectionError:
            result.error = "Connection error"
        except requests.exceptions.RequestException as e:
            result.error = f"Request error: {str(e)}"
        except Exception as e:
            result.error = f"Unexpected error: {str(e)}"
        
        return result
    
    def _extract_html_metadata(self, html_content: str) -> Dict[str, Any]:
        """Extract metadata from HTML content"""
        metadata = {}
        
        try:
            # Simple regex-based extraction (could be enhanced with BeautifulSoup)
            
            # Title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            # Meta description
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if desc_match:
                metadata['description'] = desc_match.group(1).strip()
            
            # Meta keywords
            keywords_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if keywords_match:
                metadata['keywords'] = keywords_match.group(1).strip()
            
            # Author
            author_match = re.search(r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if author_match:
                metadata['author'] = author_match.group(1).strip()
            
            # Publication date
            date_patterns = [
                r'<meta[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']',
                r'<meta[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)["\']',
                r'<meta[^>]*name=["\']published["\'][^>]*content=["\']([^"\']+)["\']'
            ]
            
            for pattern in date_patterns:
                date_match = re.search(pattern, html_content, re.IGNORECASE)
                if date_match:
                    metadata['published_date'] = date_match.group(1).strip()
                    break
        
        except Exception as e:
            self.logger.warning(f"Error extracting HTML metadata: {e}")
        
        return metadata
    
    async def validate_multiple_urls(self, urls: List[str], max_concurrent: int = 5) -> List[URLValidationResult]:
        """Validate multiple URLs concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def validate_with_semaphore(url: str) -> URLValidationResult:
            async with semaphore:
                return await self.validate_and_enhance_url(url)
        
        tasks = [validate_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        validated_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = URLValidationResult(
                    original_url=urls[i],
                    error=f"Validation failed: {str(result)}"
                )
                validated_results.append(error_result)
            else:
                validated_results.append(result)
        
        return validated_results 