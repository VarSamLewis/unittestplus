import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Import the modules from the package
try:
    from src.unittestplus import core, log_test, manipulate, serialise, testsuite
    
    # Patch sys.modules to redirect direct imports
    sys.modules['core'] = core
    sys.modules['log_test'] = log_test
    sys.modules['manipulate'] = manipulate
    sys.modules['serialise'] = serialise
    sys.modules['testsuite'] = testsuite
except ImportError:
    # If we're running locally and the package isn't installed, direct imports might still work
    pass

# Discovery and run tests as before

loader = unittest.TestLoader()
suite = loader.discover(start_dir="tests", pattern="test_*.py")

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
