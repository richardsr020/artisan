import json
import os

def save_print_config(file_path, password="123"):
    """
    Save PDF file path and password to printer.json
    Returns True if successful, False otherwise
    """
    # Validate inputs
    if not file_path:
        print("Error: No file path provided")
        return False
    
    if not file_path.lower().endswith('.pdf'):
        print("Error: Only PDF files are allowed")
        return False

    # Create config data
    config_data = {
        "file_path": file_path,
        "password": password
    }

    # Save to file
    try:
        with open("printer.json", "w") as f:
            json.dump(config_data, f, indent=4)
        print("Configuration saved successfully")
        return True
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        return False