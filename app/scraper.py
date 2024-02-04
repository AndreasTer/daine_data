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
    name_jp = parsed_content.find("small", class_="rd-header__rst-name-ja").get_text()
    category = parsed_content.find("span", property="v:category").get_text()
    r_id = parsed_content.find("a", class_="global-headbar__nav-target").get_attribute_list("href")[0].split('/')[-2]
    budget = parsed_content.find_all("b", class_="c-rating__val")[0].get_text()
    rating = parsed_content.find_all("b", class_="c-rating__val")[2].get_text()
    no_review = parsed_content.find("a", class_="gly-b-review").get_text().split('\n')[1]
    address = parsed_content.find("p", class_="rd-detail-info__rst-address").get_text().strip()
    url = parsed_content.find("a", class_="global-headbar__nav-target").get_attribute_list("href")[0]
    city = parsed_content.find("a", class_="global-headbar__nav-target").get_attribute_list("href")[0].split('/')[4].capitalize()

    restaurant = {
        'name': name_en,
        'name_jp': name_jp,
        'category': category,
        'r_id': r_id,
        'budget': budget,
        'rating': rating,
        'no_review': no_review,
        'address': address,
        'url': url,
        'city': city
    }
    return restaurant

def extract_list(parsed_content):
    """Extract restaurant info from one site.
    """

    list = []

    for link in parsed_content.find_all("a", class_='list-rst__name', href=True):
        full_url = requests.compat.urljoin(url, link["href"])
    # Extract title
    name_en = parsed_content.find("a", class_="rd-header__rst-name-main").get_text()

    return restaurant
