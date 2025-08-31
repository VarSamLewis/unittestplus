import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from unittestplus import manipulate

FUNC_DIR = Path.cwd() / "func"
DUMMY_FUNC_FILE = Path(FUNC_DIR) / "dummy_func_manipulate.json"


def dummy_func_manipulate(a, b):
    return a + b


class TestManipulateFunctions(unittest.TestCase):
    def setUp(self):
        os.makedirs(FUNC_DIR, exist_ok=True)
        # Create a dummy.json file with basic test data
        self.dummy_data = {
            "tests": [
                {
                    "test_id": 1,
                    "test_alias": "a",
                    "score": 1,
                    "definition": "def dummy_func_manipulate(): pass",
                },
                {
                    "test_id": 2,
                    "test_alias": "b",
                    "score": 3,
                    "definition": "def dummy_func_manipulate(): pass",
                },
                {
                    "test_id": 3,
                    "test_alias": "c",
                    "score": 2,
                    "definition": "def dummy_func_manipulate(): pass",
                },
            ]
        }
        with open(DUMMY_FUNC_FILE, "w") as f:
            json.dump(self.dummy_data, f)

    def tearDown(self):
        if DUMMY_FUNC_FILE.exists():
            DUMMY_FUNC_FILE.unlink()

    def test_clear_tests_confirmed(self):
        # Confirm callback always returns True
        manipulate.clear_tests(dummy_func_manipulate, confirm_callback=lambda: True)
        # File should still exist but be empty
        with open(DUMMY_FUNC_FILE, "r") as f:
            data = json.load(f)
        self.assertEqual(data["tests"], [])

    def test_clear_tests_file_not_exists(self):
        # Remove file first
        if os.path.exists(DUMMY_FUNC_FILE):
            os.remove(DUMMY_FUNC_FILE)
        manipulate.clear_tests(dummy_func_manipulate, confirm_callback=lambda: True)
        # Should not raise

    def test_delete_file_confirmed(self):
        manipulate.delete_file(dummy_func_manipulate, confirm_callback=lambda: True)
        self.assertFalse(os.path.exists(DUMMY_FUNC_FILE))

    def test_delete_file_file_not_exists(self):
        if os.path.exists(DUMMY_FUNC_FILE):
            os.remove(DUMMY_FUNC_FILE)
        manipulate.delete_file(dummy_func_manipulate, confirm_callback=lambda: True)
        # Should not raise

    def test_update_alias_success(self):
        result = manipulate.update_alias(dummy_func_manipulate, "alias1", 1)
        # Check file updated
        with open(DUMMY_FUNC_FILE, "r") as f:
            data = json.load(f)
        self.assertEqual(data["tests"][0].get("test_alias"), "alias1")
        self.assertEqual(result, "alias1")

    def test_update_message_success(self):
        result = manipulate.update_message(dummy_func_manipulate, "msg", 1)
        with open(DUMMY_FUNC_FILE, "r") as f:
            data = json.load(f)
        self.assertEqual(data["tests"][0].get("test_message"), "msg")
        self.assertEqual(result, "msg")

    def test_get_testid_found(self):
        result = manipulate.get_testid(dummy_func_manipulate, "a")
        self.assertEqual(result, 1)

    def test_rank_test_by_value(self):
        result = manipulate.rank_test_by_value(dummy_func_manipulate, "score")
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
