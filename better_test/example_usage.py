    
import core
import manipulate
import log_test
import logging

if __name__ == "__main__":

    def _gen_test_identity(func: Callable) -> int:
  
        file_path = log_test._get_file_path(func.__name__)
        if not file_path.exists():
            return []

        data = log_test._load_json(file_path)
        tests = data.get("tests", [])
        for test in tests:
            test_id = test.get(KEY_TESTS, [])
            if isinstance(test_id, int) and test_id > max_val:
                max_val = test_id

        return max_val + 1 if max_val != float('-inf') else 1

    def sum2int(int1: int, int2: int) -> int:
        if int1 is None or int2 is None:
            raise ValueError("Both inputs must be provided")
        return int1 + int2

    try:
        test_id = _gen_test_identity(sum2int)
        print(f"Generated test identity: {test_id}")
    except Exception as e:
        print("Call failed")
