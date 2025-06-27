import core
from log_test import _get_file_path, _load_json
from pprint import pprint

def _diff_json(test_1, test_2, path=""):
    diffs = []

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

def _filter_by_value(func,key, value):
    """
    Filter the test results for a function by a specified key and value.
    Returns a list of test entries where test[key] == value.
    """
    file_path = _get_file_path(func)
    if not file_path.exists():
        print(f"No file found for function '{func}'.")
        return []
    elif len(tests := _load_json(file_path).get("tests", [])) < 1:
        print(f"No file found for function '{func}'.")
        return []
    data = _load_json(file_path)
    tests = data.get("tests", [])
    filtered = [test for test in tests if test.get(key) == value]
    return filtered
    

def _clear_tests(func):
    """
    Clear all test entries for a function.
    """
    file_path = _get_file_path(func)
    if not file_path.exists():
        print(f"No file found for function '{func}'.")
        return
    data = _load_json(file_path)
    data["tests"] = []

    response = input("Are you sure you want to delete data? This CAN NOT be recovered. Type 'Yes' to continue: ")

    if response == "Yes":
        # Continue with the function
        print("Continuing...")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"All tests cleared for function '{func}'.")
    else:
        print("Operation cancelled.")
    return  # or exit the function
    

def _delete_file(func):
    """
    Delete the JSON file for a function.
    """
    file_path = _get_file_path(func)
    if not file_path.exists():
        print(f"No file found for function '{func}'.")
        return []

    response = input("Are you sure you want to delete data? This CAN NOT be recovered. Type 'Yes' to continue: ")

    if response == "Yes":
        # Continue with the function
        print("Continuing...")
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted successfully.")
    else:
        print("Operation cancelled.")
    return  # or exit the function


def compare_most_recent(func):
    """
    Compare the most recent two test entries for a function.
    """
    
    file_path = _get_file_path(func)  # Replace with your function ID
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

    def sum2int(int1, int2):
        int3 = int1 + int2
        return int3 

    core.bettertest(sum2int, inputs=(20, 20), output=40, display=False)
    
    diffs = compare_most_recent("sum2int")

    pprint(diffs)
