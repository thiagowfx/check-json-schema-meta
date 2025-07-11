#!/usr/bin/env python3
"""
Pre-commit hook to validate JSON Schema references in JSON files.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from check_jsonschema.schema_loader import SchemaLoader


def validate_json_file(file_path: Path) -> bool:
    """
    Validate a single JSON file's $schema reference.
    
    Args:
        file_path: Path to the JSON file to validate
        
    Returns:
        True if validation passes, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        schema_ref = data.get('$schema')
        if not schema_ref:
            print(f"Error: {file_path} does not contain a '$schema' key")
            return False
        
        # Load and validate the schema
        schema_loader = SchemaLoader(schema_ref)
        schema = schema_loader.get_schema()
        
        # Validate the JSON data against the schema
        import jsonschema
        jsonschema.validate(data, schema)
        
        print(f"✓ {file_path}: Schema validation passed")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: {file_path} is not valid JSON: {e}")
        return False
    except Exception as e:
        print(f"Error: {file_path} failed schema validation: {e}")
        return False


def main() -> int:
    """
    Main entry point for the pre-commit hook.
    
    Returns:
        0 on success, 1 on failure
    """
    parser = argparse.ArgumentParser(
        description="Validate JSON Schema references in JSON files"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="JSON files to validate"
    )
    
    args = parser.parse_args()
    
    all_valid = True
    
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File {file_path} does not exist")
            all_valid = False
            continue
            
        if not path.suffix.lower() == '.json':
            print(f"Warning: {file_path} is not a JSON file, skipping")
            continue
            
        if not validate_json_file(path):
            all_valid = False
    
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())