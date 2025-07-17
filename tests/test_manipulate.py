import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import manipulate

class DummyFunc:
    __name__ = "dummy_func"
#from manipulate import (
#
#    )

class TestManipulateFunctions(unittest.TestCase):
    @patch("manipulate._get_file_path")
    @patch("manipulate._load_json")
    @patch("builtins.open", new_callable=mock_open)
    def test_clear_tests_confirmed(self, mock_file, mock_load_json, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        mock_load_json.return_value = {"tests": [1, 2, 3]}
        with patch("pathlib.Path.exists", return_value=True):
            manipulate.clear_tests(DummyFunc, confirm_callback=lambda: True)
            mock_file.assert_called_with(Path("dummy.json"), "w")

    @patch("manipulate._get_file_path")
    def test_clear_tests_file_not_exists(self, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        with patch("pathlib.Path.exists", return_value=False):
            manipulate.clear_tests(DummyFunc, confirm_callback=lambda: True)

    @patch("manipulate._get_file_path")
    @patch("pathlib.Path.unlink")
    def test_delete_file_confirmed(self, mock_unlink, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        with patch("pathlib.Path.exists", return_value=True):
            manipulate.delete_file(DummyFunc, confirm_callback=lambda: True)
            mock_unlink.assert_called_once()

    @patch("manipulate._get_file_path")
    def test_delete_file_file_not_exists(self, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        with patch("pathlib.Path.exists", return_value=False):
            manipulate.delete_file(DummyFunc, confirm_callback=lambda: True)

    @patch("manipulate._get_file_path")
    @patch("manipulate._load_json")
    @patch("builtins.open", new_callable=mock_open)
    def test_update_alias_success(self, mock_file, mock_load_json, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        mock_load_json.return_value = {"tests": [{"test_id": 1}]}
        with patch("pathlib.Path.exists", return_value=True):
            result = manipulate.update_alias(DummyFunc, "alias1", 1)
            self.assertEqual(result, "alias1")

    @patch("manipulate._get_file_path")
    @patch("manipulate._load_json")
    @patch("builtins.open", new_callable=mock_open)
    def test_update_message_success(self, mock_file, mock_load_json, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        mock_load_json.return_value = {"tests": [{"test_id": 1}]}
        with patch("pathlib.Path.exists", return_value=True):
            result = manipulate.update_message(DummyFunc, "msg", 1)
            self.assertEqual(result, "msg")

    @patch("manipulate._get_file_path")
    @patch("manipulate._load_json")
    def test_get_testid_found(self, mock_load_json, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        mock_load_json.return_value = {"tests": [{"test_alias": "a", "test_id": 42}]}
        with patch("pathlib.Path.exists", return_value=True):
            result = manipulate.get_testid(DummyFunc, "a")
            self.assertEqual(result, 42)

    @patch("manipulate._get_file_path")
    @patch("manipulate._load_json")
    def test_rank_test_by_value(self, mock_load_json, mock_get_file_path):
        mock_get_file_path.return_value = Path("dummy.json")
        mock_load_json.return_value = {"tests": [{"score": 1}, {"score": 3}, {"score": 2}]}
        with patch("pathlib.Path.exists", return_value=True):
            result = manipulate.rank_test_by_value(DummyFunc, "score")
            self.assertEqual(result[0]["score"], 3)

    def test_similarity_score(self):
        scores = manipulate._similarity_score("abc", "abd")
        self.assertIsInstance(scores, list)
        self.assertEqual(len(scores[0]), 3)

    def test_diff_json(self):
        a = {"x": 1, "y": {"z": 2}}
        b = {"x": 2, "y": {"z": 2}, "w": 3}
        diffs = manipulate._diff_json(a, b)
        self.assertTrue(any(d["type"] == "changed" for d in diffs))
        self.assertTrue(any(d["type"] == "added" for d in diffs))


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
    class_test = loader.loadTestsFromTestCase(TestManipulateFunctions)
    suite = unittest.TestSuite([class_test])
    runner = unittest.TextTestRunner(resultclass=VerboseTestResult, verbosity=0)
    runner.run(suite)

if __name__ == "__main__":
    run_tests()