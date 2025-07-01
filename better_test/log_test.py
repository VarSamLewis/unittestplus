import json
from pathlib import Path
from typing import Any, Dict, Optional


def _get_file_path(func_id: str) -> Path:
    """
    Get the file path for the given function ID inside ./func/.
    """
    folder = Path.cwd() / "func"
    file_path = folder / f"{func_id}.json"
    return file_path


def _check_file_exists(file_path: Path) -> bool:
    """
    Check if a file exists at the given path.
    """
    return file_path.is_file()


def _load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load a JSON file from the given path.
    """
    with file_path.open('r') as file:
        data = json.load(file)
    return data


def _create_folder() -> None:
    """
    Create the func folder in the current root if it doesn't exist.
    """
    folder_path = Path.cwd() / "func"
    folder_path.mkdir(parents=True, exist_ok=True)


def write_json(data: Dict[str, Any]) -> None:
    """
    Write a test entry to a JSON file named after the function_id in ./func/.
    If the file doesn't exist, create it with initial structure.
    If it does, append the new test entry to the "tests" array.
    """
    _create_folder()  # Ensure the folder exists
    file_path = _get_file_path(data['function'])

    if not _check_file_exists(file_path):
        # File doesn't exist — create new structure
        output_data: Dict[str, Any] = {
            "function": data["function"],
            "function_id": data["function_id"],
            "tests": [data["test"]],
        }
    else:
        # Load existing file and append new test
        output_data = _load_json(file_path)
        output_data["tests"].append(data["test"])

    # Write to disk
    with file_path.open('w') as file:
        json.dump(output_data, file, indent=4)


if __name__ == "__main__":
    pass
