# check-json-schema-meta

A pre-commit hook that validates JSON files contain valid `$schema` references and validates the JSON data against the referenced schema.

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
     - repo: /path/to/check-json-schema-meta
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

- Python 3.11+
- check-jsonschema package