from genericpath import isfile
import json
from pathlib import Path
import os


def _get_file_path(func):
    """
    Get the file path for the given function ID inside ./func/.
    """
    folder = Path.cwd() / "func"
    file_path = folder / f"{func}.json"
    return file_path

def _check_file_exists(file_path):
	"""
	Check if a file exists at the given path.
	"""

	return isfile(file_path)


def _load_json(file_path):
	"""
	Load a JSON file from the given path.
	"""
	with open(file_path, 'r') as file:
		data = json.load(file)
	return data

def _create_folder():
    """
    Create the func folder in the current root if it doesn't exist.
    """
    folder_path = Path.cwd() / "func"
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

def write_json(data):
    """
    Write a test entry to a JSON file named after the function_id in better_test/.
    If the file doesn't exist, create it with initial structure.
    If it does, append the new test entry to the "tests" array.
    """
    _create_folder()  # Ensure the folder exists
    combined_key = f"{data['function']}_{data['function_id']}"
    file_path = _get_file_path(combined_key)
    

    if not _check_file_exists(file_path):
        # File doesn't exist � create new structure
        output_data = {
            "function": data["function"],
            "function_id": data["function_id"],
            "tests": [data["test"]]
        }
    else:
        # Load existing file and append new test
        output_data = _load_json(file_path)
        output_data["tests"].append(data["test"])

    # Write to disk
    with open(file_path, 'w') as file:
        json.dump(output_data, file, indent=4)



if __name__ == "__main__":
    pass
	