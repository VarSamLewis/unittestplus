# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2025

### Changed
- **BREAKING**: Changed import name from `unittestplus` to `testprofiler`
- Renamed main function from `unittestplus()` to `testprofiler()`
- Renamed `TestSuite.unittestplus()` method to `TestSuite.testprofiler()`
- Updated all documentation and examples with new import names
- Updated test files to use new package name

### Migration Guide
- Change `from unittestplus import unittestplus` to `from testprofiler import testprofiler`
- Change `unittestplus(...)` calls to `testprofiler(...)`
- Change `suite.unittestplus(...)` calls to `suite.testprofiler(...)`

## [1.0.0] - 2025

### Added
- LICENSE file (MIT License)
- CHANGELOG.md for tracking version history
- Version constraints to dependencies in pyproject.toml

### Changed
- **BREAKING**: Renamed package to `testprofiler` on PyPI (import name remains `unittestplus`)
- Updated README.md with correct installation instructions for PyPI
- Fixed import examples in documentation (from `core` to `unittestplus`)
- Standardized Python version target to 3.10+ across all tools (black, ruff, mypy)
- Updated version to 1.0.0 for official PyPI release

### Fixed
- Python version target inconsistencies in pyproject.toml

## [0.2.1] - 2024

### Changed
- Added dev dependencies to pyproject.toml
- Cleaned up codebase

## [0.2.0] - 2024

### Added
- Code quality tools: black, mypy, ruff
- GitHub Actions for automated testing and linting
- Type checking with mypy
- Formatting with black
- Linting with ruff

### Changed
- Major refactoring of codebase
- Improved package structure

## [0.1.8] - 2024

### Changed
- Fixed import issues
- Updated GitHub Actions workflow

## [0.1.7] - 2024

### Fixed
- Import fixes

## [0.1.6] - 2024

### Added
- requirements.txt file
- GitHub Actions for dependency installation

## Earlier Versions

See git history for details on versions 0.1.5 and earlier.

[Unreleased]: https://github.com/VarSamLewis/unittestplus/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/VarSamLewis/unittestplus/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/VarSamLewis/unittestplus/releases/tag/v1.0.0
[0.2.1]: https://github.com/VarSamLewis/unittestplus/releases/tag/v0.2.1
[0.2.0]: https://github.com/VarSamLewis/unittestplus/releases/tag/v0.2.0
[0.1.8]: https://github.com/VarSamLewis/unittestplus/releases/tag/v0.1.8
[0.1.7]: https://github.com/VarSamLewis/unittestplus/releases/tag/v0.1.7
[0.1.6]: https://github.com/VarSamLewis/unittestplus/releases/tag/v0.1.6
