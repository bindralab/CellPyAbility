# Changelog

All notable changes to CellPyAbility will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-20

### Added
- **CLI Interface**: Command-line interface with three subcommands (`gda`, `synergy`, `simple`)
  - All GUI parameters exposed as command-line arguments
  - `--counts-file` flag to bypass CellProfiler for testing
  - `--no-plot` flag for headless execution
  - `--output-dir` flag for custom output locations (defaults to `./cellpyability_output/`)
- **PyPI Package Structure**: Modern Python packaging with `pyproject.toml`
  - Entry point: `cellpyability` command
  - Proper `src/` layout
  - Package metadata and dependencies
  - Strict dependency version bounds to prevent breaking changes (e.g., NumPy <2.0.0)
- **Refactored Analysis Logic**: Core analysis separated from GUI
  - `gda_analysis.py` - dose-response analysis
  - `synergy_analysis.py` - drug combination synergy
  - `simple_analysis.py` - nuclei count matrix
  - All modules support custom output directories
- **Comprehensive Test Suite**:
  - Module I/O validation tests (all passing on Windows/macOS/Linux)
  - CellProfiler subprocess mock tests
  - Test data tables in `tests/data/` for automated validation
  - Example data and outputs moved to `example/` for manual verification
- **Documentation**: 
  - Updated README with separate PyPI and development installation workflows
  - CLI usage examples for all three modules
  - Batch processing examples
  - Testing guide (automated + manual verification)
  - `PYPI_UPLOAD_GUIDE.md` with version immutability warnings and verification steps
  - `CONTRIBUTING.md` for developers
- **CI/CD**: GitHub Actions workflow testing on Ubuntu/macOS/Windows with Python 3.8-3.11
- **Code Quality**: Consistent naming conventions, proper logging, error handling, Windows-compatible output

### Changed
- **BREAKING**: Output directory structure changed for PyPI compatibility
  - Old: Output to `src/cellpyability/gda_output/` (package directory)
  - New: Output to `./cellpyability_output/` (current working directory)
  - Prevents `PermissionError` when installed via `pip install`
- Lazy CellProfiler path initialization for better cross-platform support
- Professional documentation tone throughout (removed casual language)
- Lowercase "gda" in code (uppercase in user documentation)

### Fixed
- **CRITICAL**: Runtime-generated files now write to current working directory (CWD) instead of package directory
  - `cellprofiler_path.txt` - config file in CWD (was in package dir)
  - `cellpyability.log` - log file in CWD (was in package dir)
  - `cellpyability_output/` - all analysis results in CWD
  - Ensures package works in read-only system installations
- `toolbox.py` now copies (not moves) test data files when using `--counts-file`
- Windows test failures due to file lock issues (added robust cleanup with `ignore_errors=True`)
- Windows unicode errors (replaced emojis with ASCII symbols)

### Known Limitations
- Config file (`cellprofiler_path.txt`) created in working directory (may be unexpected UX)
  - Future: Consider moving to `~/.cellpyability/` for cleaner behavior (planned for v0.2.0)

## [0.0.1] - Pre-release

### Added
- Initial GUI-only version
- GDA (dose-response) analysis module
- Synergy analysis module
- Simple count matrix module
- Windows application packaging
- CellProfiler integration

[0.1.0]: https://github.com/bindralab/CellPyAbility/releases/tag/v0.1.0
[0.0.1]: https://github.com/bindralab/CellPyAbility/releases/tag/v0.0.1
