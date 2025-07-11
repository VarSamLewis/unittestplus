from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from collections import Counter
from difflib import SequenceMatcher
from math import sqrt
import statistics as stats
import json
from pprint import pprint
import logging
from log_test import write_json
from core import KEY_TESTS, KEY_TEST_ID
from log_test import _get_file_path, _load_json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------HELPER FUNCTIONS-------------------------------------------
def _diff_json(test_1: Dict[str, Any], test_2: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
    diffs: List[Dict[str, Any]] = []

    keys_a = set(test_1.keys())
    keys_b = set(test_2.keys())

    for key in keys_a - keys_b:
        diffs.append({"type": "removed", "path": f"{path}.{key}".lstrip("."), "value": test_1[key]})

    for key in keys_b - keys_a:
        diffs.append({"type": "added", "path": f"{path}.{key}".lstrip("."), "value": test_2[key]})

    for key in keys_a & keys_b:
        val_a = test_1[key]
        val_b = test_2[key]
        current_path = f"{path}.{key}".lstrip(".")

        if isinstance(val_a, dict) and isinstance(val_b, dict):
            diffs.extend(_diff_json(val_a, val_b, path=current_path))
        elif val_a != val_b:
            diffs.append({"type": "changed", "path": current_path, "old_value": val_a, "new_value": val_b})

    return diffs

def _similarity_score(s1: str, s2: str) -> List[List[float]]:
    """
    Calculate multiple similarity scores between two strings.
    """
    # SequenceMatcher similarity
    score_1: float = SequenceMatcher(None, s1, s2).ratio()

    # Jaccard similarity
    set1, set2 = set(s1), set(s2)
    score_2: float = len(set1 & set2) / len(set1 | set2)

    # Cosine similarity
    vec1, vec2 = Counter(s1), Counter(s2)
    dot_product = sum(vec1[ch] * vec2[ch] for ch in vec1)
    magnitude1 = sqrt(sum(count ** 2 for count in vec1.values()))
    magnitude2 = sqrt(sum(count ** 2 for count in vec2.values()))
    score_3 = dot_product / (magnitude1 * magnitude2)

    return [[score_1, score_2, score_3]]

# -------------------------------------------MAIN FUNCTIONS-------------------------------------------
def clear_tests(func: Union[str, Callable], confirm_callback: Optional[Callable[[], bool]] = None) -> None:
    """
    Clear all test entries for a function.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        print(f"No file found for function '{func.__name__}'.")
        return

    data: Dict[str, Any] = _load_json(file_path)
    data["tests"] = []

    if confirm_callback is None:
        confirm_callback = lambda: input("Are you sure you want to delete data? This CAN NOT be recovered. Type 'Yes' to continue: ") == "Yes"

    if confirm_callback():
        print("Continuing...")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"All tests cleared for function '{func.__name__}'.")
    else:
        print("Operation cancelled.")


def delete_file(func: Union[str, Callable], confirm_callback: Optional[Callable[[], bool]] = None) -> None:
    """
    Delete the JSON file for a function.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        print(f"No file found for function '{func.__name__}'.")
        return

    if confirm_callback is None:
        confirm_callback = lambda: input("Are you sure you want to delete data? This CAN NOT be recovered. Type 'Yes' to continue: ") == "Yes"

    if confirm_callback():
        print("Continuing...")
        file_path.unlink()
        print(f"File '{file_path}' has been deleted successfully.")
    else:
        print("Operation cancelled.")


def update_alias(func: Callable, alias: str, test_id: int) -> str:
    """
    Assigns an alias to a test by modifying the existing JSON file.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return ""

    data = _load_json(file_path)
    tests = data.get("tests", [])

    for test in tests:
        if test.get("test_id") == test_id:
            test["test_alias"] = alias
            break
    else:
        logger.warning(f"No test with ID {test_id} found.")
        return ""

    # Save updated data back to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    return alias


def update_message(func: Callable, message: str, test_id: int) -> str:
    """
    Assigns a message to a test by modifying the existing JSON file.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return ""

    data = _load_json(file_path)
    tests = data.get("tests", [])

    for test in tests:
        if test.get("test_id") == test_id:
            test["test_message"] = message
            break
    else:
        logger.warning(f"No test with ID {test_id} found.")
        return ""

    # Save updated data back to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    return message

def get_testid(func: Union[str, Callable], alias: str) -> int:
    """
    Returns the testID of a test by its alias.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return -1
    data = _load_json(file_path)
    tests = data.get("tests", [])
    for test in tests:
        if test.get("test_alias") == alias:
            return test.get(KEY_TEST_ID, -1)
    logger.warning(f"No test with alias '{alias}' found.")
    return -1

def rank_test_by_value(func: Callable, key: str) -> List[Dict[str, Any]]:
    """Ranks previous tests by a given numeric key (descending)."""
    file_path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return []

    tests = _load_json(file_path).get(KEY_TESTS, [])
    return sorted(tests, key=lambda x: x.get(key, 0), reverse=True)

def get_previous_test_definition(func: Callable, test_id: int = None, alias: str = None):
    """
    Returns the definition of a previous test by its index.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return ""

    data = _load_json(file_path)
    tests = data.get("tests", [])
    
    if alias is None:
        # If no alias is provided, search by test_id
        for test in tests:
            if test.get(KEY_TEST_ID) == test_id:
                return test.get("definition", "")
    else:
        # If alias is provided, find the test_id first
        test_id = get_testid(func, alias)
        if test_id == -1:
            logger.warning(f"No test with alias '{alias}' found.")
            return ""
        for test in tests:
            if test.get(KEY_TEST_ID) == test_id:
                return test.get("definition", "")
    return logging.error(f"No test found with testid or alias")


def filter_test_by_value(func: Callable, key: str, value: Any) -> List[Dict[str, Any]]:
    """Filters previous test results by a specific key/value pair."""
    file_path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func}'.")
        return []

    data = _load_json(file_path)
    tests = data.get(KEY_TESTS, [])
    return [test for test in tests if test.get(key) == value]

