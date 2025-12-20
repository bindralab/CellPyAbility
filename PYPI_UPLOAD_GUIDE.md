# PyPI Publication Guide

This guide explains how to publish CellPyAbility to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens**: Generate API tokens for uploads:
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/
   - Save tokens securely (they won't be shown again)

3. **Install Build Tools**:
   ```bash
   pip install --upgrade build twine
   ```

## Building the Package

1. **Clean Previous Builds**:
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   ```

2. **Build the Package**:
   ```bash
   python -m build
   ```

   This creates two files in `dist/`:
   - `cellpyability-0.1.0.tar.gz` (source distribution)
   - `cellpyability-0.1.0-py3-none-any.whl` (wheel distribution)

3. **Check the Build** (optional - may show warnings about metadata but package works):
   ```bash
   twine check dist/*
   ```

## Testing on TestPyPI (Recommended First Step)

1. **Upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

   When prompted:
   - Username: `__token__`
   - Password: Your TestPyPI API token (including the `pypi-` prefix)

2. **Test Installation**:
   ```bash
   # Create a fresh virtual environment
   python -m venv test_env
   source test_env/bin/activate  # On Windows: test_env\Scripts\activate

   # Install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cellpyability

   # Test the CLI
   cellpyability --help
   cellpyability gda --help
   ```

3. **If Testing Succeeds**, proceed to PyPI upload.

## Publishing to PyPI

1. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

   When prompted:
   - Username: `__token__`
   - Password: Your PyPI API token (including the `pypi-` prefix)

2. **Verify Installation**:
   ```bash
   pip install cellpyability
   cellpyability --help
   ```

3. **View on PyPI**:
   - Your package will be available at: https://pypi.org/project/cellpyability/

## Using .pypirc for Authentication (Optional)

To avoid entering credentials each time, create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Security Note**: Keep this file secure (`chmod 600 ~/.pypirc` on Unix).

## Post-Publication

1. **Create a GitHub Release**:
   - Tag the commit: `git tag v0.1.0`
   - Push the tag: `git push origin v0.1.0`
   - Create a release on GitHub with release notes from CHANGELOG.md

2. **Update Documentation**:
   - Add PyPI installation instructions to README
   - Update shields/badges to show PyPI version

3. **Monitor**:
   - Watch for issues reported on PyPI
   - Check download stats (after a few days)

## Updating the Package

When releasing a new version:

1. Update version in `src/cellpyability/__init__.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Rebuild and upload:
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   python -m build
   twine upload dist/*
   ```

## Troubleshooting

### Build Warnings

The package may show warnings about `license-file` metadata during build. These are **non-critical** and don't prevent installation or upload. The package is fully functional.

### Runtime-Generated Files

The package creates configuration and log files in the current working directory (PyPI-compatible):
- `cellprofiler_path.txt` - Created on first run when CellProfiler path needs to be saved
- `cellpyability.log` - Debug log file created during each run
- `cellpyability_output/` - Directory containing all analysis results

All these files are created in the user's working directory, not in the package installation directory, ensuring compatibility with read-only system installations.

### No Permission Issues

The package is designed to work correctly in read-only environments:
- NO writes to package installation directory
- All output to current working directory by default
- Works in virtual environments, user installations, and system-wide installations

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [TestPyPI](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
