from dataclasses import dataclass
from typing import Dict

@dataclass
class ScraperConfig:
    BASE_URL: str = "https://tabelog.com/en"
    CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    DELAY_BETWEEN_REQUESTS: float = 1.0  # seconds
    MAX_RESTAURANTS_PER_MINUTE: int = 100

    # Headers to mimic browser behavior
    DEFAULT_HEADERS: Dict[str, str] = None

    def __post_init__(self):
        self.DEFAULT_HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

@dataclass
class DatabaseConfig:
    DB_NAME: str = "tabelog_restaurants.db"
    TABLES: Dict[str, str] = None

    def __post_init__(self):
        self.TABLES = {
            "restaurants": """
                CREATE TABLE IF NOT EXISTS restaurants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_en TEXT,
                    name_jp TEXT,
                    rating REAL,
                    review_count INTEGER,
                    address TEXT,
                    city TEXT,
                    region TEXT,
                    latitude REAL,
                    longitude REAL,
                    price_lunch TEXT,
                    price_dinner TEXT,
                    url TEXT UNIQUE,
                    area TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "categories": """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            """,
            "restaurant_categories": """
                CREATE TABLE IF NOT EXISTS restaurant_categories (
                    restaurant_id INTEGER,
                    category_id INTEGER,
                    PRIMARY KEY (restaurant_id, category_id),
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """,
            "error_logs": """
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT,
                    error_message TEXT,
                    url TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }

# Cities and their corresponding Tabelog URLs
CITY_URLS: Dict[str, str] = {
    "tokyo": "/tokyo/",
    "osaka": "/osaka/",
    "kyoto": "/kyoto/",
    "yokohama": "/yokohama/",
    "sapporo": "/sapporo/",
}

# URL patterns for different search types
URL_PATTERNS: Dict[str, str] = {
    "city": "{base_url}{location}",
    "food": "{base_url}/rstLst/{cuisine}/?SrtT=rt"  # Sorted by rating
}

# Create instances of configs
scraper_config = ScraperConfig()
db_config = DatabaseConfig() 