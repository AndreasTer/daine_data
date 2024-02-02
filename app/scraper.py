import requests
from bs4 import BeautifulSoup as soup

def fetch_url(url):
    """Fetches HTML content from a given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None


def parse_html(html_content):
    """Parses HTML content using BeautifulSoup."""
    return soup(html_content, "html.parser")


def extract_restaurant(parsed_content):
    """Extract restaurant info from one site.
    """
    # Extract title
    name_en = parsed_content.find("a", class_="rd-header__rst-name-main").get_text()
    category = parsed_content.find("span", property="v:category").get_text()
    print("Restaurant Name:", name_en)
    print("Category:", category)

    # Example: Extracting all article headlines
    #headlines = parsed_content.find_all("h2")
    #article_data = [headline.text.strip() for headline in headlines]
    return None
