import requests
from bs4 import BeautifulSoup

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
  return BeautifulSoup(html_content, "html.parser")

def extract_data(parsed_content):
  """Extracts desired data from parsed HTML content.

  Replace this placeholder with your specific data extraction logic.
  """
  # Example: Extracting all article headlines
  headlines = parsed_content.find_all("h2")
  article_data = [headline.text.strip() for headline in headlines]
  return article_data