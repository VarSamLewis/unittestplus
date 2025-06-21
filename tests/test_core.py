import unittest
import types
import re
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))

from core import (
    _execute_function, _check_inputVoutput, _func_Identity, _test_Indenity,
    _checkProfile, bettertest
)


def dummy_func(int1, int2):
    int3 = int1 + int2
    return int3 


def error_func(int1, int2):
    int3 = int1 + "not_a_number"  # Deliberate type mismatch
    return int3


class TestBetterTestFunctions(unittest.TestCase):

    def test_execute_function_success(self):
        self.assertEqual(_execute_function(dummy_func, args=[2, 3]), 5)

    def test_bettertest_error(self):
        result = bettertest(error_func, inputs=(2, 3), output=None, display=False)
        self.assertTrue(result['test']['error'])
        self.assertTrue(result['test']['error_message'])  # Just check that an error message exists

    def test_check_inputVoutput_true(self):
        self.assertTrue(_check_inputVoutput(10, 10, display=False))

    def test_check_inputVoutput_false(self):
        self.assertFalse(_check_inputVoutput(5, 10, display=False))

    def test_check_inputVoutput_none(self):
        self.assertFalse(_check_inputVoutput(None, 10, display=False))

    def test_func_identity_stability(self):
        id1 = _func_Identity(dummy_func)
        id2 = _func_Identity(dummy_func)
        self.assertEqual(id1['function_id'], id2['function_id'])

    def test_func_identity_uniqueness(self):
        id1 = _func_Identity(dummy_func)
        id2 = _func_Identity(error_func)
        self.assertNotEqual(id1['function_id'], id2['function_id'])

    def test_test_identity_different(self):
        id1 = _test_Indenity(dummy_func)
        id2 = _test_Indenity(dummy_func)
        self.assertNotEqual(id1, id2)

    def test_checkProfile(self):
        result, time_used, mem_used = _checkProfile(dummy_func, args=[1, 2])
        self.assertEqual(result, 3)
        self.assertTrue(time_used >= 0)
        self.assertTrue(mem_used >= 0)

    def test_bettertest_success(self):
        result = bettertest(dummy_func, inputs=(2, 2), output=4, display=False)
        self.assertTrue(result['test']['metrics']['output_match'])

    def test_bettertest_failure(self):
        result = bettertest(dummy_func, inputs=(2, 2), output=5, display=False)
        self.assertFalse(result['test']['metrics']['output_match'])


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