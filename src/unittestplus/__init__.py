from .core import unittestplus
from .manipulate import run_regression
from .testsuite import TestSuite

__version__ = "0.2.0"  # Match with your pyproject.toml

__all__ = [
    "unittestplus",
    "run_regression",
    "TestSuite",
]
