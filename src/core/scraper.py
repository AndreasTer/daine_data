import asyncio
import random
from typing import List
from loguru import logger
from src.config.settings import CITY_URLS, scraper_config
from src.utils.http import HttpClient
from src.utils.parsing import TabelogParser
from src.core.database import Database

class TabelogScraper:
    def __init__(self, db: Database):
        self.config = scraper_config
        self.db = db
        self.http_client = HttpClient()
        self.parser = TabelogParser()

    async def initialize(self):
        """Initialize the scraper."""
        await self.http_client.initialize()

    async def close(self):
        """Close the scraper."""
        await self.http_client.close()

    async def _get_restaurant_urls(self, base_url: str, page: int) -> List[str]:
        """Get restaurant URLs from a listing page."""
        # Add page parameter to URL if it's not the first page
        url = f"{base_url}/rstLst/{page}/" if page > 1 else base_url
        html = await self.http_client.get(url)
        if not html:
            return []

        urls = self.parser.extract_restaurant_urls(html)
        if not urls:
            await self.db.log_error("URL_EXTRACTION_ERROR", f"No URLs found on page {page}", url)
        return urls

    async def _scrape_restaurant(self, url: str, search_term: str) -> bool:
        """Scrape a single restaurant."""
        html = await self.http_client.get(url)
        if not html:
            return False

        # Extract area from URL (e.g., "tokyo" from "/tokyo/...")
        url_parts = url.split('/')
        area = None
        for city in CITY_URLS:
            if city in url_parts:
                area = city
                break
        
        if not area:
            # If no city found in URL, use the region from JSON-LD as area
            restaurant_data = self.parser.parse_restaurant_page(html, url, None)
            if restaurant_data and restaurant_data.get('region'):
                area = restaurant_data['region'].lower()
            else:
                area = 'unknown'
        
        # Now parse with the correct area
        restaurant_data = self.parser.parse_restaurant_page(html, url, area)
        if restaurant_data:
            logger.debug(f"Storing restaurant with area: {area}, city: {restaurant_data.get('city')}, region: {restaurant_data.get('region')}")
            return await self.db.insert_restaurant(restaurant_data)
        return False

    async def scrape_listing(self, base_url: str, pages: int, search_term: str):
        """Scrape restaurants from a listing page."""
        logger.info(f"Starting scrape for search term: {search_term}")
        
        for page in range(1, pages + 1):
            restaurant_urls = await self._get_restaurant_urls(base_url, page)
            tasks = []
            
            for url in restaurant_urls:
                if not await self.db.url_exists(url):
                    tasks.append(self._scrape_restaurant(url, search_term))
                
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                successful = len([r for r in results if r])
                logger.info(f"Processed {successful} restaurants from page {page}")
                logger.info(f"Found {len(restaurant_urls)} restaurants, {successful} new entries added")
            
            await asyncio.sleep(random.uniform(1, 2))