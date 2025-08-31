import os
import sys
import unittest

import numpy as np
import pandas as pd
import polars as pl

# Adjust path for local import if needed
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from unittestplus import serialise


class TestSafeSerialise(unittest.TestCase):

    def test_serialize_dataframe(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        result = serialise.safe_serialise(df)
        self.assertEqual(result["type"], "DataFrame")
        self.assertEqual(result["shape"], (2, 2))
        self.assertEqual(result["columns"], ["a", "b"])
        self.assertEqual(result["dtypes"], {"a": "int64", "b": "int64"})
        self.assertEqual(result["sample"], df.head(3).to_dict())

    def test_serialize_series(self):
        s = pd.Series([1, 2, 3], name="my_series")
        result = serialise.safe_serialise(s)
        self.assertEqual(result["type"], "Series")
        self.assertEqual(result["shape"], (3,))
        self.assertEqual(result["name"], "my_series")
        self.assertEqual(result["dtype"], "int64")
        self.assertEqual(result["sample"], [1, 2, 3])

    def test_serialize_ndarray(self):
        arr = np.array(
            [[1, 2], [3, 4]], dtype=np.int64
        )  # Forcing dtype to int64 for platform compatibility
        result = serialise.safe_serialise(arr)
        self.assertEqual(result["type"], "ndarray")
        self.assertEqual(result["shape"], (2, 2))
        self.assertEqual(result["dtype"], "int64")
        self.assertEqual(result["sample"], [1, 2, 3])

    def test_serialize_list(self):
        result = serialise.safe_serialise([1, 2, 3, 4])
        self.assertEqual(result["type"], "list")
        self.assertEqual(result["length"], 4)
        self.assertEqual(result["sample"], [1, 2, 3])

    def test_serialize_dict(self):
        d = {"a": 1, "b": 2, "c": 3}
        result = serialise.safe_serialise(d)
        self.assertEqual(result["type"], "dict")
        self.assertEqual(result["length"], 3)
        self.assertEqual(result["sample"], {"a": 1, "b": 2, "c": 3})

    def test_serialize_primitive(self):
        for val in [123, "hello", 3.14, True, None]:
            self.assertEqual(serialise.safe_serialise(val), val)

    def test_serialize_unhandled_type(self):
        class Foo:
            def __str__(self):
                return "custom_obj"

        f = Foo()
        self.assertEqual(serialise.safe_serialise(f), "custom_obj")


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
    class_test = loader.loadTestsFromTestCase(TestSafeSerialise)
    suite = unittest.TestSuite([class_test])
    runner = unittest.TextTestRunner(resultclass=VerboseTestResult, verbosity=0)
    runner.run(suite)


if __name__ == "__main__":
    run_tests()
