import json

db_config = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "your_database_name"
}

target_url = "https://www.example.com/target-page"
db_table = "scraped_data"

def load_config():
    global config
    try:
        config = json.load(db_config)

    except FileNotFoundError:
        print("Error: Configuration file not found. Please create config.json")
    except json.JSONDecodeError:
        print("Error: Invalid configuration file format. Please check config.json")
    return