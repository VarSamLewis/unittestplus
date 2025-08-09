# Core functionality
from .core import unittestplus
from .core import (
    _compare_outputs, _simple_assert, 
    _gen_func_identity, _gen_test_identity, 
    _check_profile, _add_custom_metrics
)

# Manipulation functions
from .manipulate import (
    clear_tests, delete_file, update_alias, update_message,
    get_testid, rank_test_by_value, get_previous_test_definition,
    filter_test_by_value, compare_func_similarity, compare_most_recent,
    get_test, compare_io, run_regression, _rebuild_function_from_definition
)

# TestSuite class
from .testsuite import TestSuite

# Logging and file functions (if you want to expose these)
from .log_test import write_json, _get_file_path, _load_json, _get_regression_file_path

# Serialization (if you have this module)
try:
    from .serialise import safe_serialise
except ImportError:
    pass

# Constants
from .core import KEY_TESTS, KEY_TEST_ID, KEY_FUNCTION, KEY_FUNCTION_ID

__version__ = "0.1.3"