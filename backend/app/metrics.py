from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter
from fastapi.responses import Response

# Counters
http_requests = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["tool", "endpoint", "method", "status"]
)

scan_requests = Counter(
    "scan_requests_total",
    "Total scan requests",
    ["tool"]
)

scans_completed = Counter(
    "scans_completed_total",
    "Completed scans",
    ["tool", "status"]
)

payment_success = Counter(
    "payment_success_total",
    "Successful payments",
    ["tool", "product_sku"]
)

payment_revenue_cents = Counter(
    "payment_revenue_cents_total",
    "Total revenue in cents",
    ["tool"]
)

tokens_consumed = Counter(
    "tokens_consumed_total",
    "Tokens consumed",
    ["tool"]
)

free_trial_used = Counter(
    "free_trial_used_total",
    "Free trial scans used",
    ["tool"]
)

page_views = Counter(
    "page_views_total",
    "Page views",
    ["tool", "page"]
)

crawler_visits = Counter(
    "crawler_visits_total",
    "Crawler visits",
    ["tool", "bot"]
)

# Histograms
scan_duration = Histogram(
    "scan_duration_seconds",
    "Scan duration in seconds",
    ["tool"],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

# Gauges
active_scans = Gauge(
    "active_scans",
    "Currently active scans",
    ["tool"]
)


# Metrics endpoint
metrics_router = APIRouter()


@metrics_router.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
