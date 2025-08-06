from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from collections import Counter
from difflib import SequenceMatcher
from math import sqrt
import statistics as stats
import json
import logging
from core import KEY_TESTS, KEY_TEST_ID
from log_test import _get_file_path, _load_json, _get_regression_file_path, _check_file_exists, _create_folder
from core import unittestplus
from contextlib import contextmanager
import ast
import inspect


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

@contextmanager
def _custom_output_path(path):
    original_get_file_path = globals().get('get_file_path')
    globals()['get_file_path'] = lambda x: Path(path)
    try:
        yield
    finally:
        if original_get_file_path:
            globals()['get_file_path'] = original_get_file_path

def _clean_and_format_definition(definition: str) -> str:
    """
    Clean and format a function definition string to fix common issues.
    Specifically handles the format with spaces instead of newlines.
    """
    if not definition.strip():
        raise ValueError("Empty function definition")
    
    cleaned = definition.replace('\\"', '"').replace("\\'", "'")
    

    if '\n' not in cleaned:
        parts = []
        current_part = ""
        i = 0
        
        while i < len(cleaned):

            if cleaned[i:i+8] == '        ': 
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
                i += 8
                # Skip any additional spaces
                while i < len(cleaned) and cleaned[i] == ' ':
                    i += 1
            elif cleaned[i:i+12] == '            ':  # 12 spaces = deeper indentation
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
                i += 12
                # Skip any additional spaces
                while i < len(cleaned) and cleaned[i] == ' ':
                    i += 1
            else:
                current_part += cleaned[i]
                i += 1

        if current_part.strip():
            parts.append(current_part.strip())
        

        if parts:
            formatted_lines = []
            
            # First part should be the function definition
            if parts[0].startswith('def '):
                formatted_lines.append(parts[0])
                
                # Process remaining parts
                for part in parts[1:]:
                    if part.startswith('if ') or part.startswith('elif ') or part.startswith('else:') or \
                       part.startswith('for ') or part.startswith('while ') or part.startswith('try:') or \
                       part.startswith('except ') or part.startswith('finally:'):
                        # Control structure - base indentation
                        formatted_lines.append('    ' + part)
                    elif part.startswith('return ') or part.startswith('raise ') or part.startswith('pass'):
                        if formatted_lines and any(formatted_lines[-1].strip().startswith(kw) for kw in ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except ', 'finally:']):
                            # This should be indented further (nested under control structure)
                            formatted_lines.append('        ' + part)
                        else:
                            # This is at function body level
                            formatted_lines.append('    ' + part)
                    else:
                        # Default to function body indentation
                        formatted_lines.append('    ' + part)
            
            cleaned = '\n'.join(formatted_lines)
    
    return cleaned


def _rebuild_function_from_definition(definition: str, func_name: str):
    """
    Rebuild a function from its string definition with proper error handling.
    """
    try:
        # Clean up the definition string
        cleaned_definition = _clean_and_format_definition(definition)
        
        # Debug: print the cleaned definition
        print(f"Debug - Cleaned definition for {func_name}:")
        print(repr(cleaned_definition))
        print("Formatted:")
        print(cleaned_definition)
        print("-" * 50)
        
        # Create namespace for execution
        namespace = {}
        
        # Execute the function definition
        exec(cleaned_definition, namespace)
        
        # Return the function
        if func_name in namespace:
            return namespace[func_name]
        else:
            raise ValueError(f"Function '{func_name}' not found in definition")
            
    except SyntaxError as e:
        raise SyntaxError(f"Invalid function definition for '{func_name}': {e}")
    except Exception as e:
        raise RuntimeError(f"Error rebuilding function '{func_name}': {e}")


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

def compare_io(func: Union[str, Callable],  test_id_1: int ,  test_id_2: int ) -> Optional[str]:
    """
    Compare inputs and outputs of two test entries by their IDs.
    """

    file_path: Path = _get_file_path(func.__name__)
    if not file_path.exists():
        print("No tests found for this function.")
        return None

    data = _load_json(file_path)
    tests = data.get("tests", [])
    if len(tests) < 2:
        print("Not enough test entries to compare.")
        return None

    input_1 = output_1 = input_2 = output_2 = None
    for test in tests:
            if test.get(KEY_TEST_ID) == test_id_1:
                input_1 = test.get("inputs", {})
                output_1 = test.get("actual_output", {})

            if test.get(KEY_TEST_ID) == test_id_2:
                    input_2 = test.get("inputs", {})
                    output_2 = test.get("actual_output", {})

            if input_1 is not None and input_2 is not None:
                break

    if input_1 == input_2 and output_1 == output_2:
        print("Inputs and outputs are identical.")

    elif input_1 == input_2 and output_1 != output_2:
        print("Inputs are identical, but outputs differ.")

    elif input_1 != input_2 and output_1 == output_2:
        print("Inputs are different, but outputs are identical.")

    else:
        print("Inputs and outputs are different.")
    
    return input_1, input_2, output_1, output_2


def run_regression(func: str, inputs: List[Any], file_path: str = None, display :bool = True) -> Dict[str, Any]:
    """
    Run regression tests for a specific function using provided inputs.
    Tests the inputs against all existing test cases stored in the function's test file.
    
    Args:
        func: Name of the function to test
        inputs: List of input sets to test with
        file_path: Optional path to regression file. Defaults to {func}_regression.json
    
    Returns:
        Dictionary containing regression test results
    """
    # Initialize variables at function scope to avoid UnboundLocalError
    test_func = None
    regression_file_path = None
    existing_test_cases = []
    test_data = None
    
    try:
        # Get the function's original test file to load the function definition
        func_test_file = _get_file_path(func)
    
        if not _check_file_exists(func_test_file):
            raise FileNotFoundError(f"Function test file not found: {func_test_file}")
    
        # Load function definition
        test_data = _load_json(func_test_file)
    
        if not test_data.get('tests') or not test_data['tests']:
            raise ValueError(f"No tests found in {func_test_file}")
    
        # Get function definition from first test
        first_test = test_data['tests'][0]
        if 'definition' not in first_test:
            raise ValueError(f"No function definition found in {func_test_file}")
    
        definition = first_test['definition']
        test_func = _rebuild_function_from_definition(definition, func)
    
        # Determine regression file path
        if file_path is None:
            regression_file_path = _get_regression_file_path(func)
        else:
            regression_file_path = Path(file_path)
            
    except Exception as e:
        # Fixed logging error - use proper string formatting
        logger.error("Error loading function definition: %s", str(e))
        return {
            'function': func,
            'error': f"Failed to load function definition: {str(e)}",
            'success': False
        }

    try:
        # Get all existing tests from the original test file
        for test in test_data['tests']:
            test_case = {
                'test_id': test['test_id'],
                'args': test['metrics']['args'],
                'kwargs': test['metrics']['kwargs'],
                'expected_output': test['metrics']['expected_output']
            }
            existing_test_cases.append(test_case)
    
        # Run user inputs with all existing test cases
        regression_results = {
            'function': func,
            'user_inputs': len(inputs),
            'existing_tests': len(existing_test_cases),
            'total_combinations': len(inputs) * len(existing_test_cases),
            'results': []
        }
    
        result_id = 1
        
    except Exception as e:
        # Fixed logging error
        logger.error("Error processing test cases: %s", str(e))
        return {
            'function': func,
            'error': f"Failed to process test cases: {str(e)}",
            'success': False
        }

    # For each user input
    for input_idx, user_input in enumerate(inputs):
        # Prepare user input
        if isinstance(user_input, (list, tuple)):
            user_args = list(user_input)
            user_kwargs = {}
        elif isinstance(user_input, dict):
            user_args = user_input.get('args', [])
            user_kwargs = user_input.get('kwargs', {})
        else:
            user_args = [user_input]
            user_kwargs = {}
        
        # Test this user input against each existing test case
        for test_case in existing_test_cases:
            try:
                # Run with user input
                user_output = test_func(*user_args, **user_kwargs)
                
                # Run with original test case
                original_output = test_func(*test_case['args'], **test_case['kwargs'])
                
                # Compare outputs
                outputs_match = user_output == original_output
                expected_match = user_output == test_case['expected_output']
                
                result = {
                    'result_id': result_id,
                    'user_input_index': input_idx + 1,
                    'original_test_id': test_case['test_id'],
                    'user_input': {
                        'args': user_args,
                        'kwargs': user_kwargs
                    },
                    'original_test': {
                        'args': test_case['args'],
                        'kwargs': test_case['kwargs'],
                        'expected_output': test_case['expected_output']
                    },
                    'outputs': {
                        'user_output': user_output,
                        'original_output': original_output
                    },
                    'comparisons': {
                        'user_vs_original': outputs_match,
                        'user_vs_expected': expected_match
                    },
                    'success': True,
                    'error': None
                }
                
            except Exception as e:
                result = {
                    'result_id': result_id,
                    'user_input_index': input_idx + 1,
                    'original_test_id': test_case['test_id'],
                    'user_input': {
                        'args': user_args,
                        'kwargs': user_kwargs
                    },
                    'original_test': {
                        'args': test_case['args'],
                        'kwargs': test_case['kwargs'],
                        'expected_output': test_case['expected_output']
                    },
                    'success': False,
                    'error': str(e)
                }
            
            regression_results['results'].append(result)
            result_id += 1
    
    # Save regression results (only if we have a valid path)
    if regression_file_path:
        try:
            _create_folder()
            with open(regression_file_path, 'w') as f:
                json.dump(regression_results, f, indent=4)
        except Exception as e:
            logger.error("Error saving regression results: %s", str(e))
    
    # Calculate summary stats
    successful_results = [r for r in regression_results['results'] if r['success']]
    
    summary = {
            'function': func,
            'total_combinations': len(regression_results['results']),
            'successful_runs': len(successful_results),
            'errors': len(regression_results['results']) - len(successful_results),
            'user_vs_original_matches': len([r for r in successful_results if r['comparisons']['user_vs_original']]),
            'user_vs_expected_matches': len([r for r in successful_results if r['comparisons']['user_vs_expected']])
        }

    if display:
        print(json.dumps(summary, indent=2))

    
    return summary


if __name__ == "__main__":
    pass
