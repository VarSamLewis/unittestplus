from genericpath import isfile
import json
from pathlib import Path
import os


def _get_file_path(func: str) -> Path:
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


def _get_regression_file_path(func: str) -> Path:
    """
    Get the regression file path for the given function inside ./func/.
    """
    folder = Path.cwd() / "func"
    file_path = folder / f"{func}_regression.json"
    return file_path


def write_json(data, file_path = None):
    """
    Write a test entry to a JSON file named after the function_id in better_test/.
    If the file doesn't exist, create it with initial structure.
    If it does, append the new test entry to the "tests" array.
    """ 
    _create_folder()  # Ensure the folder exists
    #combined_key = f"{data['function']}_{data['function_id']}"
    if file_path is None:
        # If no file path is provided, derive it from the function name
        file_path = _get_file_path(data['function'])
    else:
        # Ensure the provided file path is a Path object
        file_path = Path(file_path)
    

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
	