import datetime
import hashlib
import inspect
import json
import logging
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .log_test import _get_file_path, _load_json, write_json
from .manipulate import _rebuild_function_from_definition
from .serialise import safe_serialise
from .utils import set_unittestplus_log_level

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
KEY_TESTS = "tests"
KEY_TEST_ID = "test_id"
KEY_FUNCTION = "function"
KEY_FUNCTION_ID = "function_id"


def _get_func_name(func: Union[str, Callable]) -> str:
    return func if isinstance(func, str) else func.__name__


def _execute_function(
    func: Callable,
    args: Optional[List[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
) -> Any:
    """Executes a function safely with given arguments."""
    if func is None:
        raise ValueError("Function cannot be None")

    args = args or []
    kwargs = kwargs or {}

    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise RuntimeError(f"Error executing function: {e}")


def _gen_func_identity(func: Callable) -> Dict[str, str]:
    """Generates a hashed identity for a function."""
    if func is None:
        raise ValueError("Function cannot be None")

    try:
        full_id = f"{func.__module__}.{func.__name__}"
        func_hash = hashlib.md5(full_id.encode()).hexdigest()
        return {KEY_FUNCTION: func.__name__, KEY_FUNCTION_ID: func_hash}
    except Exception as e:
        raise RuntimeError(f"Error generating function identity: {e}")


def _gen_test_identity(func: Callable) -> int:
    """Generates a unique test identity. Doesn't increment but no errors"""
    file_path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return 1  # Return int, not list
    max_val = float("-inf")
    data = _load_json(file_path)
    tests = data.get("tests", [])
    for test in tests:
        test_id = test.get(KEY_TEST_ID, None)
        if isinstance(test_id, int) and test_id > max_val:
            max_val = test_id

    return int(max_val + 1) if max_val != float("-inf") else 1


def _check_profile(
    func: Callable,
    args: Optional[List[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[Any, float, float]:
    """Profiles function execution time and peak memory usage."""
    args = args or []
    kwargs = kwargs or {}

    tracemalloc.start()
    start_time = time.perf_counter()

    result = func(*args, **kwargs)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_time = end_time - start_time
    memory_used_kb = peak / 1024

    return result, elapsed_time, memory_used_kb


def _clean_definition(def_str: str) -> str:
    """Cleans source code by removing comments and whitespace."""
    lines = def_str.split("\n")
    filtered = [
        line.rstrip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]
    definition = "\n".join(filtered)
    return definition


def _add_custom_metrics(
    func: Callable,
    custom_metrics: Optional[Dict[str, Union[str, Callable[..., Any]]]],
    args: List[Any],
    kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluates user-defined custom metrics using the provided function, args, and kwargs.

    Returns a dictionary of metric_name: result.
    If custom_metrics is None or empty, returns an empty dictionary.
    """
    if not custom_metrics:
        return {}

    results: Dict[str, Any] = {}

    for name, metric in custom_metrics.items():
        try:
            if isinstance(metric, str):
                context = {
                    "func": func,
                    "args": args,
                    "kwargs": kwargs,
                }
                results[name] = eval(metric, {}, context)
            elif callable(metric):
                results[name] = metric(func=func, args=args, kwargs=kwargs)
            else:
                results[name] = f"[Invalid metric type: {type(metric)}]"
        except Exception as e:
            results[name] = f"[Error evaluating metric: {str(e)}]"

    return results


def _compare_outputs(a: Any, b: Any, max_items: int = 3) -> bool:
    try:
        # If either is None but not both, return False
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False

        # Check exact type match first to avoid ambiguous equality
        if not isinstance(a, type(b)):
            return False

        else:
            a_ser = safe_serialise(a, max_items)
            b_ser = safe_serialise(b, max_items)

            if a_ser == b_ser:
                return True

            print("Mismatch found:")
            if isinstance(a_ser, dict) and isinstance(b_ser, dict):
                for key in set(a_ser.keys()).union(b_ser.keys()):
                    val_a = a_ser.get(key, "<missing>")
                    val_b = b_ser.get(key, "<missing>")
                    if val_a != val_b:
                        print(f" - Key '{key}': {val_a} ≠ {val_b}")
                        logger.warning(
                            f"""Outputs do not match:\n
                            Expected: {a_ser}\n
                            Actual: {b_ser}
                            """
                        )
                return False
            else:
                print(f"Expected: {a_ser}, Actual: {b_ser}")
                logger.warning(
                    f"Outputs do not match: Expected: {a_ser}, Actu al: {b_ser}"
                )
                return False
    except Exception as e:
        logger.error(f"Error comparing outputs: {e}")
        return False


def _simple_assert(assert_type: str, output: Any, assert_value: Any = None) -> bool:
    """Performs a simple assertion based on assert_type."""
    if assert_type == "equals":
        return output == assert_value
    elif assert_type == "not_equals":
        return output != assert_value
    elif assert_type == "greater_than":
        return output > assert_value
    elif assert_type == "less_than":
        return output < assert_value
    elif assert_type == "not_none":
        return output is not None
    elif assert_type == "is_none":
        return output is None
    elif assert_type == "in":
        return output in assert_value
    elif assert_type == "not_in":
        return output not in assert_value
    else:
        raise ValueError(f"Unknown assert_type: {assert_type}")


def unittestplus(
    func: Callable[..., Any],
    inputs: Optional[Union[List[Any], Tuple[Any, ...]]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    expected_output: Any = None,
    display: bool = True,
    alias: Optional[str] = None,
    message: Optional[str] = None,
    custom_metrics: Optional[Dict[str, Union[str, Callable[..., Any]]]] = None,
    assertion: Optional[Dict[str, Any]] = None,
    verbose: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Executes a function with test inputs, compares result to expected output,
    and logs execution info.
    """

    set_unittestplus_log_level(logging.INFO if verbose else logging.ERROR)

    if inputs is None:
        args = []
    elif isinstance(inputs, (list, tuple)):
        args = list(inputs)
    else:
        args = [inputs]

    original_definition = None

    if isinstance(func, str):
        file_path: Path = _get_file_path(func)
        func_name = func
    else:
        file_path = _get_file_path(func.__name__)
        func_name = func.__name__

    if not file_path.exists():
        # Create a new test file with an empty tests list
        initial_data: Dict[str, List[Any]] = {"tests": []}
        with open(file_path, "w") as f:
            json.dump(initial_data, f, indent=4)
        data = initial_data
        tests = []
    else:
        data = _load_json(file_path)
        tests = data.get("tests", [])
        if len(tests) == 0:
            logger.error("No function definition provided")
            return None

        latest_test = tests[-1]
        original_definition = latest_test.get("definition", "")
        func = _rebuild_function_from_definition(original_definition, func_name)

    kwargs = kwargs or {}
    # Serialize all inputs and outputs for logging
    combined_inputs = {f"arg{i}": safe_serialise(arg) for i, arg in enumerate(args)}
    combined_inputs.update({k: safe_serialise(v) for k, v in kwargs.items()})

    # Use original definition if we have it, otherwise try to get source
    if original_definition:
        code_clean = original_definition
    else:
        try:
            code = inspect.getsource(func)
            code_clean = _clean_definition(code)
        except OSError:
            # If we can't get the source (dynamically created function), use repr
            code_clean = f"# Dynamically created function\n{func.__name__}"
    func_info = _gen_func_identity(func)
    test_id = _gen_test_identity(func)

    custom_metric_values = _add_custom_metrics(func, custom_metrics or {}, args, kwargs)

    try:
        output_actual, exec_time, mem_used = _check_profile(
            func, args=args, kwargs=kwargs
        )
        error = None
        error_message = None

        assertion_passed = None
        if assertion:
            if "type" not in assertion:
                raise ValueError("If using 'assertion', it must include a 'type' key.")

            assert_type = assertion["type"]
            assert_value = assertion.get("value")
            try:
                assertion_passed = _simple_assert(
                    assert_type, output_actual, assert_value
                )
                if assertion_passed:
                    logger.debug(
                        f"Assertion passed: {assert_type} for output: {output_actual}"
                    )
                else:
                    logger.warning(
                        f"Assertion failed: {assert_type} for output: {output_actual}"
                    )
            except Exception:
                assertion_passed = False

    except Exception as e:
        output_actual = None
        exec_time = 0.0
        mem_used = 0.0
        error = True
        error_message = str(e)
        assertion_passed = None

    log_entry: Dict[str, Any] = {
        KEY_FUNCTION: func_info[KEY_FUNCTION],
        KEY_FUNCTION_ID: func_info[KEY_FUNCTION_ID],
        "test": {
            "test_id": test_id,
            "test_alias": alias,
            "test_message": message,
            "error": error,
            "error_message": error_message,
            "metrics": {
                "inputs": combined_inputs,
                "args": [safe_serialise(a) for a in args],
                "kwargs": {k: safe_serialise(v) for k, v in kwargs.items()},
                "expected_output": safe_serialise(expected_output),
                "actual_output": safe_serialise(output_actual),
                "output_match": _compare_outputs(output_actual, expected_output),
                "assertion": assertion,
                "assertion_passed": assertion_passed,
                "execution_time_sec": round(exec_time, 3),
                "peak_memory_kb": round(mem_used, 3),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "custom_metrics": custom_metric_values,
            },
            "definition": code_clean,
        },
    }

    if display and verbose:
        test = log_entry["test"]
        logger.debug(
            f"Test run: function='{func.__name__}', test_id={test['test_id']}, "
            f"output={test['metrics']['actual_output']}, error={test['error']}"
        )

    write_json(log_entry)

    return log_entry


if __name__ == "__main__":

    def example_func(x, y):
        return x + y

    unittestplus(
        func=example_func,
        inputs=[2, 3],
        expected_output=5,
        alias="Addition test",
        message="Basic addition check",
        assertion={"type": "equals", "value": 5},
        display=True,
    )
