import aiosqlite
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
from src.config.settings import db_config

class Database:
    def __init__(self):
        self.db_name = db_config.DB_NAME
        self.tables = db_config.TABLES

    async def initialize(self):
        """Initialize the database and create tables if they don't exist."""
        async with aiosqlite.connect(self.db_name) as db:
            for table_name, create_table_sql in self.tables.items():
                try:
                    await db.execute(create_table_sql)
                    await db.commit()
                except Exception as e:
                    logger.error(f"Error creating table {table_name}: {str(e)}")
                    raise

    async def insert_restaurant(self, restaurant_data: Dict[str, Any]) -> bool:
        """Insert a restaurant record and its categories into the database."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                # Insert restaurant
                sql = """
                    INSERT INTO restaurants (
                        name_en, name_jp, rating, review_count, address,
                        city, region, latitude, longitude,
                        price_lunch, price_dinner, url, area
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                # Log the values being inserted
                values = (
                    restaurant_data.get('name_en'),
                    restaurant_data.get('name_jp'),
                    restaurant_data.get('rating'),
                    restaurant_data.get('review_count'),
                    restaurant_data.get('address'),
                    restaurant_data.get('city'),
                    restaurant_data.get('region'),
                    restaurant_data.get('latitude'),
                    restaurant_data.get('longitude'),
                    restaurant_data.get('price_lunch'),
                    restaurant_data.get('price_dinner'),
                    restaurant_data.get('url'),
                    restaurant_data.get('area')
                )
                
                logger.debug(f"Inserting restaurant with location data: city={values[5]}, region={values[6]}, lat={values[7]}, long={values[8]}")
                
                cursor = await db.execute(sql, values)
                restaurant_id = cursor.lastrowid

                # Insert categories
                categories = restaurant_data.get('categories', [])
                for category in categories:
                    category_id = await self._get_or_create_category(db, category)
                    if category_id:
                        await db.execute(
                            "INSERT INTO restaurant_categories (restaurant_id, category_id) VALUES (?, ?)",
                            (restaurant_id, category_id)
                        )

                await db.commit()
                return True
        except aiosqlite.IntegrityError as e:
            if "UNIQUE constraint failed: restaurants.url" in str(e):
                logger.warning(f"Duplicate restaurant URL: {restaurant_data.get('url')}")
            else:
                logger.error(f"Database integrity error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inserting restaurant: {str(e)}")
            return False

    async def _get_or_create_category(self, db: aiosqlite.Connection, category_name: str) -> Optional[int]:
        """Get category ID or create if it doesn't exist."""
        try:
            async with db.execute("SELECT id FROM categories WHERE name = ?", (category_name,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    return result[0]
            
            async with db.execute("INSERT INTO categories (name) VALUES (?)", (category_name,)) as cursor:
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error getting/creating category {category_name}: {str(e)}")
            return None

    async def log_error(self, error_type: str, error_message: str, url: Optional[str] = None):
        """Log an error to the database."""
        sql = "INSERT INTO error_logs (error_type, error_message, url) VALUES (?, ?, ?)"
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(sql, (error_type, error_message, url))
                await db.commit()
        except Exception as e:
            logger.error(f"Error logging to database: {str(e)}")

    async def get_restaurant_count(self) -> int:
        """Get the total number of restaurants in the database."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute("SELECT COUNT(*) FROM restaurants") as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting restaurant count: {str(e)}")
            return 0

    async def get_restaurants_by_area(self, area: str) -> List[Dict[str, Any]]:
        """Get all restaurants for a specific area."""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT r.*, GROUP_CONCAT(c.name) as categories
                    FROM restaurants r
                    LEFT JOIN restaurant_categories rc ON r.id = rc.restaurant_id
                    LEFT JOIN categories c ON rc.category_id = c.id
                    WHERE r.area = ?
                    GROUP BY r.id
                """, (area,)) as cursor:
                    rows = await cursor.fetchall()
                    restaurants = []
                    for row in rows:
                        restaurant = dict(row)
                        if restaurant['categories']:
                            restaurant['categories'] = restaurant['categories'].split(',')
                        else:
                            restaurant['categories'] = []
                        restaurants.append(restaurant)
                    return restaurants
        except Exception as e:
            logger.error(f"Error getting restaurants by area: {str(e)}")
            return []

    async def url_exists(self, url: str) -> bool:
        """Check if a restaurant URL already exists in the database."""
        sql = "SELECT COUNT(*) FROM restaurants WHERE url = ?"
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute(sql, (url,)) as cursor:
                    result = await cursor.fetchone()
                    return result[0] > 0 if result else False
        except Exception as e:
            logger.error(f"Error checking URL existence: {str(e)}")
            return False 