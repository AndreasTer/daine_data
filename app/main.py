# Import necessary libraries
import scraper
import database
import config

def main():
    # Load configuration
    try:
        config.load_config()
    except FileNotFoundError:
        print("Error: Configuration file not found. Please create config.py")
        return
    # Fetch and parse HTML content
    try:
        html_content = scraper.fetch_url(target_url)
        parsed_content = scraper.parse_html(html_content)
    except Exception as e:
        print(f"Error fetching or parsing HTML: {e}")
        return

    # Extract and save data
    try:
        database.save_data(db_connection, data, config.db_table)
    except Exception as e:
        print(f"Error saving data to database: {e}")
        return

    # Close database connection
    database.close_connection(db_connection)

    print("Scraping and data storage completed successfully!")


if __name__ == "__main__":
    main()

