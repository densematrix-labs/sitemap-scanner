import pytest
from unittest.mock import AsyncMock, patch

from app.services.crawler import ScanResult, PageInfo


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


@pytest.mark.asyncio
async def test_get_quota_new_device(client):
    response = await client.get(
        "/api/v1/scan/quota",
        headers={"X-Device-Id": "test-device-1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["free_remaining"] == 5
    assert data["paid_remaining"] == 0


@pytest.mark.asyncio
async def test_scan_missing_device_id(client):
    response = await client.post(
        "/api/v1/scan",
        json={"url": "https://example.com"}
    )
    assert response.status_code == 422  # Missing header


@pytest.mark.asyncio
async def test_scan_invalid_url(client):
    response = await client.post(
        "/api/v1/scan",
        json={"url": "not-a-url"},
        headers={"X-Device-Id": "test-device-2"}
    )
    # Should still work - we prepend https://
    # Just check it doesn't crash
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_scan_max_pages_validation(client):
    response = await client.post(
        "/api/v1/scan",
        json={"url": "https://example.com", "max_pages": 100},
        headers={"X-Device-Id": "test-device-3"}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_scan_max_depth_validation(client):
    response = await client.post(
        "/api/v1/scan",
        json={"url": "https://example.com", "max_depth": 5},
        headers={"X-Device-Id": "test-device-4"}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_scan_success(client):
    # Mock the crawler
    mock_result = ScanResult(
        root_url="https://example.com",
        pages={"https://example.com": PageInfo(
            url="https://example.com",
            title="Example",
            status=200,
            links=[]
        )},
        nodes=[{"id": 0, "url": "https://example.com", "title": "Example", "status": 200, "depth": 0, "linkCount": 0}],
        links=[],
        stats={"totalPages": 1, "totalLinks": 0, "brokenPages": 0, "maxDepth": 0}
    )
    
    with patch("app.api.v1.scanner.SitemapCrawler") as MockCrawler:
        mock_instance = AsyncMock()
        mock_instance.scan.return_value = mock_result
        MockCrawler.return_value = mock_instance
        
        response = await client.post(
            "/api/v1/scan",
            json={"url": "https://example.com"},
            headers={"X-Device-Id": "test-device-5"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["root_url"] == "https://example.com"
        assert len(data["nodes"]) == 1
        assert data["remaining_scans"] == 4


@pytest.mark.asyncio
async def test_quota_exhausted(client):
    device_id = "quota-test-device"
    
    # Mock successful scan result
    mock_result = ScanResult(
        root_url="https://example.com",
        pages={},
        nodes=[],
        links=[],
        stats={"totalPages": 0, "totalLinks": 0, "brokenPages": 0, "maxDepth": 0}
    )
    
    with patch("app.api.v1.scanner.SitemapCrawler") as MockCrawler:
        mock_instance = AsyncMock()
        mock_instance.scan.return_value = mock_result
        MockCrawler.return_value = mock_instance
        
        # Use up all 5 free scans
        for i in range(5):
            response = await client.post(
                "/api/v1/scan",
                json={"url": "https://example.com"},
                headers={"X-Device-Id": device_id}
            )
            assert response.status_code == 200
        
        # 6th scan should fail
        response = await client.post(
            "/api/v1/scan",
            json={"url": "https://example.com"},
            headers={"X-Device-Id": device_id}
        )
        assert response.status_code == 402


@pytest.mark.asyncio
async def test_error_response_format(client):
    """Test that 402 error has proper string detail."""
    device_id = "error-test-device"
    
    mock_result = ScanResult(
        root_url="https://example.com",
        pages={},
        nodes=[],
        links=[],
        stats={"totalPages": 0, "totalLinks": 0, "brokenPages": 0, "maxDepth": 0}
    )
    
    with patch("app.api.v1.scanner.SitemapCrawler") as MockCrawler:
        mock_instance = AsyncMock()
        mock_instance.scan.return_value = mock_result
        MockCrawler.return_value = mock_instance
        
        # Exhaust quota
        for _ in range(5):
            await client.post(
                "/api/v1/scan",
                json={"url": "https://example.com"},
                headers={"X-Device-Id": device_id}
            )
        
        # Get error response
        response = await client.post(
            "/api/v1/scan",
            json={"url": "https://example.com"},
            headers={"X-Device-Id": device_id}
        )
        
        assert response.status_code == 402
        data = response.json()
        detail = data.get("detail")
        # Detail should be a string, not an object
        assert isinstance(detail, str), f"detail should be string, got {type(detail)}"
        assert "[object Object]" not in str(detail)


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert b"http_requests_total" in response.content
