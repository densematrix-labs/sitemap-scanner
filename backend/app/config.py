from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sitemap Scanner"
    DEBUG: bool = False
    
    # Crawler
    MAX_PAGES: int = 50
    MAX_DEPTH: int = 2
    REQUEST_DELAY: float = 1.0  # seconds between requests
    REQUEST_TIMEOUT: int = 10
    USER_AGENT: str = "SitemapScanner/1.0 (+https://sitemap-scanner.demo.densematrix.ai)"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    # Free tier
    FREE_SCANS_PER_DAY: int = 5
    
    # Payment (Creem)
    CREEM_API_KEY: str = ""
    CREEM_WEBHOOK_SECRET: str = ""
    CREEM_PRODUCT_IDS: str = "{}"
    
    # Metrics
    TOOL_NAME: str = "sitemap-scanner"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
