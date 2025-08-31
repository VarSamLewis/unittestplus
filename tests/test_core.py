import inspect
import json
import os
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from unittestplus import core


def dummy_func_core(a, b):
    return a + b


def error_func_core(a, b):
    return a + "bad"  # Will raise TypeError


FUNC_DIR = os.path.join(os.path.dirname(__file__), "..", "func")
DUMMY_FUNC_FILE = Path(FUNC_DIR) / "dummy_func_core.json"
ERROR_FUNC_FILE = Path(FUNC_DIR) / "error_func_core.json"


class TestCoreFunctions(unittest.TestCase):
    def setUp(self):
        os.makedirs(FUNC_DIR, exist_ok=True)
        # Write dummy_func_core.json
        dummy_data = {
            "tests": [
                {
                    "definition": inspect.getsource(dummy_func_core),
                    "test_id": 1,
                    "metrics": {
                        "args": [2, 2],
                        "kwargs": {},
                        "expected_output": 4,
                        "actual_output": 4,
                        "output_match": True,
                    },
                }
            ]
        }
        with open(DUMMY_FUNC_FILE, "w") as f:
            json.dump(dummy_data, f)
        # Write error_func_core.json
        error_data = {
            "tests": [
                {
                    "definition": inspect.getsource(error_func_core),
                    "test_id": 1,
                    "metrics": {
                        "args": [2, 3],
                        "kwargs": {},
                        "expected_output": None,
                        "actual_output": None,
                        "output_match": False,
                    },
                }
            ]
        }
        with open(ERROR_FUNC_FILE, "w") as f:
            json.dump(error_data, f)

    def tearDown(self):
        if DUMMY_FUNC_FILE.exists():
            DUMMY_FUNC_FILE.unlink()
        if ERROR_FUNC_FILE.exists():
            ERROR_FUNC_FILE.unlink()

    def test_execute_function_success(self):
        self.assertEqual(core._execute_function(dummy_func_core, args=[2, 3]), 5)

    def test_execute_function_none(self):
        with self.assertRaises(ValueError):
            core._execute_function(None, args=[1, 2])

    def test_execute_function_error(self):
        with self.assertRaises(RuntimeError):
            core._execute_function(error_func_core, args=[1, 2])

    def test_compare_outputs_equal_scalars(self):
        self.assertTrue(core._compare_outputs(5, 5))
        self.assertTrue(core._compare_outputs("hello", "hello"))
        self.assertFalse(core._compare_outputs(5, "5"))

    def test_compare_outputs_none(self):
        self.assertTrue(core._compare_outputs(None, None))
        self.assertFalse(core._compare_outputs(None, 0))
        self.assertFalse(core._compare_outputs("None", None))

    def test_compare_outputs_lists(self):
        a = [1, 2, 3]
        b = [1, 2, 3]
        c = [1, 2, 4]
        self.assertTrue(core._compare_outputs(a, b))
        self.assertFalse(core._compare_outputs(a, c))

    def test_compare_outputs_dicts(self):
        a = {"x": 1, "y": 2}
        b = {"x": 1, "y": 2}
        c = {"x": 1, "y": 99}
        self.assertTrue(core._compare_outputs(a, b))
        self.assertFalse(core._compare_outputs(a, c))

    def test_compare_outputs_dataframes(self):
        df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        df2 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        df3 = pd.DataFrame({"a": [1, 2], "b": [3, 9]})
        self.assertTrue(core._compare_outputs(df1, df2))
        self.assertFalse(core._compare_outputs(df1, df3))

    def test_compare_outputs_series(self):
        s1 = pd.Series([1, 2, 3])
        s2 = pd.Series([1, 2, 3])
        s3 = pd.Series([1, 2, 4])
        self.assertTrue(core._compare_outputs(s1, s2))
        self.assertFalse(core._compare_outputs(s1, s3))

    def test_compare_outputs_ndarray(self):
        arr1 = np.array([1, 2, 3])
        arr2 = np.array([1, 2, 3])
        arr3 = np.array([1, 2, 9])
        self.assertTrue(core._compare_outputs(arr1, arr2))
        self.assertFalse(core._compare_outputs(arr1, arr3))

    def test_compare_outputs_type_mismatch(self):
        self.assertFalse(core._compare_outputs([1, 2, 3], (1, 2, 3)))
        self.assertFalse(core._compare_outputs({"a": 1}, [("a", 1)]))

    def test_gen_func_identity_stability(self):
        id1 = core._gen_func_identity(dummy_func_core)
        id2 = core._gen_func_identity(dummy_func_core)
        self.assertEqual(id1["function_id"], id2["function_id"])

    def test_gen_func_identity_uniqueness(self):
        id1 = core._gen_func_identity(dummy_func_core)
        id2 = core._gen_func_identity(error_func_core)
        self.assertNotEqual(id1["function_id"], id2["function_id"])

    def test_gen_func_identity_none(self):
        with self.assertRaises(ValueError):
            core._gen_func_identity(None)

    def test_gen_test_identity_new(self):
        result = core._gen_test_identity(dummy_func_core)
        self.assertEqual(result, 2)  # Next test_id after 1

    def test_gen_test_identity_increment(self):
        # Add another test to dummy_func_core.json
        with open(DUMMY_FUNC_FILE, "r") as f:
            data = json.load(f)
        data["tests"].append(
            {
                "definition": inspect.getsource(dummy_func_core),
                "test_id": 2,
                "metrics": {
                    "args": [3, 3],
                    "kwargs": {},
                    "expected_output": 6,
                    "actual_output": 6,
                    "output_match": True,
                },
            }
        )
        with open(DUMMY_FUNC_FILE, "w") as f:
            json.dump(data, f)
        result = core._gen_test_identity(dummy_func_core)
        self.assertEqual(result, 3)

    def test_check_profile(self):
        result, time_used, mem_used = core._check_profile(dummy_func_core, args=[1, 2])
        self.assertEqual(result, 3)
        self.assertTrue(time_used >= 0)
        self.assertTrue(mem_used >= 0)

    def test_clean_definition(self):
        code = "def foo():\n    # comment\n    return 1\n"
        cleaned = core._clean_definition(code)
        self.assertNotIn("# comment", cleaned)
        self.assertIn("return 1", cleaned)

    def test_add_custom_metrics_none(self):
        result = core._add_custom_metrics(dummy_func_core, None, [1, 2], {})
        self.assertEqual(result, {})

    def test_add_custom_metrics_callable(self):
        def metric(func, args, kwargs):
            return args[0] * 2

        metrics = {"double_first": metric}
        result = core._add_custom_metrics(dummy_func_core, metrics, [2, 3], {})
        self.assertEqual(result["double_first"], 4)

    def test_add_custom_metrics_string(self):
        metrics = {"sum_args": "args[0] + args[1]"}
        result = core._add_custom_metrics(dummy_func_core, metrics, [2, 3], {})
        self.assertEqual(result["sum_args"], 5)

    def test_add_custom_metrics_invalid(self):
        metrics = {"bad": 123}
        result = core._add_custom_metrics(dummy_func_core, metrics, [2, 3], {})
        self.assertIn("Invalid metric type", result["bad"])

    def test_add_custom_metrics_error(self):
        metrics = {"err": "1/0"}
        result = core._add_custom_metrics(dummy_func_core, metrics, [2, 3], {})
        self.assertIn("Error evaluating metric", result["err"])

    def test_unittestplus_success(self):
        result = core.unittestplus(
            dummy_func_core, inputs=[2, 2], expected_output=4, display=False
        )
        self.assertTrue(result["test"]["metrics"]["output_match"])
        self.assertIsNone(result["test"]["error"])

    def test_unittestplus_failure(self):
        result = core.unittestplus(
            dummy_func_core, inputs=[2, 2], expected_output=5, display=False
        )
        self.assertFalse(result["test"]["metrics"]["output_match"])

    def test_unittestplus_error(self):
        result = core.unittestplus(
            error_func_core, inputs=[2, 3], expected_output=None, display=False
        )
        self.assertTrue(result["test"]["error"])
        self.assertTrue(result["test"]["error_message"])


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
    class_test = loader.loadTestsFromTestCase(TestCoreFunctions)
    suite = unittest.TestSuite([class_test])
    runner = unittest.TextTestRunner(resultclass=VerboseTestResult, verbosity=0)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
