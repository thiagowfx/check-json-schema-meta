# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python pre-commit hook tool that validates JSON files contain valid `$schema` references and validates the JSON data against the referenced schema. It serves as a workaround for a missing feature in the `check-jsonschema` package.

## Development Commands

### Dependencies and Environment
```bash
# Install dependencies using uv
uv sync

# Run the tool directly
uv run check-json-schema-meta file1.json file2.json
uv run check-json-schema-meta --strict file1.json file2.json
```

### Testing
```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_check_json_schema_meta.py

# Run with verbose output
uv run pytest tests/ -v
```

### Code Quality Tools
The project uses several formatting and linting tools configured in `pyproject.toml`:

- **Black**: Code formatting (target Python 3.9+)
- **isort**: Import sorting (black profile)
- **Bandit**: Security analysis (excludes tests/, skips B101)
- **Pre-commit**: Git hooks for code quality

Check the pre-commit configuration and run hooks manually:
```bash
pre-commit install
pre-commit run --all-files
```

## Architecture

### Core Module: `check_json_schema_meta.py`
Single-file implementation with two main functions:

- `validate_json_file(file_path, strict=False)`: Validates individual JSON files
  - Loads JSON and checks for `$schema` key
  - Uses `check_jsonschema.schema_loader.SchemaLoader` to load referenced schemas
  - Validates data against schema using `jsonschema.validate()`
  - Handles JSON arrays gracefully (skips validation unless `--strict`)
  - Returns boolean success/failure

- `main()`: CLI entry point
  - Argument parsing with `argparse`
  - Processes multiple files and accumulates results
  - Supports `--strict` flag to fail on missing `$schema`
  - Exits with code 0 (success) or 1 (failure)

### Test Structure: `tests/test_check_json_schema_meta.py`
Comprehensive test suite using:
- `tempfile.NamedTemporaryFile` for creating test JSON files
- `unittest.mock.patch` for mocking `sys.argv` in CLI tests
- Pytest with class-based organization (`TestValidateJsonFile`, `TestMain`)

Test coverage includes:
- Valid/invalid JSON files
- Missing/invalid schema references
- Strict vs non-strict modes
- JSON arrays vs objects
- Real-world examples (renovate.json)
- File handling edge cases

## Key Dependencies

- `check-jsonschema`: For loading JSON schemas from URLs/files
- `jsonschema`: For validating JSON data against schemas
- `pytest`: Testing framework

## Pre-commit Hook Configuration

The tool is designed to be used as a pre-commit hook. The hook configuration is defined in the repository for external use:
- Hook ID: `check-json-schema-meta`
- Language: `python`
- Entry point: CLI script defined in `pyproject.toml`
