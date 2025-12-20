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
- **PyPI Package Structure**: Modern Python packaging with `pyproject.toml`
  - Entry point: `cellpyability` command
  - Proper `src/` layout
  - Package metadata and dependencies
- **Refactored Analysis Logic**: Core analysis separated from GUI
  - `gda_analysis.py` - dose-response analysis
  - `synergy_analysis.py` - drug combination synergy
  - `simple_analysis.py` - nuclei count matrix
- **Comprehensive Test Suite**:
  - Module I/O validation tests (all passing)
  - CellProfiler subprocess mock tests
  - Test data in `tests/data/` for automated validation
  - Example data in `example/` for manual verification
- **Documentation**: Updated README with CLI usage, batch processing examples, and testing guide
- **Code Quality**: Consistent naming conventions, proper logging, error handling

### Changed
- Lowercase "gda" in code (kept uppercase in user documentation)
- Renamed `test/` directory to `example/` for clarity
- Output directories: `gda_output/`, `synergy_output/`, `simple_output/`
- Lazy CellProfiler path initialization for better cross-platform support

### Fixed
- `toolbox.py` now copies (not moves) test data files when using `--counts-file`
- Proper handling of runtime-generated files (e.g., `cellprofiler_path.txt`)

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
