import datetime
import time
import tracemalloc
import pprint
import json
import inspect
import hashlib
import uuid
from log_test import write_json


def _execute_function(func, args=None, kwargs=None):
    if func is None:
        raise ValueError("Function cannot be None")
    else:
        args = args or []
        kwargs = kwargs or {}

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            raise RuntimeError(f"An error occurred while executing the function: {e}")

def _check_inputVoutput(output_actual, output_target, display = True):
    if output_actual == output_target:
        if display == True:
            print("Function output matches expected value.")
        else:
            return True
    elif output_actual is None:
        if display == True:
            print("Function returned None.")
        else:
            return False
    else:
        if display == True:
            print(f"Output is different.\nExpected: {output_target}\nGot: {output_actual}")
        else:
            return False
        

def _func_Identity(func):
    if func is None:
        raise ValueError("Function cannot be None")

    try:
        # Source code and qualified name provide a good fingerprint
        func_name = func.__name__
        func_module = func.__module__
        full_id = f"{func_module}.{func_name}"

        # Create a short unique hash
        func_hash = hashlib.md5(full_id.encode()).hexdigest()

        return {
            "function": func_name,
            "function_id": func_hash
        }
    except Exception as e:
        raise RuntimeError(f"Error generating function identity: {e}")


def _test_Indenity(func, assign_id = False, ID = 0):
    """
    if func is None:
        raise ValueError("Function cannot be None")
    else:
        return f"{func}_{uuid.uuid4().hex}"
    """
    if func is None:
        raise ValueError("Function cannot be None")
    else:
        base_string = f"{func.__module__}.{func.__name__}.{uuid.uuid4()}"
        return int(hashlib.md5(base_string.encode()).hexdigest(), 16)


def _checkProfile(func, args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}

    tracemalloc.start()
    start_time = time.perf_counter()

    result = func(*args, **kwargs)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_time = end_time - start_time
    memory_used = peak / 1024  # Convert bytes to kilobytes

    return result, elapsed_time, memory_used

def bettertest(func, inputs=None, kwargs=None, output=None, display=True):
    """
    Executes a function with test inputs, compares result to expected output, logs the result including timing and memory.
    """

    args = list(inputs) if inputs else []
    kwargs = kwargs or {}

    combined_inputs = {f"arg{i}": arg for i, arg in enumerate(args)}
    combined_inputs.update(kwargs)

    code = inspect.getsource(func)
    func_info = _func_Identity(func)
    test_id = _test_Indenity(func)

    try:
        output_actual, exec_time, mem_used = _checkProfile(func, args=args, kwargs=kwargs)
        error = None
        error_message = None
    except Exception as e:
        output_actual = None
        exec_time = 0
        mem_used = 0
        error = True
        error_message = str(e)

    # Only check output if there was no error
    if error is None:
        _check_inputVoutput(output_actual, output)


    log_entry = {
        "function": func_info["function"],
        "function_id": func_info["function_id"],
        "test": {
            "test_id": test_id,
            "error": error,
            "error_message":error_message,
            "metrics": {
                "inputs": combined_inputs,
                "args": args,
                "kwargs": kwargs,
                "expected_output": output,
                "actual_output": output_actual,
                "output_match": output_actual == output,
                "execution_time_sec": round(exec_time, 3),
                "peak_memory_kb": mem_used,
                "timestamp": datetime.datetime.utcnow().isoformat()
            },
            "definition": code
        }
    }


    if display == True:
        print(f"\n--- Running test for function `{func.__name__}` ---")
        print(json.dumps(log_entry, indent=2))
    else:
        None

    return log_entry


if __name__ == "__main__":

    def sum2int(int1, int2):
        int3 = int1 + int2
        return int3 

    def sumintstr(int1, int2):
        int3 = int1 + "not_a_number"  # Deliberate type mismatch
        return int3

    try:
        result = bettertest(sum2int, inputs=(20, "Dog"), output=40)
    except Exception as e:
        print(e)
    
