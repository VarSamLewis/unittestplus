import unittest
import types
import re
import json
import datetime
import tempfile
import shutil
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'better_test')))


from log_test import (
    _get_file_path,
    _check_file_exists,
    _load_json,
    write_json
)

# Dummy data for testing
dummy_data = {
    "function": "sum2int",
    "function_id": "sum2int_abcd1234",
    "test": {
        "test_id": "test001",
        "error": False,
        "error_message": None,
        "metrics": {
            "inputs": {"arg0": 1, "arg1": 2},
            "args": [1, 2],
            "kwargs": {},
            "expected_output": 3,
            "actual_output": 3,
            "output_match": True,
            "execution_time_sec": 0.002,
            "peak_memory_kb": 512,
            "timestamp": datetime.datetime.utcnow().isoformat()
        },
        "definition": "def sum2int(a, b):\n    return a + b"
    }
}


class TestBetterTestFunctions(unittest.TestCase):

    def setUp(self):
        # Create temp directory and patch Path.cwd
        self.test_dir = tempfile.mkdtemp()
        self.better_test_path = os.path.join(self.test_dir, "better_test")
        os.makedirs(self.better_test_path, exist_ok=True)

        self.original_cwd = Path.cwd
        Path.cwd = lambda: Path(self.test_dir)

    def tearDown(self):
        # Restore Path.cwd and clean up
        Path.cwd = self.original_cwd
        shutil.rmtree(self.test_dir)

    def test_get_file_path(self):
        expected = Path(self.test_dir) / "better_test" / "sum2int_abcd1234.json"
        actual = _get_file_path("sum2int_abcd1234")
        self.assertEqual(Path(actual), expected)

    def test_check_file_exists_false(self):
        path = _get_file_path("nonexistent")
        self.assertFalse(_check_file_exists(path))

    def test_write_json_creates_file(self):
        file_path = _get_file_path(dummy_data["function_id"])
        self.assertFalse(_check_file_exists(file_path))

        write_json(dummy_data)
        self.assertTrue(_check_file_exists(file_path))

        with open(file_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["function_id"], dummy_data["function_id"])
            self.assertEqual(len(data["tests"]), 1)
            self.assertEqual(data["tests"][0]["test_id"], "test001")

    def test_write_json_appends_test(self):
        # Write first test
        write_json(dummy_data)

        # Modify and write second test
        new_test = dummy_data.copy()
        new_test["test"] = new_test["test"].copy()
        new_test["test"]["test_id"] = "test002"
        write_json(new_test)

        file_path = _get_file_path(dummy_data["function_id"])
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data["tests"]), 2)
            self.assertEqual(data["tests"][1]["test_id"], "test002")


def run_tests():
    class VerboseTestResult(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            print(f"{test.id()} - PASS")

        def addFailure(self, test, err):
            super().addFailure(test, err)
            print(f"{test.id()} - FAIL: {err[1]}")

        def addError(self, test, err):
            super().addError(test, err)
            print(f"{test.id()} - ERROR: {err[1]}")

    loader = unittest.TestLoader()
    class_test = loader.loadTestsFromTestCase(TestBetterTestFunctions)
    suite = unittest.TestSuite([class_test])
    runner = unittest.TextTestRunner(resultclass=VerboseTestResult, verbosity=0)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
 
