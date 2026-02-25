# Sitemap Scanner

Visual website sitemap scanner - crawl any website and visualize its structure with an interactive force-directed graph.

## Features

- 🔍 **Shallow Crawl**: Scan up to 50 pages, max 2 levels deep
- 📊 **Interactive Graph**: Force-directed visualization of site structure
- 🚦 **Broken Link Detection**: Identify pages with errors
- 🌍 **Multi-language**: Supports EN, ZH, JA, DE, FR, KO, ES
- ⚡ **Fast & Respectful**: Rate-limited, respects robots.txt

## Tech Stack

- **Frontend**: React + Vite + TypeScript + react-force-graph-2d
- **Backend**: Python FastAPI + aiohttp + BeautifulSoup
- **Database**: SQLite (for usage tracking)

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up -d
```

## API

### POST /api/v1/scan

Scan a website.

Request:
```json
{
  "url": "https://example.com",
  "max_pages": 50,
  "max_depth": 2
}
```

Headers:
- `X-Device-Id`: Device fingerprint for rate limiting

Response:
```json
{
  "success": true,
  "root_url": "https://example.com",
  "nodes": [...],
  "links": [...],
  "stats": {
    "totalPages": 25,
    "totalLinks": 48,
    "brokenPages": 2,
    "maxDepth": 2
  },
  "remaining_scans": 4
}
```

### GET /api/v1/scan/quota

Get remaining scan quota.

## Legal Compliance

This tool is designed to be used responsibly:
- Only scan websites you own or have permission to scan
- Respects robots.txt directives
- Rate-limited to 1 request/second
- Maximum 50 pages per scan

## License

MIT
