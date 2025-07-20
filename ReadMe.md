# unittestplus

**unittestplus** is a lightweight Python utility for testing individual functions with built-in execution profiling. It logs inputs, outputs, execution time, peak memory usage, and can help version and validate function behavior.

I want this to be published on PyPI by the 1st of September 2025
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
- Extensible structure for future versioning, diffs, and JSON logging.
- Generates stable function identities based on module and function name (not affected by internal code changes), enabling tracking of function history independent of code edits.

## How it works

unittestplus combines traditional unit testing (does the function work as expected), basic profiling (timing and memory usage), and function-level version tracking, giving engineers a more complete picture of a function and its history without needing to check Git (or other VCS) or rely on integration/end-to-end tests.

Each test produces a JSON-like log entry with structure similar to:

```json
{
  "function": "sum2int",
  "function_id": "abc123def456",
  "test": {
    "test_id": 123456789,
    "test_alias": "Unique alias for easier retrival"
    "test_message": "Space for messages (authors, commit details) etc."
    "error": null,
    "error_message": null,
    "metrics": {
      "inputs": {"arg0": 2, "arg1": 3},
      "args": [2, 3],
      "kwargs": {},
      "expected_output": 5,
      "actual_output": 5,
      "output_match": true,
      "execution_time_sec": 0.001,
      "peak_memory_kb": 0.789,
      "timestamp": "2025-06-20T15:30:00.000000",
      "custom_metrics": {}
    },
    "definition": "def sum2int(int1, int2):\n    return int1 + int2"
  }
}
```
Complex types (dataframes, dicts etc.) are not stored completely in order to kep test logs lightweight. instead metadata is stored, such as the type and length of the object, and a hash of the content for quick comparison.

## Installation

Just clone and run in any Python environment (3.7+). Please read requirements.txt for dependencies.

```bash
git clone https://github.com/yourname/unittestplus.git
cd unittestplus
python tests/test_core.py
```

## Philosophy

unittestplus is for data scientists, ML engineers, and backend developers who want:

- Fast feedback loops
- Lightweight test instrumentation
- Introspective testing without full test frameworks
- Non-determistic function behavior tracking (LLM outputs, random generators etc.)) 


## License

MIT License

## To-Do

### Documentation and housekeeping
- [ ] Add more examples and documentation
- [ ] Add traceback to loggging

### Publishing to PyPI
- [ ] Prepare Your Package for PyPI
- [ ] Generate PyPI API Token
- [ ] Add the Token to GitHub Secrets
- [ ] Create GitHub Action Workflow for publishing
- [ ] Tag a Release to Trigger Deploy
- [ ] Test on TestPyPI First
- [ ] Validate on PyPI

### Funcxtionality to add in the future
- [ ] Add test suite class 
- [ ] Add regression testing functionality (test new inputs against previous inputs))
- [ ] Functions to rollback changes 
- [ ] Mocks
- [ ] Concurrency (unique test ids might cause issues if multiple devs work on it)
