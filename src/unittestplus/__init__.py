from .core import unittestplus
from .manipulate import run_regression
from .testsuite import TestSuite

__version__ = "0.2.1"  # Match with pyproject.toml

__all__ = [
    "unittestplus",
    "run_regression",
    "TestSuite",
]
