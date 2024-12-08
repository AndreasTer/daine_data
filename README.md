# Tabelog Restaurant Data Scraper

A Python-based scraping tool to collect restaurant data from Tabelog (tabelog.com), a Japanese restaurant review website.

## Features

- Asynchronous scraping for high performance
- SQLite database storage
- Rate limiting and retry mechanisms
- Command-line interface
- Error handling and logging
- Progress tracking

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper with:
```bash
python main.py --city <city_name> --pages <number_of_pages>
```

Example:
```bash
python main.py --city tokyo --pages 10
```

## Data Collection

The scraper collects the following data points:
- Restaurant name (Japanese and English)
- Rating (0-5 scale)
- Number of reviews
- Address
- Price range (lunch and dinner)
- Restaurant URL
- Category/cuisine type
- Area/city

## Database Schema

The data is stored in SQLite with the following structure:
- restaurants table containing all collected data points
- Error logging table for tracking issues

## Error Handling

- Automatic retry (up to 3 times) for failed requests
- Comprehensive error logging
- Rate limiting to prevent IP blocks

## Performance

- Target processing speed: 100 restaurants per minute
- Concurrent page processing
- Automatic delay between requests

## Requirements

- Python 3.8+
- See requirements.txt for package dependencies 