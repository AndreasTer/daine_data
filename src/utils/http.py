from typing import Dict, Optional
import httpx
import asyncio
import random
from loguru import logger
from fake_useragent import UserAgent
from src.config.settings import scraper_config
import socket
import time

class HttpClient:
    def __init__(self):
        self.config = scraper_config
        self.client = None
        self.ua = UserAgent()
        self.semaphore = asyncio.Semaphore(self.config.CONCURRENT_REQUESTS)

    async def initialize(self):
        """Initialize the HTTP client."""
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=self.config.REQUEST_TIMEOUT,
                follow_redirects=True
            )

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with a random user agent."""
        headers = self.config.DEFAULT_HEADERS.copy()
        headers["User-Agent"] = self.ua.random
        return headers

    async def _wait_with_exponential_backoff(self, retry_count: int):
        """Wait with exponential backoff between retries."""
        wait_time = min(300, (2 ** retry_count) + random.uniform(0, 1))  # Cap at 300 seconds
        logger.warning(f"Waiting {wait_time:.2f} seconds before retry {retry_count + 1}")
        await asyncio.sleep(wait_time)

    async def get(self, url: str, retry_count: int = 0) -> Optional[str]:
        """Make an HTTP GET request with retry logic and rate limiting."""
        if retry_count >= self.config.RETRY_ATTEMPTS:
            logger.error(f"Max retries exceeded for URL: {url}")
            return None

        try:
            async with self.semaphore:
                await asyncio.sleep(self.config.DELAY_BETWEEN_REQUESTS)
                
                try:
                    response = await self.client.get(url, headers=self._get_headers())
                    
                    if response.status_code == 200:
                        return response.text
                    elif response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        return await self.get(url, retry_count + 1)
                    else:
                        logger.error(f"HTTP {response.status_code} for URL: {url}")
                        if response.status_code in [500, 502, 503, 504]:
                            await self._wait_with_exponential_backoff(retry_count)
                            return await self.get(url, retry_count + 1)
                        return None
                
                except (httpx.ConnectError, httpx.ConnectTimeout, socket.gaierror) as e:
                    logger.error(f"Connection error for {url}: {str(e)}")
                    await self._wait_with_exponential_backoff(retry_count)
                    return await self.get(url, retry_count + 1)
                
                except httpx.TimeoutException as e:
                    logger.error(f"Timeout error for {url}: {str(e)}")
                    await self._wait_with_exponential_backoff(retry_count)
                    return await self.get(url, retry_count + 1)
                
                except Exception as e:
                    logger.error(f"Error fetching {url}: {str(e)}")
                    await self._wait_with_exponential_backoff(retry_count)
                    return await self.get(url, retry_count + 1)

        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            await asyncio.sleep(random.uniform(1, 3))
            return await self.get(url, retry_count + 1) 