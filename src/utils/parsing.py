from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import json
from loguru import logger
import re

class TabelogParser:
    @staticmethod
    def _extract_number(text: str) -> int:
        """Extract number from Japanese text."""
        if not text:
            return 0
        # Extract digits from text (handles both half-width and full-width numbers)
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text by removing extra whitespace and parentheses."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.replace('(', '').replace(')', '')).strip()

    @staticmethod
    def _extract_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON-LD data from the page."""
        try:
            json_ld_script = soup.find('script', type='application/ld+json')
            if json_ld_script and json_ld_script.string:
                data = json.loads(json_ld_script.string)
                logger.debug(f"Found JSON-LD data: {data}")
                return data
        except Exception as e:
            logger.error(f"Error extracting JSON-LD data: {str(e)}")
        return None

    @staticmethod
    def _extract_price_range(soup: BeautifulSoup, meal_type: str) -> Optional[str]:
        """Extract price range for lunch or dinner."""
        try:
            # Find the price in the rdheader-budget section
            budget_section = soup.find('div', class_='rdheader-budget')
            if budget_section:
                # Find the rating div that contains the meal type icon
                meal_icon = budget_section.find('i', attrs={'aria-label': meal_type})
                if meal_icon:
                    # Get the parent p tag and then find the price link
                    price_container = meal_icon.find_parent('p')
                    if price_container:
                        price_link = price_container.find('a', class_='rdheader-budget__price-target')
                        if price_link and price_link.string:
                            price_text = price_link.string.strip()
                            # Return None if price is just a dash
                            if price_text == '-':
                                return None
                            # Clean up the price text
                            price_text = re.sub(r'\s+', ' ', price_text).strip()
                            logger.debug(f"Found {meal_type} price: {price_text}")
                            return price_text

            logger.debug(f"No {meal_type} price found in rdheader-budget section")
            return None

        except Exception as e:
            logger.error(f"Error extracting {meal_type} price: {str(e)}")
            return None

    @staticmethod
    def _extract_location_data(json_ld: Dict[str, Any]) -> tuple[Optional[str], Optional[str], Optional[str], Optional[float], Optional[float]]:
        """Extract location data from JSON-LD."""
        try:
            address_data = json_ld.get('address', {})
            geo_data = json_ld.get('geo', {})

            # Extract address components
            address_parts = [
                address_data.get('streetAddress', ''),
                address_data.get('addressLocality', ''),
                address_data.get('addressRegion', ''),
                address_data.get('postalCode', '')
            ]
            address = ' '.join(part for part in address_parts if part).strip()

            # Extract city (first part of addressLocality before any spaces)
            city = None
            if address_data.get('addressLocality'):
                city = address_data['addressLocality'].split(' ')[0]

            # Extract region
            region = address_data.get('addressRegion')

            # Extract coordinates
            latitude = longitude = None
            if isinstance(geo_data.get('latitude'), (int, float)):
                latitude = float(geo_data['latitude'])
            if isinstance(geo_data.get('longitude'), (int, float)):
                longitude = float(geo_data['longitude'])

            logger.debug(f"Extracted location data - Address: {address}, City: {city}, Region: {region}, Coords: ({latitude}, {longitude})")
            return address, city, region, latitude, longitude

        except Exception as e:
            logger.error(f"Error extracting location data: {str(e)}")
            return None, None, None, None, None

    @staticmethod
    def parse_restaurant_page(html: str, url: str, area: str) -> Optional[Dict[str, Any]]:
        """Parse a restaurant detail page."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract JSON-LD data
            json_ld = TabelogParser._extract_json_ld(soup)
            
            # Basic info section - handle both English and Japanese names
            name_container = soup.select_one('h2.display-name')
            if name_container:
                name_en = name_container.select_one('span').text.strip() if name_container.select_one('span') else None
                # Japanese name is in the alias span
                name_jp = name_container.find_next_sibling('span', class_='alias')
                name_jp = TabelogParser._clean_text(name_jp.text) if name_jp else None
            else:
                name_en = None
                name_jp = None
            
            # Rating and reviews
            try:
                rating_elem = soup.select_one('span.rdheader-rating__score-val-dtl')
                rating = float(rating_elem.text.strip()) if rating_elem else None
            except (ValueError, AttributeError):
                rating = None
            
            review_elem = soup.select_one('span.rdheader-rating__review-target')
            review_count = TabelogParser._extract_number(review_elem.text) if review_elem else 0
            
            # Extract location data
            address = city = region = latitude = longitude = None
            if json_ld:
                address, city, region, latitude, longitude = TabelogParser._extract_location_data(json_ld)
            
            if not address:
                # Fallback to HTML parsing for address
                address_elem = soup.select_one('p.rstinfo-table__address')
                if address_elem:
                    address = address_elem.text.strip()
            
            # Price ranges
            price_lunch = TabelogParser._extract_price_range(soup, "Lunch")
            price_dinner = TabelogParser._extract_price_range(soup, "Dinner")
            
            # Categories
            categories = []
            try:
                category_header = soup.find('th', text=re.compile('Categories', re.IGNORECASE))
                if category_header:
                    category_cell = category_header.find_next_sibling('td')
                    if category_cell:
                        categories = [cat.strip() for cat in category_cell.text.split(',')]
            except Exception as e:
                logger.error(f"Error extracting categories: {str(e)}")

            # Create restaurant data dictionary
            restaurant_data = {
                'name_en': name_en,
                'name_jp': name_jp,
                'rating': rating,
                'review_count': review_count,
                'address': address,
                'city': city,
                'region': region,
                'latitude': latitude,
                'longitude': longitude,
                'price_lunch': price_lunch,
                'price_dinner': price_dinner,
                'url': url,
                'categories': categories,
                'area': area
            }

            # Log successful parsing
            logger.debug(f"Successfully parsed restaurant: {name_en} ({name_jp})")
            logger.debug(f"Location: {city}, {region} ({latitude}, {longitude})")
            logger.debug(f"Price ranges - Lunch: {price_lunch or 'Not available'}, Dinner: {price_dinner or 'Not available'}")
            logger.debug(f"Categories: {', '.join(categories)}")
            return restaurant_data

        except Exception as e:
            logger.error(f"Error parsing restaurant page: {str(e)}")
            return None

    @staticmethod
    def extract_restaurant_urls(html: str) -> List[str]:
        """Extract restaurant URLs from a listing page."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            restaurant_links = soup.select('a.list-rst__rst-name-target')
            urls = [link['href'] for link in restaurant_links]
            logger.debug(f"Found {len(urls)} restaurant URLs")
            return urls
        except Exception as e:
            logger.error(f"Error extracting URLs: {str(e)}")
            return [] 