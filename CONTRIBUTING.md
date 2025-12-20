# Contributing to CellPyAbility

Thank you for your interest in contributing to CellPyAbility! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CellPyAbility.git
   cd CellPyAbility
   ```
3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Run tests** to ensure everything works:
   ```bash
   python tests/test_module_outputs.py
   python tests/test_cellprofiler_subprocess.py
   ```

4. **Commit your changes** with a descriptive message:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

## Code Style Guidelines

- Follow **PEP 8** style guidelines for Python code
- Add **docstrings** to new functions and modules
- Keep functions **focused and single-purpose**
- Use **descriptive variable names**
- Be mindful of **existing namespace**

## Testing Guidelines

### Adding Tests

When adding new features, please include tests:

1. **Module I/O tests**: Add test cases to `tests/test_module_outputs.py`
   - Include any new test data in `tests/data/` with `test_` prefix
   - Ensure outputs match expected files

2. **Example data**: Add any new example data to `example/` with `example_` prefix
   - This helps users manually verify the tool works correctly

3. **Mock tests**: For subprocess calls or external dependencies, use `unittest.mock`

### Running Tests

```bash
# Run all tests
python tests/test_module_outputs.py
python tests/test_cellprofiler_subprocess.py

# Test CLI commands
cellpyability --help
cellpyability gda --help
```

## Documentation

- Update the **README.md** if you add new features or change usage
- Update the **CHANGELOG.md** with your changes (under "Unreleased" section)
- Add **inline comments** when it improves clarity
- Update **CLI help text** if you modify command-line arguments

## Commit Message Guidelines

Use clear, descriptive commit messages:

- **feat**: New feature (e.g., "feat: add batch processing support")
- **fix**: Bug fix (e.g., "fix: correct dilution calculation")
- **docs**: Documentation changes (e.g., "docs: update CLI examples")
- **test**: Adding or updating tests (e.g., "test: add synergy module tests")
- **refactor**: Code refactoring (e.g., "refactor: extract analysis logic")
- **style**: Code style changes (e.g., "style: apply PEP 8 formatting")

## Questions or Issues?

- **Bug reports**: Open an issue on GitHub with a clear description and steps to reproduce
- **Feature requests**: Open an issue describing the feature and its use case
- **Questions**: Open a discussion on GitHub or reach out to james.elia@yale.edu

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
