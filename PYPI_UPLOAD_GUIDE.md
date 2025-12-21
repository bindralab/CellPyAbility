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

**CRITICAL NOTE**: PyPI and TestPyPI version numbers are **immutable**. Once you upload version `0.1.0`, you cannot upload it again, even after fixing bugs. Version numbers cannot be deleted or reused.

**Best Practice**: If you find issues during testing, you MUST bump the version number before rebuilding:
- Development versions: `0.1.0.dev1`, `0.1.0.dev2`, etc.
- Release candidates: `0.1.0rc1`, `0.1.0rc2`, etc.
- Patch versions: `0.1.1`, `0.1.2`, etc.

Update the version in **both** `src/cellpyability/__init__.py` and `pyproject.toml` before rebuilding.

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
   
   # Verify the version matches what you expect
   python -c "import cellpyability; print(cellpyability.__version__)"
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

1. **Update version in BOTH locations** (keep them synchronized):
   - `src/cellpyability/__init__.py`: Change `__version__ = "0.1.0"` to new version
   - `pyproject.toml`: Change `version = "0.1.0"` to match
   
   **Verification**: After updating, check they match:
   ```bash
   # Extract version from pyproject.toml
   grep 'version = ' pyproject.toml
   
   # Extract version from __init__.py
   grep '__version__' src/cellpyability/__init__.py
   ```

2. Update `CHANGELOG.md` with changes

3. Rebuild and upload:
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   python -m build
   
   # Double-check version is correct before uploading
   python -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])"
   
   twine upload dist/*
   ```

4. **Verify after publication**:
   ```bash
   pip install --upgrade cellpyability
   python -c "import cellpyability; print(cellpyability.__version__)"
   ```

## Troubleshooting

### Version Synchronization

**Critical**: The version number must match in both files:
- `src/cellpyability/__init__.py`: `__version__ = "0.1.0"`
- `pyproject.toml`: `version = "0.1.0"`

**Verify synchronization**:
```bash
# Check both versions are identical
python -c "
import tomli
with open('pyproject.toml', 'rb') as f:
    toml_version = tomli.load(f)['project']['version']
    
with open('src/cellpyability/__init__.py') as f:
    for line in f:
        if '__version__' in line:
            py_version = line.split('=')[1].strip().strip('\"')
            break
            
if toml_version == py_version:
    print(f'✓ Versions match: {toml_version}')
else:
    print(f'✗ VERSION MISMATCH: pyproject.toml={toml_version}, __init__.py={py_version}')
    exit(1)
"
```

**After installation**, verify the installed version:
```bash
pip install cellpyability
python -c "import cellpyability; print(f'Installed version: {cellpyability.__version__}')"
```

### Build Warnings

The package may show warnings about `license-file` metadata during build. These are **non-critical** and don't prevent installation or upload. The package is fully functional.

### Runtime-Generated Files

The package creates configuration and log files in the current working directory (PyPI-compatible):
- `cellprofiler_path.txt` - Created on first run when CellProfiler path needs to be saved
- `cellpyability.log` - Debug log file created during each run
- `cellpyability_output/` - Directory containing all analysis results

All these files are created in the user's working directory, not in the package installation directory, ensuring compatibility with read-only system installations.

**Design Note**: The config file (`cellprofiler_path.txt`) is created in the current working directory. While this works, it means:
- ✅ **Pros**: No permission issues, works in any environment
- ⚠️ **Consideration**: Config file appears in user's working folder (e.g., Desktop if they run commands there)

**Future Enhancement (v0.2.0)**: Consider moving config to user's home directory (`~/.cellpyability/config.txt`) for cleaner behavior, similar to tools like `~/.ssh/` or `~/.aws/`. This would make the config persist globally regardless of working directory.

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
