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

### Core Function

**Function:** `unittestplus`

Runs a function with given inputs and logs the result.

```python
unittestplus(
    func,                # Function to test
    inputs=None,         # Positional arguments
    kwargs=None,         # Keyword arguments
    expected_output=None,# Expected output to compare against
    display=True,        # Print/log test result summary
    alias=None,          # Alias for this test
    message=None,        # Message/description for this test
    custom_metrics=None, # Custom metrics to evaluate
    assertion=None,      # Assertion dict, e.g. {"type": "equals", "value": 5}
    verbose=False        # If True, show detailed logs; if False, suppress logs
) 
```

---
### All UserFacing API Function Examples 

```python
from unittestplus.core import unittestplus
from unittestplus.manipulate import run_regression
from unittestplus.testsuite import TestSuite

# --- Simple function to test ---
def add(a, b):
    return a + b

# --- Run unittestplus ---
result = unittestplus(
    func=add,
    inputs=[2, 3],
    expected_output=5,
    alias="Addition test",
    message="Basic addition check",
    assertion={"type": "equals", "value": 5},
    display=True,
)

# --- Run regression ---
regression_result = run_regression(
    func="add",  # Name as string for regression
    inputs=[[2, 3], [10, 20], [0, 0]],
    display=True,
)

# --- Run testsuite ---
suite = TestSuite()

func = "add"

suite.unittestplus(func, inputs=[5, 5])
suite.unittestplus(func, inputs=[10, 20], expected_output=30)
suite.unittestplus(func, inputs=[-5, 5], expected_output=0)
suite.unittestplus(
    func, inputs=[1, 2], expected_output=3, assertion={"type": "equals", "value": 3}
)
suite.unittestplus(
    func, inputs=[1, 2], expected_output=4, assertion={"type": "equals", "value": 3}
)
suite.unittestplus(
    func, inputs=[1, 2], expected_output=4, assertion={"type": "equals", "value": 2}
)
suite.unittestplus(func, inputs=["1", 2])
suite.run_tests()
suite.print_summary()
```
---

## License

MIT License

---
## To-Do

### Documentation and housekeeping
- [ ] Add traceback to logging
- [ ] Refactor long functions
- [ ] Split up modules to prevent circular imports

### Publishing to PyPi
- [ ] Validate on PyPI

### Functionality to add in the future
- [ ] Data validity checks (schemas, types)
- [ ] More complex assertions (tolerances, regex, custom functions)
- [ ] Bytemap strings 
- [ ] Async function support
- [ ] Change JSON writes to either use sqllite or append-only writes
- [ ] Concurrency (unique, sequential test ids might cause issues if multiple devs work on it)
