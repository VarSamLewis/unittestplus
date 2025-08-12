from .core import unittestplus

KEY_TESTS = "tests"
KEY_TEST_ID = "test_id"


class TestSuite:
    def __init__(self):
        self.tests = []


    def unittestplus(self, func, **kwargs):
        self.tests.append({
            "func": func,
            "kwargs": kwargs
            })


    def run_tests(self):
        results = []
        for test in self.tests:
            func = test["func"]
            kwargs = test["kwargs"]
            result = unittestplus(func, **kwargs)
            results.append(result)
            
        return results
    
    def summary_tbl(self):

        if not hasattr(self, 'results') or not self.results:
            self.results = self.run_tests()

        total_tests = len(self.results)
        tests_with_errors = 0
        tests_with_expected = 0
        tests_with_output_match = 0
        tests_with_assertion = 0
        tests_passed_assertion = 0
        tests_with_error = 0

        functions_tested = set()

        for result in self.results:
            if result is None:
                continue

            function_name = result.get('function')
            functions_tested.add(function_name)

            test = result.get('test', {})
            metrics = test.get('metrics', {})

            # Check if expected output was provided
            if metrics.get('expected_output') is not None:
                tests_with_expected += 1
            
            # Check if output matched expected
            if metrics.get('output_match') is True:
                tests_with_output_match += 1
            
            # Check if test had an assertion
            if metrics.get('assertion') is not None:
                tests_with_assertion += 1
            
            # Check if assertion passed
            if metrics.get('assertion_passed') is True:
                tests_passed_assertion += 1
            
            # Check if test had an error
            if test.get('error') is True:
                tests_with_error += 1
        
        summary_tbl = {}

        summary_tbl = {
            'total_tests': total_tests,
            'unique_functions': len(functions_tested),
            'functions_tested': list(functions_tested),
            'tests_with_expected_output': tests_with_expected,
            'tests_with_output_match': tests_with_output_match,
            'output_match_percentage': round(tests_with_output_match / total_tests * 100, 1) if total_tests > 0 else 0,
            'tests_with_assertion': tests_with_assertion,
            'tests_passed_assertion': tests_passed_assertion,
            'assertion_pass_percentage': round(tests_passed_assertion / tests_with_assertion * 100, 1) if tests_with_assertion > 0 else 0,
            'tests_with_error': tests_with_error,
            'error_percentage': round(tests_with_error / total_tests * 100, 1) if total_tests > 0 else 0
            
            }
        return summary_tbl

    def print_summary(self):
        summary = self.summary_tbl()
        
        print("\n===== TEST SUITE SUMMARY =====")
        print(f"Total tests run: {summary['total_tests']}")
        print(f"Functions tested: {', '.join(summary['functions_tested'])}")

        print("\n--- Test Coverage ---")
        print(f"Tests with expected output: {summary['tests_with_expected_output']} ({summary['tests_with_expected_output']/summary['total_tests']*100:.1f}%)")
        print(f"Tests with assertions: {summary['tests_with_assertion']} ({summary['tests_with_assertion']/summary['total_tests']*100:.1f}%)")
        
        print("\n--- Test Results ---")
        print(f"Tests with output match: {summary['tests_with_output_match']} ({summary['output_match_percentage']}%)")
        print(f"Tests with passing assertions: {summary['tests_passed_assertion']} ({summary['assertion_pass_percentage']}%)")
        print(f"Tests with errors: {summary['tests_with_error']} ({summary['error_percentage']}%)")
        print("==============================\n")


def main():
    suite = TestSuite()
   
    func = "sum2int"

    suite.unittestplus(func, inputs = [5,5])
    suite.unittestplus(func, inputs=[10, 20], expected_output = 30)
    suite.unittestplus(func, inputs=[-5, 5], expected_output=0)
    suite.unittestplus(func, inputs=[1, 2], expected_output=3, assertion={"type": "equals", "value": 3})
    suite.unittestplus(func, inputs=[1, 2], expected_output=4, assertion={"type": "equals", "value": 3})
    suite.unittestplus(func, inputs=[1, 2], expected_output=4, assertion={"type": "equals", "value": 2})
    suite.unittestplus(func, inputs=["1", 2])
    
    suite.run_tests()
    suite.print_summary()

if __name__ == "__main__":
    main()