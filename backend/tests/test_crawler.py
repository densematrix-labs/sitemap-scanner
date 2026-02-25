import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from app.services.crawler import SitemapCrawler, PageInfo


class TestSitemapCrawler:
    
    def test_normalize_url(self):
        crawler = SitemapCrawler()
        
        assert crawler._normalize_url("https://example.com/") == "https://example.com"
        assert crawler._normalize_url("https://example.com/page#section") == "https://example.com/page"
        assert crawler._normalize_url("http://example.com/path/") == "http://example.com/path"
    
    def test_is_same_domain(self):
        crawler = SitemapCrawler()
        crawler.base_domain = "https://example.com"
        
        assert crawler._is_same_domain("https://example.com/page") is True
        assert crawler._is_same_domain("https://example.com/page/sub") is True
        assert crawler._is_same_domain("https://other.com/page") is False
        assert crawler._is_same_domain("https://sub.example.com/page") is False
    
    def test_is_valid_url(self):
        crawler = SitemapCrawler()
        
        assert crawler._is_valid_url("https://example.com") is True
        assert crawler._is_valid_url("http://example.com") is True
        assert crawler._is_valid_url("ftp://example.com") is False
        assert crawler._is_valid_url("mailto:test@example.com") is False
        assert crawler._is_valid_url("https://example.com/file.pdf") is False
        assert crawler._is_valid_url("https://example.com/image.jpg") is False
        assert crawler._is_valid_url("https://example.com/style.css") is False
    
    def test_is_allowed_by_robots_no_parser(self):
        crawler = SitemapCrawler()
        crawler.robots_parser = None
        
        assert crawler._is_allowed_by_robots("https://example.com/page") is True
    
    def test_build_result(self):
        crawler = SitemapCrawler()
        crawler.pages = {
            "https://example.com": PageInfo(
                url="https://example.com",
                title="Home",
                status=200,
                links=["https://example.com/about"],
                depth=0
            ),
            "https://example.com/about": PageInfo(
                url="https://example.com/about",
                title="About",
                status=200,
                links=[],
                depth=1
            )
        }
        
        result = crawler._build_result("https://example.com")
        
        assert result.root_url == "https://example.com"
        assert len(result.nodes) == 2
        assert len(result.links) == 1
        assert result.stats["totalPages"] == 2
        assert result.stats["totalLinks"] == 1
        assert result.stats["brokenPages"] == 0
        assert result.stats["maxDepth"] == 1
    
    def test_build_result_with_broken_page(self):
        crawler = SitemapCrawler()
        crawler.pages = {
            "https://example.com": PageInfo(
                url="https://example.com",
                title="Home",
                status=200,
                links=["https://example.com/404"],
                depth=0
            ),
            "https://example.com/404": PageInfo(
                url="https://example.com/404",
                title="Not Found",
                status=404,
                links=[],
                depth=1
            )
        }
        
        result = crawler._build_result("https://example.com")
        
        assert result.stats["brokenPages"] == 1


@pytest.mark.asyncio
async def test_fetch_page_success():
    crawler = SitemapCrawler()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"content-type": "text/html"}
    mock_response.text = AsyncMock(return_value="""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <a href="/about">About</a>
                <a href="https://example.com/contact">Contact</a>
            </body>
        </html>
    """)
    
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    page = await crawler._fetch_page(mock_session, "https://example.com")
    
    assert page.title == "Test Page"
    assert page.status == 200


@pytest.mark.asyncio
async def test_fetch_page_timeout():
    import asyncio
    
    crawler = SitemapCrawler()
    
    mock_session = AsyncMock()
    mock_session.get.side_effect = asyncio.TimeoutError()
    
    page = await crawler._fetch_page(mock_session, "https://example.com")
    
    assert page.status == 0
    assert page.title == "Timeout"


@pytest.mark.asyncio
async def test_fetch_page_non_html():
    crawler = SitemapCrawler()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"content-type": "application/json"}
    
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    page = await crawler._fetch_page(mock_session, "https://example.com/api")
    
    assert page.links == []


@pytest.mark.asyncio 
async def test_scan_basic():
    """Test basic scan flow with mocked HTTP."""
    crawler = SitemapCrawler(max_pages=5, max_depth=1)
    
    html_content = """
        <html>
            <head><title>Test</title></head>
            <body>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
            </body>
        </html>
    """
    
    with patch.object(crawler, '_fetch_robots_txt', new_callable=AsyncMock):
        with patch.object(crawler, '_fetch_page', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = PageInfo(
                url="https://example.com",
                title="Test",
                status=200,
                links=["https://example.com/page1", "https://example.com/page2"]
            )
            
            result = await crawler.scan("https://example.com")
            
            assert result.root_url == "https://example.com"
            assert len(result.nodes) >= 1
