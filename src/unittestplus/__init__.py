from .core import unittestplus
from .testsuite import TestSuite
from .manipulate import run_regression

__version__ = "0.2.0"  # Match with your pyproject.toml

__all__ = [
    "unittestplus",
    "run_regression",
    "TestSuite",
]
