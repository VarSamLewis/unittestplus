import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_file_path(func: str) -> Path:
    """
    Get the file path for the given function ID inside ./func/.
    """
    folder = Path.cwd() / "func"
    file_path = folder / f"{func}.json"
    logger.debug(f"Resolved file path for function '{func}': {file_path}")
    return file_path


def _check_file_exists(file_path):
    """
    Check if a file exists at the given path.
    """
    if isinstance(file_path, Path):
        exists = file_path.is_file()
    else:
        exists = Path(file_path).is_file()
    logger.debug(f"Checked existence for file '{file_path}': {exists}")
    return exists


def _load_json(file_path):
    """
    Load a JSON file from the given path.
    """
    logger.info(f"Loading JSON file: {file_path}")
    with open(file_path, "r") as file:
        data = json.load(file)
    logger.debug(f"Loaded data from '{file_path}': {data}")
    return data


def _create_folder():
    """
    Create the func folder in the current root if it doesn't exist.
    """
    folder_path = Path.cwd() / "func"
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created folder: {folder_path}")
    else:
        logger.debug(f"Folder already exists: {folder_path}")


def _get_regression_file_path(func: str) -> Path:
    """
    Get the regression file path for the given function inside ./func/.
    """
    folder = Path.cwd() / "func"
    file_path = folder / f"{func}_regression.json"
    logger.debug(f"Resolved regression file path for function '{func}': {file_path}")
    return file_path


def write_json(data, file_path=None):
    """
    Write a test entry to a JSON file named after the function_id in better_test/.
    If the file doesn't exist, create it with initial structure.
    If it does, append the new test entry to the "tests" array.
    """
    _create_folder()
    if file_path is None:
        file_path = _get_file_path(data["function"])
    else:
        file_path = Path(file_path)

    if not _check_file_exists(file_path):
        logger.info(f"File '{file_path}' does not exist. Creating new test log.")
        output_data = {
            "function": data["function"],
            "function_id": data["function_id"],
            "tests": [data["test"]],
        }
    else:
        logger.info(f"File '{file_path}' exists. Appending new test entry.")
        output_data = _load_json(file_path)
        output_data["tests"].append(data["test"])

    with open(file_path, "w") as file:
        json.dump(output_data, file, indent=4)
        logger.info(f"Wrote test log to '{file_path}'")


if __name__ == "__main__":
    pass
