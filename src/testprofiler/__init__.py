from .core import testprofiler
from .manipulate import run_regression
from .testsuite import TestSuite

__version__ = "1.0.1"  # Match with pyproject.toml

__all__ = [
    "testprofiler",
    "run_regression",
    "TestSuite",
]
