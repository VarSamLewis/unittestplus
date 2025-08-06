# unittestplus

**unittestplus** is a lightweight Python utility for testing individual functions with built-in execution profiling, regression testing, and test management. It logs inputs, outputs, execution time, peak memory usage, and can help version and validate function behavior.

> **PyPI Release Target:** September 1st, 2025

---

## Features

- Easy-to-use `unittestplus()` function for testing any Python function.
- Automatically compares actual vs expected output.
- Logs:
  - Inputs (args + kwargs)
  - Execution time (in seconds)
  - Peak memory usage (in KB)
  - Output match (boolean)
  - Timestamp
  - Full function definition (as a string)
- Extensible structure for versioning, diffs, and JSON logging.
- Generates stable function identities based on module and function name.
- Regression testing and test comparison utilities.
- Lightweight serialization for complex types (DataFrames, arrays, etc.).
- Test management: clear, delete, filter, rank, and update test metadata.

---

## Installation

Clone and run in any Python environment (3.7+). See `requirements.txt` for dependencies.

```bash
git clone https://github.com/yourname/unittestplus.git
cd unittestplus
python tests/run_tests.py
```

## Philosophy

unittestplus is for data scientists, ML engineers, and backend developers who want:

- Fast feedback loops
- Lightweight test instrumentation
- Introspective testing without full test frameworks
- Non-deterministic function behavior tracking (LLM outputs, random generators, etc.)

---

## Quick Start Example

```python
from core import unittestplus

def sum2int(a, b):
    return a + b

# Run and log a test
unittestplus(
    func=sum2int,
    inputs=[2, 3],
    expected_output=5,
    alias="Addition test",
    message="Basic addition check",
    assertion={"type": "equals", "value": 5},
    display=True
)
```

---

## Test Log Structure

Each test produces a JSON log entry in `func/<function_name>.json`:

```json
{
  "function": "sum2int",
  "function_id": "abc123def456",
  "test": {
    "test_id": 1,
    "test_alias": "Addition test",
    "test_message": "Basic addition check",
    "error": null,
    "error_message": null,
    "metrics": {
      "inputs": {"arg0": 2, "arg1": 3},
      "args": [2, 3],
      "kwargs": {},
      "expected_output": 5,
      "actual_output": 5,
      "output_match": true,
      "assertion": {
           "type": "equals",
           "value": 5
      },
      "assertion_passed": true,
      "execution_time_sec": 0.001,
      "peak_memory_kb": 0.789,
      "timestamp": "2025-06-20T15:30:00.000000",
      "custom_metrics": {}
    },
    "definition": "def sum2int(a, b):\n    return a + b"
  }
}
```

Complex types (dataframes, dicts, etc.) are stored as metadata (type, length, sample) for lightweight logs.

---

## User-Facing API

### 1. Logging and Running Tests

**Function:** `unittestplus`

Runs a function with given inputs and logs the result.

```python
unittestplus(
    func,                # Function to test
    inputs=None,         # List/tuple of positional arguments
    kwargs=None,         # Dict of keyword arguments
    expected_output=None,
    display=True,
    alias=None,
    message=None,
    custom_metrics=None, # Dict of metric functions or expressions
    assertion=None       # Dict, e.g. {"type": "equals", "value": 5}
)
```

---

### 2. Managing Test Files

**Clear all tests for a function:**

```python
from manipulate import clear_tests
clear_tests(sum2int)
```

**Delete a function's test file:**

```python
from manipulate import delete_file
delete_file(sum2int)
```

---

### 3. Test Metadata

**Update test alias or message:**

```python
from manipulate import update_alias, update_message
update_alias(sum2int, "MyAlias", test_id=1)
update_message(sum2int, "This is a test", test_id=1)
```

**Get test ID by alias:**

```python
from manipulate import get_testid
test_id = get_testid(sum2int, "MyAlias")
```

---

### 4. Test Query & Comparison

**Filter tests by value:**

```python
from manipulate import filter_test_by_value
results = filter_test_by_value(sum2int, key="error", value=False)
```

**Rank tests by a metric:**

```python
from manipulate import rank_test_by_value
ranked = rank_test_by_value(sum2int, key="execution_time_sec")
```

**Compare most recent tests:**

```python
from manipulate import compare_most_recent
diffs = compare_most_recent(sum2int)
```

**Compare inputs/outputs of two tests:**

```python
from manipulate import compare_io
compare_io(sum2int, test_id_1=1, test_id_2=2)
```

---

### 5. Regression Testing

**Run regression tests:**

```python
from manipulate import run_regression
summary = run_regression("sum2int", inputs=[[2, 3], [5, 7]])
```

---

### 6. Serialization Utilities

**Safely serialize objects for logging:**

```python
from serialise import safe_serialise
safe_serialise([1, 2, 3])
```


---

## License

MIT License

---
## To-Do

### Documentation and housekeeping
- [ ] Add more examples and documentation
- [ ] Add traceback to loggging
- [ ] Refactor long functions

### Publishing to PyPi
- [ ] Validate on PyPI

### Funcxtionality to add in the future
- [ ] Bytemap strings
- [ ] Add test suite class 
- [ ] Functions to rollback changes 
- [ ] Mocks
- [ ] Concurrency (unique test ids might cause issues if multiple devs work on it)
