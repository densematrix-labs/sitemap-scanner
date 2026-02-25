# Sitemap Scanner — Visual Website Structure Analyzer

## Overview
| Item | Value |
|------|-------|
| Tool Name | Sitemap Scanner |
| Tool Slug | sitemap-scanner |
| URL | https://sitemap-scanner.demo.densematrix.ai |
| Target Users | Web developers, SEO specialists, site owners |

## Core Features (MVP)
1. **URL Input** — User provides a website URL to scan
2. **Shallow Crawl** — Extract all links from the page (max 2 levels deep)
3. **Visual Sitemap** — Interactive force-directed graph showing page relationships
4. **Statistics** — Page count, link count, broken links detection

## Legal Compliance (🔴 Critical)
- ✅ **User Authorization**: ToS requires users to only scan sites they own/control
- ✅ **Rate Limiting**: 1 request/second max
- ✅ **Robots.txt**: Check and respect robots.txt
- ✅ **Page Limit**: Maximum 50 pages per scan
- ✅ **User-Agent**: Identify as "SitemapScanner/1.0 (+sitemap-scanner.demo.densematrix.ai)"

## Differentiation
- ✅ Free to use (5 scans/day)
- ✅ No registration required
- ✅ Visual graph output (not just list)
- ✅ Instant results

## Tech Stack
- Backend: Python FastAPI + aiohttp + BeautifulSoup4
- Frontend: React + Vite (TypeScript) + react-force-graph-2d
- Database: SQLite (token tracking)
- Deployment: Docker → langsheng

## Completion Criteria
- [ ] Core scan functionality works
- [ ] Visual graph renders correctly
- [ ] Deployed to sitemap-scanner.demo.densematrix.ai
- [ ] Health check passes
