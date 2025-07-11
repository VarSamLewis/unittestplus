import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
from pathlib import Path
#from src import log_test

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import log_test

class TestLogTestFunctions(unittest.TestCase):
    def setUp(self):
        self.func_name = "myfunc"
        self.file_path = Path.cwd() / "func" / f"{self.func_name}.json"
        self.dummy_data = {
            "function": self.func_name,
            "function_id": "id123",
            "test": {"test_id": 1, "result": 42}
        }

    @patch("log_test.Path")
    def test_get_file_path(self, mock_path):
        mock_path.cwd.return_value = Path("/tmp")
        result = log_test._get_file_path("abc")
        self.assertEqual(result, Path("/tmp") / "func" / "abc.json")

    @patch("log_test.isfile", return_value=True)
    def test_check_file_exists_true(self, mock_isfile):
        self.assertTrue(log_test._check_file_exists("somefile.json"))

    @patch("log_test.isfile", return_value=False)
    def test_check_file_exists_false(self, mock_isfile):
        self.assertFalse(log_test._check_file_exists("somefile.json"))

    @patch("builtins.open", new_callable=mock_open, read_data='{"a":1}')
    @patch("json.load", return_value={"a": 1})
    def test_load_json(self, mock_json_load, mock_file):
        result = log_test._load_json("dummy.json")
        self.assertEqual(result, {"a": 1})
        mock_file.assert_called_with("dummy.json", "r")

    @patch("log_test.Path")
    def test_create_folder_not_exists(self, mock_path):
        mock_folder = MagicMock()
        mock_folder.exists.return_value = False
        mock_folder.mkdir = MagicMock()
        mock_cwd = MagicMock()
        mock_cwd.__truediv__.return_value = mock_folder
        mock_path.cwd.return_value = mock_cwd
        mock_path.return_value = mock_folder
        log_test._create_folder()
        mock_folder.mkdir.assert_called_with(parents=True, exist_ok=True)


    @patch("log_test._create_folder")
    @patch("log_test._get_file_path")
    @patch("log_test._check_file_exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_write_json_creates_new(self, mock_file, mock_exists, mock_get_file_path, mock_create_folder):
        mock_get_file_path.return_value = Path("func/myfunc.json")
        data = {
            "function": "myfunc",
            "function_id": "id123",
            "test": {"test_id": 1, "result": 42}
        }
        log_test.write_json(data)
        mock_file.assert_called_with(Path("func/myfunc.json"), "w")

    @patch("log_test._create_folder")
    @patch("log_test._get_file_path")
    @patch("log_test._check_file_exists", return_value=True)
    @patch("log_test._load_json")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_json_appends(self, mock_file, mock_load_json, mock_exists, mock_get_file_path, mock_create_folder):
        mock_get_file_path.return_value = Path("func/myfunc.json")
        mock_load_json.return_value = {
            "function": "myfunc",
            "function_id": "id123",
            "tests": [{"test_id": 1, "result": 42}]
        }
        data = {
            "function": "myfunc",
            "function_id": "id123",
            "test": {"test_id": 2, "result": 99}
        }
        log_test.write_json(data)
        mock_file.assert_called_with(Path("func/myfunc.json"), "w")

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
