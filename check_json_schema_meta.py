#!/usr/bin/env python3
"""Pre-commit hook to validate JSON Schema references in JSON files."""

import argparse
import json
import sys
from pathlib import Path

import jsonschema
from check_jsonschema.schema_loader import SchemaLoader


def validate_json_file(file_path: Path, strict: bool = False) -> bool:
    """
    Validate a single JSON file's $schema reference.

    Args:
        file_path: Path to the JSON file to validate
        strict: If True, fail on missing $schema. If False, gracefully skip.

    Returns:
        True if validation passes, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle case where JSON is an array instead of an object
        if isinstance(data, list):
            if strict:
                print(f"❌ {file_path}: JSON array does not support '$schema' key")
                return False
            else:
                return True

        schema_ref = data.get("$schema")
        if not schema_ref:
            if strict:
                print(f"❌ {file_path}: Missing '$schema' key")
                return False
            else:
                return True

        # Load and validate the schema
        schema_loader = SchemaLoader(schema_ref)
        schema = schema_loader.get_schema()
        jsonschema.validate(data, schema)

        print(f"✅ {file_path}: Schema validation passed")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ {file_path}: Invalid JSON - {e}")
        return False
    except jsonschema.ValidationError as e:
        # Format validation error more clearly
        if e.absolute_path:
            path_str = ".".join(str(p) for p in e.absolute_path)
            print(f"❌ {file_path}: Invalid value at '{path_str}' - {e.message}")
        else:
            print(f"❌ {file_path}: Schema validation failed - {e.message}")
        return False
    except Exception as e:
        print(f"❌ {file_path}: {e}")
        return False


def main() -> int:
    """
    Entry point for the pre-commit hook.

    Returns:
        0 on success, 1 on failure
    """
    parser = argparse.ArgumentParser(
        description="Validate JSON Schema references in JSON files",
        epilog="""
Usage examples:
  %(prog)s file1.json file2.json
  %(prog)s --strict *.json
  %(prog)s --help
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="+", help="JSON files to validate")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing $schema (default: gracefully skip)",
    )
    args = parser.parse_args()

    validation_results = []

    for file_path in args.files:
        path = Path(file_path)

        if not path.exists():
            print(f"❌ {file_path}: File not found")
            validation_results.append(False)
            continue

        if path.suffix.lower() != ".json":
            print(f"⚠️  {file_path}: Not a JSON file, skipping")
            continue

        validation_results.append(validate_json_file(path, args.strict))

    return 0 if all(validation_results) else 1


if __name__ == "__main__":
    sys.exit(main())
