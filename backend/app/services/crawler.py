import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from robotexclusionrulesparser import RobotExclusionRulesParser
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class PageInfo:
    url: str
    title: str
    status: int
    links: List[str] = field(default_factory=list)
    depth: int = 0


@dataclass
class ScanResult:
    root_url: str
    pages: Dict[str, PageInfo]
    nodes: List[dict]
    links: List[dict]
    stats: dict


class SitemapCrawler:
    def __init__(self, max_pages: int = None, max_depth: int = None, delay: float = None):
        self.max_pages = max_pages or settings.MAX_PAGES
        self.max_depth = max_depth or settings.MAX_DEPTH
        self.delay = delay or settings.REQUEST_DELAY
        self.user_agent = settings.USER_AGENT
        self.timeout = settings.REQUEST_TIMEOUT
        
        self.visited: Set[str] = set()
        self.pages: Dict[str, PageInfo] = {}
        self.robots_parser: Optional[RobotExclusionRulesParser] = None
        self.base_domain: str = ""
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes."""
        parsed = urlparse(url)
        # Remove fragment and normalize
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if normalized.endswith('/') and len(parsed.path) > 1:
            normalized = normalized[:-1]
        return normalized
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(self.base_domain)
            return parsed.netloc == base_parsed.netloc
        except Exception:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling."""
        try:
            parsed = urlparse(url)
            # Only http/https
            if parsed.scheme not in ('http', 'https'):
                return False
            # Skip file downloads
            skip_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js', '.zip', '.tar', '.gz')
            if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
                return False
            return True
        except Exception:
            return False
    
    async def _fetch_robots_txt(self, session: aiohttp.ClientSession, base_url: str) -> None:
        """Fetch and parse robots.txt."""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    content = await response.text()
                    self.robots_parser = RobotExclusionRulesParser()
                    self.robots_parser.parse(content)
                    logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {e}")
            self.robots_parser = None
    
    def _is_allowed_by_robots(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        if self.robots_parser is None:
            return True
        try:
            return self.robots_parser.is_allowed("*", url)
        except Exception:
            return True
    
    async def _fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[PageInfo]:
        """Fetch a single page and extract info."""
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                allow_redirects=True
            ) as response:
                if response.status != 200:
                    return PageInfo(url=url, title="", status=response.status, links=[])
                
                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type:
                    return PageInfo(url=url, title="", status=response.status, links=[])
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract title
                title_tag = soup.find('title')
                title = title_tag.get_text(strip=True) if title_tag else url
                
                # Extract links
                links = []
                for anchor in soup.find_all('a', href=True):
                    href = anchor['href']
                    full_url = urljoin(url, href)
                    normalized = self._normalize_url(full_url)
                    
                    if self._is_valid_url(normalized) and self._is_same_domain(normalized):
                        if normalized not in links:
                            links.append(normalized)
                
                return PageInfo(url=url, title=title[:200], status=response.status, links=links)
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url}")
            return PageInfo(url=url, title="Timeout", status=0, links=[])
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return PageInfo(url=url, title=str(e)[:100], status=0, links=[])
    
    async def scan(self, start_url: str) -> ScanResult:
        """Scan a website starting from the given URL."""
        # Normalize and validate start URL
        start_url = self._normalize_url(start_url)
        if not start_url.startswith(('http://', 'https://')):
            start_url = 'https://' + start_url
        
        self.base_domain = start_url
        self.visited = set()
        self.pages = {}
        
        headers = {'User-Agent': self.user_agent}
        connector = aiohttp.TCPConnector(limit=5)  # Limit concurrent connections
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            # Fetch robots.txt first
            await self._fetch_robots_txt(session, start_url)
            
            # BFS crawl
            queue = [(start_url, 0)]  # (url, depth)
            
            while queue and len(self.pages) < self.max_pages:
                url, depth = queue.pop(0)
                normalized_url = self._normalize_url(url)
                
                if normalized_url in self.visited:
                    continue
                if depth > self.max_depth:
                    continue
                if not self._is_allowed_by_robots(normalized_url):
                    logger.info(f"Blocked by robots.txt: {normalized_url}")
                    continue
                
                self.visited.add(normalized_url)
                
                # Rate limiting
                if len(self.pages) > 0:
                    await asyncio.sleep(self.delay)
                
                page = await self._fetch_page(session, normalized_url)
                if page:
                    page.depth = depth
                    self.pages[normalized_url] = page
                    
                    # Add links to queue
                    if depth < self.max_depth:
                        for link in page.links:
                            if link not in self.visited:
                                queue.append((link, depth + 1))
        
        # Build graph data
        return self._build_result(start_url)
    
    def _build_result(self, root_url: str) -> ScanResult:
        """Build the scan result with graph data."""
        nodes = []
        links = []
        url_to_id = {}
        
        # Create nodes
        for i, (url, page) in enumerate(self.pages.items()):
            url_to_id[url] = i
            nodes.append({
                "id": i,
                "url": url,
                "title": page.title,
                "status": page.status,
                "depth": page.depth,
                "linkCount": len(page.links)
            })
        
        # Create links
        for url, page in self.pages.items():
            source_id = url_to_id[url]
            for target_url in page.links:
                if target_url in url_to_id:
                    target_id = url_to_id[target_url]
                    links.append({
                        "source": source_id,
                        "target": target_id
                    })
        
        # Statistics
        stats = {
            "totalPages": len(self.pages),
            "totalLinks": len(links),
            "brokenPages": sum(1 for p in self.pages.values() if p.status != 200),
            "maxDepth": max((p.depth for p in self.pages.values()), default=0)
        }
        
        return ScanResult(
            root_url=root_url,
            pages=self.pages,
            nodes=nodes,
            links=links,
            stats=stats
        )
