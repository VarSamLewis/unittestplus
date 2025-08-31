import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from unittestplus import log_test

FUNC_DIR = Path.cwd() / "func"
DUMMY_FUNC_FILE = Path(FUNC_DIR) / "dummy_func_log_test.json"


def dummy_func_log_test(a, b):
    return a + b


class TestLogTestFunctions(unittest.TestCase):
    def setUp(self):
        FUNC_DIR.mkdir(parents=True, exist_ok=True)
        self.func_name = "dummy_func_log_test"
        self.file_path = DUMMY_FUNC_FILE
        self.dummy_data = {
            "function": self.func_name,
            "function_id": "id123",
            "tests": [{"test_id": 1, "result": 42}],
        }
        with open(self.file_path, "w") as f:
            json.dump(self.dummy_data, f)

    def tearDown(self):
        if DUMMY_FUNC_FILE.exists():
            DUMMY_FUNC_FILE.unlink()

    def test_get_file_path(self):
        result = log_test._get_file_path(self.func_name)
        self.assertEqual(result, DUMMY_FUNC_FILE)

    def test_check_file_exists_true(self):
        self.assertTrue(log_test._check_file_exists(self.file_path))

    def test_check_file_exists_false(self):
        if self.file_path.exists():
            self.file_path.unlink()
        self.assertFalse(log_test._check_file_exists(self.file_path))

    def test_load_json(self):
        result = log_test._load_json(self.file_path)
        self.assertEqual(result["function"], self.func_name)
        self.assertEqual(result["function_id"], "id123")
        self.assertEqual(result["tests"][0]["test_id"], 1)

    """
    def test_create_folder_not_exists(self):
        # Remove folder and file if exists
        if self.file_path.exists():
            self.file_path.unlink()
        if FUNC_DIR.exists():
            os.rmdir(FUNC_DIR)
        log_test._create_folder()
        self.assertTrue(FUNC_DIR.exists())
    """

    def test_write_json_creates_new(self):
        # Remove file first
        if self.file_path.exists():
            self.file_path.unlink()
        data = {
            "function": self.func_name,
            "function_id": "id123",
            "test": {"test_id": 2, "result": 99},
        }
        log_test.write_json(data)
        with open(self.file_path, "r") as f:
            result = json.load(f)
        self.assertEqual(result["function"], self.func_name)
        self.assertEqual(result["function_id"], "id123")
        self.assertEqual(result["tests"][0]["test_id"], 2)

    def test_write_json_appends(self):
        data = {
            "function": self.func_name,
            "function_id": "id123",
            "test": {"test_id": 2, "result": 99},
        }
        log_test.write_json(data)
        with open(self.file_path, "r") as f:
            result = json.load(f)
        self.assertEqual(len(result["tests"]), 2)
        self.assertEqual(result["tests"][1]["test_id"], 2)
        self.assertEqual(result["tests"][1]["result"], 99)


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
    class_test = loader.loadTestsFromTestCase(TestLogTestFunctions)
    suite = unittest.TestSuite([class_test])
    runner = unittest.TextTestRunner(resultclass=VerboseTestResult, verbosity=0)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
