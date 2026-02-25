from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, HttpUrl, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import re

from app.models import get_db
from app.services.crawler import SitemapCrawler
from app.services.token_service import check_and_use_scan, get_remaining_scans
from app.metrics import scan_requests, scans_completed, scan_duration

router = APIRouter(prefix="/api/v1/scan", tags=["scanner"])


class ScanRequest(BaseModel):
    url: str
    max_pages: Optional[int] = 50
    max_depth: Optional[int] = 2
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        # Allow URLs without protocol
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        # Basic URL validation
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid URL format')
        return v
    
    @field_validator('max_pages')
    @classmethod
    def validate_max_pages(cls, v):
        if v is not None and (v < 1 or v > 50):
            raise ValueError('max_pages must be between 1 and 50')
        return v
    
    @field_validator('max_depth')
    @classmethod
    def validate_max_depth(cls, v):
        if v is not None and (v < 1 or v > 2):
            raise ValueError('max_depth must be between 1 and 2')
        return v


class NodeInfo(BaseModel):
    id: int
    url: str
    title: str
    status: int
    depth: int
    linkCount: int


class LinkInfo(BaseModel):
    source: int
    target: int


class ScanStats(BaseModel):
    totalPages: int
    totalLinks: int
    brokenPages: int
    maxDepth: int


class ScanResponse(BaseModel):
    success: bool
    root_url: str
    nodes: List[NodeInfo]
    links: List[LinkInfo]
    stats: ScanStats
    remaining_scans: int


class QuotaResponse(BaseModel):
    free_remaining: int
    paid_remaining: int
    total_remaining: int


@router.post("", response_model=ScanResponse)
async def scan_website(
    request: ScanRequest,
    x_device_id: str = Header(..., alias="X-Device-Id"),
    db: AsyncSession = Depends(get_db)
):
    """
    Scan a website and return its structure as a graph.
    
    Rate limited by device ID. Free tier: 5 scans/day.
    """
    scan_requests.labels(tool="sitemap-scanner").inc()
    
    # Check quota
    allowed, reason, remaining = await check_and_use_scan(db, x_device_id)
    
    if not allowed:
        raise HTTPException(
            status_code=402,
            detail="Daily scan limit reached. Purchase more scans to continue."
        )
    
    # Perform scan
    import time
    start_time = time.time()
    
    crawler = SitemapCrawler(
        max_pages=request.max_pages,
        max_depth=request.max_depth
    )
    
    try:
        result = await crawler.scan(request.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
    
    duration = time.time() - start_time
    scan_duration.labels(tool="sitemap-scanner").observe(duration)
    scans_completed.labels(tool="sitemap-scanner", status="success").inc()
    
    return ScanResponse(
        success=True,
        root_url=result.root_url,
        nodes=result.nodes,
        links=result.links,
        stats=result.stats,
        remaining_scans=remaining
    )


@router.get("/quota", response_model=QuotaResponse)
async def get_quota(
    x_device_id: str = Header(..., alias="X-Device-Id"),
    db: AsyncSession = Depends(get_db)
):
    """Get remaining scan quota for the device."""
    return await get_remaining_scans(db, x_device_id)
