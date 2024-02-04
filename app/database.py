import csv

def write_to_csv(list, name, path):
    """Exports list to csv"""
    # Prepare headers for your CSV file
    headers = list[0].keys() # Replace with your desired columns

    # Open the CSV file in write mode
    with open(path+ name + ".csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)

    # Write the header row
        writer.writeheader()

    # Write each restaurant data as a dictionary row
        for restaurant in list:
             # Convert restaurant data to a dictionary with matching header keys
            writer.writerow(restaurant)
        
        print("CSV file " + name + " created!")
        