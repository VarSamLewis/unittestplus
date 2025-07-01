from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from collections import Counter
from difflib import SequenceMatcher
from math import sqrt
import statistics as stats
import json

import core
from log_test import _get_file_path, _load_json



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


def _clear_tests(func: Union[str, Callable], confirm_callback: Optional[Callable[[], bool]] = None) -> None:
    """
    Clear all test entries for a function.
    """
    file_path: Path = _get_file_path(func)
    if not file_path.exists():
        print(f"No file found for function '{func}'.")
        return

    data: Dict[str, Any] = _load_json(file_path)
    data["tests"] = []

    if confirm_callback is None:
        confirm_callback = lambda: input("Are you sure you want to delete data? This CAN NOT be recovered. Type 'Yes' to continue: ") == "Yes"

    if confirm_callback():
        print("Continuing...")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"All tests cleared for function '{func}'.")
    else:
        print("Operation cancelled.")


def _delete_file(func: Union[str, Callable], confirm_callback: Optional[Callable[[], bool]] = None) -> None:
    """
    Delete the JSON file for a function.
    """
    file_path: Path = _get_file_path(func)
    if not file_path.exists():
        print(f"No file found for function '{func}'.")
        return

    if confirm_callback is None:
        confirm_callback = lambda: input("Are you sure you want to delete data? This CAN NOT be recovered. Type 'Yes' to continue: ") == "Yes"

    if confirm_callback():
        print("Continuing...")
        file_path.unlink()
        print(f"File '{file_path}' has been deleted successfully.")
    else:
        print("Operation cancelled.")


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


def compare_func_similarity(func: Union[str, Callable], display: bool = True) -> Optional[str]:
    """
    Return the testID of the most similar test definition to the most recent one.
    """
    file_path: Path = _get_file_path(func)
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
    file_path: Path = _get_file_path(func)
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


if __name__ == "__main__":

    def sum2int(int1: int, int2: int) -> int:
        return int1 + int2

    core.bettertest(sum2int, inputs=(20, 20), output=40, display=False)
    print(compare_func_similarity("sum2int"))
