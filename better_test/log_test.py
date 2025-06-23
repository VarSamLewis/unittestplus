from genericpath import isfile
import json
from pathlib import Path
import os


def _get_file_path(func_id):
	"""
	Get the file path for the given function ID.
	"""
	cwd = Path.cwd()

	file_path = f"{cwd}/better_test/{func_id}.json"
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

def write_json(data):
    """
    Write a test entry to a JSON file named after the function_id in better_test/.
    If the file doesn't exist, create it with initial structure.
    If it does, append the new test entry to the "tests" array.
    """
    file_path = _get_file_path(data['function_id'])

    if not _check_file_exists(file_path):
        # File doesn't exist — create new structure
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
	