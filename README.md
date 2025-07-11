# check-json-schema-meta

A pre-commit hook that validates JSON files contain valid `$schema` references and validates the JSON data against the referenced schema.

> **Note**: This repository serves as a workaround for [python-jsonschema/check-jsonschema#310](https://github.com/python-jsonschema/check-jsonschema/issues/310) - a feature request to add validation of `$schema` references in JSON files.

## Features

- Validates that JSON files contain a `$schema` key
- Loads and validates the referenced JSON Schema (supports both local files and URLs)
- Validates JSON data against the schema
- Exits with non-zero code on errors but checks all files before exiting
- Integrates with pre-commit hooks

## Installation

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Add to your `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/thiagowfx/check-json-schema-meta
       rev: main
       hooks:
         - id: check-json-schema-meta
   ```

## Usage

Direct usage:
```bash
uv run check-json-schema-meta file1.json file2.json
```

## Development

Run tests:
```bash
uv run pytest tests/
```

## Requirements

- Python 3.9+
- check-jsonschema package
