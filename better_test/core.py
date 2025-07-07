import datetime
from os import error
import time
import tracemalloc
import json
import inspect
from pathlib import Path
import hashlib
import uuid
import logging
import re
from typing import Callable, Any, Optional, Dict, List, Tuple, Union

from log_test import write_json, _get_file_path, _load_json  # Use absolute import in real projects

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
KEY_TESTS = "tests"
KEY_TEST_ID = "test_id"
KEY_FUNCTION = "function"
KEY_FUNCTION_ID = "function_id"


def _execute_function(func: Callable, args: Optional[List[Any]] = None, kwargs: Optional[Dict[str, Any]] = None) -> Any:
    """Executes a function safely with given arguments."""
    if func is None:
        raise ValueError("Function cannot be None")

    args = args or []
    kwargs = kwargs or {}

    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise RuntimeError(f"Error executing function: {e}")


def _check_input_vs_output(output_actual: Any, output_target: Any, display: bool = True) -> Optional[bool]:
    """Compares actual vs expected output."""
    if output_actual == output_target:
        if display:
            logger.info("Function output matches expected value.")
        return True
    elif output_actual is None:
        if display:
            logger.warning("Function returned None.")
        return False
    else:
        if display:
            logger.warning(f"Output mismatch.\nExpected: {output_target}\nGot: {output_actual}")
        return False

def _gen_func_identity(func: Callable) -> Dict[str, str]:
    """Generates a hashed identity for a function."""
    if func is None:
        raise ValueError("Function cannot be None")

    try:
        full_id = f"{func.__module__}.{func.__name__}"
        func_hash = hashlib.md5(full_id.encode()).hexdigest()
        return {
            KEY_FUNCTION: func.__name__,
            KEY_FUNCTION_ID: func_hash
        }
    except Exception as e:
        raise RuntimeError(f"Error generating function identity: {e}")

def _gen_test_identity(func: Callable) -> int:
    """Generates a unique test identity. Doesn't increment but no errors"""
  
    file_path = _get_file_path(func.__name__)
    if not file_path.exists():
        logger.warning(f"No file found for function '{func.__name__}'.")
        return []
    max_val = float('-inf')
    data = _load_json(file_path)
    tests = data.get("tests", [])
    for test in tests:
        test_id = test.get(KEY_TEST_ID, [])
        if isinstance(test_id, int) and test_id > max_val:
            max_val = test_id

    return max_val + 1 if max_val != float('-inf') else 1

def _check_profile(func: Callable, args: Optional[List[Any]] = None, kwargs: Optional[Dict[str, Any]] = None
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
    lines = def_str.split('\n')
    filtered = [line for line in lines if not line.strip().startswith('#')]
    joined = ''.join(filtered)
    left_strip = joined.lstrip()
    definition = left_strip.rstrip()
    return definition 

def _add_custom_metrics(
    func: Callable,
    custom_metrics: Optional[Dict[str, Union[str, Callable[..., Any]]]],
    args: List[Any],
    kwargs: Dict[str, Any]
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

def bettertest(func: Callable,
               inputs: Optional[List[Any]] = None,
               kwargs: Optional[Dict[str, Any]] = None,
               expected_output: Any = None,
               display: bool = True,
               alias: str = None,
               message: str = None,
               custom_metrics: Optional[Dict[str, Union[str, Callable[..., Any]]]] = None) -> Dict[str, Any]:
    """
    Executes a function with test inputs, compares result to expected output, and logs execution info.
    """
    args = list(inputs) if inputs else []
    kwargs = kwargs or {}
    combined_inputs = {f"arg{i}": arg for i, arg in enumerate(args)}
    combined_inputs.update(kwargs)
    code = inspect.getsource(func)
    code_clean = _clean_definition(code)
    func_info = _gen_func_identity(func)
    test_id = _gen_test_identity(func)
    
    custom_metric_values = _add_custom_metrics(func, custom_metrics or {}, args, kwargs)

    try:
        output_actual, exec_time, mem_used = _check_profile(func, args=args, kwargs=kwargs)
        error = None
        error_message = None
    except Exception as e:
        output_actual = None
        exec_time = 0.0
        mem_used = 0.0
        error = True
        error_message = str(e)

    if error is None:
        _check_input_vs_output(output_actual, expected_output, display)

    log_entry = {
        KEY_FUNCTION: func_info[KEY_FUNCTION],
        KEY_FUNCTION_ID: func_info[KEY_FUNCTION_ID],
        "test": 
            {
            "test_id": test_id,
            "test_alias": alias,
            "test_message": message,
            "error": error,
            "error_message": error_message,
            "metrics": {
                "inputs": combined_inputs,
                "args": args,
                "kwargs": kwargs,
                "expected_output": expected_output,
                "actual_output": output_actual,
                "output_match": output_actual == expected_output,
                "execution_time_sec": round(exec_time, 3),
                "peak_memory_kb": round(mem_used, 3),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "custom_metrics": custom_metric_values
            },
            "definition": code_clean
            
        }
    }

    if display:
        logger.info(f"--- Running test for function `{func.__name__}` ---\n{json.dumps(log_entry, indent=2)}")


    write_json(log_entry)

    return log_entry


if __name__ == "__main__":
    pass