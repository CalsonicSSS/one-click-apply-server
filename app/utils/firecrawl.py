from firecrawl import FirecrawlApp
from app.config import get_settings

settings = get_settings()

firecrawl_app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)


