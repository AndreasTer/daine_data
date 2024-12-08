import asyncio
import argparse
from loguru import logger
import sys
from typing import Optional
from src.core.database import Database
from src.core.scraper import TabelogScraper
from src.config import CITY_URLS, URL_PATTERNS, scraper_config

def setup_logger():
    """Configure logging settings."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )
    logger.add(
        "scraper.log",
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Tabelog Restaurant Data Scraper")
    
    # Create a mutually exclusive group for search type
    search_type = parser.add_mutually_exclusive_group(required=True)
    search_type.add_argument(
        "--city",
        type=str,
        choices=list(CITY_URLS.keys()),
        help="City to scrape restaurants from"
    )
    search_type.add_argument(
        "--food",
        "-f",
        type=str,
        help="Food type to search for (e.g., pizza, sushi, ramen)"
    )
    
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to scrape (default: 1)"
    )
    return parser.parse_args()

def get_search_url(args) -> str:
    """Generate the appropriate search URL based on arguments."""
    base_url = scraper_config.BASE_URL
    
    if args.city:
        return URL_PATTERNS["city"].format(
            base_url=base_url,
            location=CITY_URLS[args.city]
        )
    elif args.food:
        return URL_PATTERNS["food"].format(
            base_url=base_url,
            cuisine=args.food.lower()
        )
    else:
        raise ValueError("Either city or food argument must be provided")

async def main():
    """Main execution function."""
    # Setup logging
    setup_logger()
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Initialize database
        db = Database()
        await db.initialize()
        logger.info("Database initialized successfully")
        
        # Initialize scraper
        scraper = TabelogScraper(db)
        await scraper.initialize()
        logger.info("Scraper initialized successfully")
        
        # Get the appropriate search URL
        search_url = get_search_url(args)
        search_type = "city" if args.city else "food"
        search_term = args.city if args.city else args.food
        
        # Start scraping
        logger.info(f"Starting scrape for {search_type}: {search_term}, {args.pages} pages")
        await scraper.scrape_listing(search_url, args.pages, search_term)
        
        # Get final count
        count = await db.get_restaurant_count()
        logger.info(f"Scraping completed. Total restaurants in database: {count}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)
    finally:
        if 'scraper' in locals():
            await scraper.close()
        logger.info("Scraper closed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1) 