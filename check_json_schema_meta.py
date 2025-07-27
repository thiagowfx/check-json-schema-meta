#!/usr/bin/env python3
"""Pre-commit hook to validate JSON Schema references in JSON files."""

import argparse
import json
import os
import sys
from pathlib import Path

import jsonschema
from check_jsonschema.schema_loader import SchemaLoader


def validate_json_file(
    file_path: Path, strict: bool = False, expand_env_vars: bool = False
) -> bool:
    """
    Validate a single JSON file's $schema reference.

    Args:
        file_path: Path to the JSON file to validate
        strict: If True, fail on missing $schema. If False, gracefully skip.
        expand_env_vars: If True, expand environment variables in $schema paths.

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

        # Expand environment variables in the schema reference
        if expand_env_vars:
            schema_ref = os.path.expandvars(schema_ref)

        # Load and validate the schema using SchemaLoader's built-in validator
        schema_loader = SchemaLoader(schema_ref)

        # Create a copy of data without $schema for validation
        data_without_schema = {k: v for k, v in data.items() if k != "$schema"}

        # Use SchemaLoader's get_validator method which handles $ref resolution properly
        # and avoids the deprecation warning
        from check_jsonschema.formats import FormatOptions
        from check_jsonschema.regex_variants import (
            RegexImplementation,
            RegexVariantName,
        )

        regex_impl = RegexImplementation(RegexVariantName.default)
        validator = schema_loader.get_validator(
            path=file_path,
            instance_doc=data_without_schema,
            format_opts=FormatOptions(regex_impl=regex_impl),
            regex_impl=regex_impl,
            fill_defaults=False,
        )

        validator.validate(data_without_schema)

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
    parser.add_argument(
        "--expand-env-vars",
        action="store_true",
        help="Expand environment variables in $schema paths (default: false)",
    )
    args = parser.parse_args()

    validation_results = []

    for file_path in args.files:
        path = Path(file_path)

        if not path.exists():
            print(f"❌ {file_path}: File not found")
            validation_results.append(False)
            continue

        # Try to parse as JSON regardless of extension
        try:
            with open(path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError:
            print(f"❌ {file_path}: Not a valid JSON file")
            validation_results.append(False)
            continue

        validation_results.append(
            validate_json_file(path, args.strict, args.expand_env_vars)
        )

    return 0 if all(validation_results) else 1


if __name__ == "__main__":
    sys.exit(main())
