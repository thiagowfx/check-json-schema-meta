# check-json-schema-meta

A pre-commit hook that validates JSON files contain valid `$schema` references and validates the JSON data against the referenced schema.

> **Note**: This repository serves as a workaround for [python-jsonschema/check-jsonschema#310](https://github.com/python-jsonschema/check-jsonschema/issues/310) - a feature request to add validation of `$schema` references in JSON files.

## Features

- Validates that JSON files contain a `$schema` key (gracefully skips by default)
- Loads and validates the referenced JSON Schema (supports both local files and URLs)
- Validates JSON data against the schema
- `--strict` flag to make missing `$schema` fail validation
- Exits with non-zero code on errors but checks all files before exiting
- Integrates with pre-commit hooks
- Supports validating JSON files against a schema specified by the `$schema` key.
- **NEW:** If the `$schema` key is missing, you can set the `JSON_SCHEMA_URL` environment variable to provide a default schema reference for validation.

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

### Pre-commit Hook Usage

One-shot preview (trial):

```shell
pre-commit try-repo https://github.com/thiagowfx/check-json-schema-meta check-json-schema-meta --all
```

Basic configuration in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/thiagowfx/check-json-schema-meta
    rev: main  replace with the latest tag
    hooks:
      - id: check-json-schema-meta
```

With strict mode enabled:

```yaml
repos:
  - repo: https://github.com/thiagowfx/check-json-schema-meta
    rev: main  replace with the latest tag
    hooks:
      - id: check-json-schema-meta
        args: ['--strict']
```

Run pre-commit hooks:

```bash
# Install pre-commit hooks
pre-commit install

# Run only this specific hook
pre-commit run [--all-files] check-json-schema-meta
```

If your JSON files do not include a `$schema` key, you can set the environment variable `JSON_SCHEMA_URL` to specify a default schema to use for validation:

```bash
export JSON_SCHEMA_URL="https://example.com/your-default-schema.json"
pre-commit run --all-files
```

### Direct Usage

```bash
# Default behavior - gracefully skip files without $schema
uv run check-json-schema-meta file1.json file2.json

# Strict mode - fail on missing $schema
uv run check-json-schema-meta --strict file1.json file2.json
```

### Options

- `--strict`: Make missing `$schema` fail validation. By default, files without `$schema` are gracefully skipped.

## Development

Run tests:

```bash
uv run pytest
```

## Requirements

- Python 3.9+
- check-jsonschema package
