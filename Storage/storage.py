# storage.py
import json
import os

DB_FILE = "database.json"

def save_database(data):
    """Save the entire DATABASE to JSON file."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_database():
    """Load DATABASE from file. If file doesn't exist, return empty DB."""
    if not os.path.exists(DB_FILE):
        return {
            "products": {},
            "partners": {},
            "saleorders": {}, 
            "invoices": {},
        }

    with open(DB_FILE, "r") as f:
        return json.load(f)