def compare_func_similarity(func: Union[str, Callable], display: bool = True) -> Optional[str]:
    """
    Return the testID of the most similar test definition to the most recent one.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        print(f"No file found for function '{func}'.")
        return None

    data = _load_json(file_path)
    tests = data.get("tests", [])
    if len(tests) < 2:
        print("Not enough test entries to compare.")
        return None

    latest_test = tests[-1]
    definition_1 = latest_test.get("definition", "")
    prev_tests = tests[:-1]

    similarity_results: List[Tuple[str, float, List[List[float]]]] = []
    for test in prev_tests:
        definition_2 = test.get("definition", "")
        scores = _similarity_score(definition_1, definition_2)
        median_score = stats.median(scores[0])
        similarity_results.append((test.get("testID"), median_score, scores))

    best_match = max(similarity_results, key=lambda x: x[1])

    if display:
        print(f"Best match similarity scores: {best_match[2]}")

    return best_match[0]


def compare_most_recent(func: Union[str, Callable]) -> List[Dict[str, Any]]:
    """
    Compare the most recent two test entries for a function.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        print("No tests found for this function.")
        return []

    data = _load_json(file_path)
    tests = data.get("tests", [])
    if len(tests) < 2:
        print("Not enough test entries to compare.")
        return []

    test_1 = tests[-1]
    test_2 = tests[-2]
    return _diff_json(test_1, test_2)


def get_test(func: Union[str, Callable],  test_id: int = None, alias: str = None, display: bool =True):
    """
    Returns a specific test entry by its ID or alias.
    """
    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return None

    data = _load_json(file_path)
    tests = data.get("tests", [])
    test_instance: Optional[Dict[str, Any]] = None
    
    if alias is not None:
        test_id = get_testid(func, alias)

    if test_id is not None:
        for test in tests:
            if test.get(KEY_TEST_ID) == test_id:
                #pprint(test, indent=4)
                test_instance = test
                #return test
                break
    else:
        logger.error("Either test_id or alias must be provided.")
        return None

    if test_instance and display:
        logger.info(f"--- Test `{test_id}` ---\n{json.dumps(test, indent=2)}")


if __name__ == "__main__":
    pass
