"""Unit tests for check_json_schema_meta module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from check_json_schema_meta import main, validate_json_file


class TestValidateJsonFile:
    """Test the validate_json_file function."""

    def test_valid_json_with_schema(self) -> None:
        """Test validation of a valid JSON file with proper schema."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
                f,
            )
            f.flush()

            result = validate_json_file(Path(f.name))
            Path(f.name).unlink()

        assert result is True

    def test_json_without_schema(self) -> None:
        """Test validation of JSON file without $schema key (default behavior)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "test"}, f)
            f.flush()

            result = validate_json_file(Path(f.name))
            Path(f.name).unlink()

        assert result is True  # Default behavior is to gracefully skip

    def test_json_without_schema_non_strict(self) -> None:
        """Test validation of JSON file without $schema key in non-strict mode."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "test"}, f)
            f.flush()

            result = validate_json_file(Path(f.name), strict=False)
            Path(f.name).unlink()

        assert result is True

    def test_json_without_schema_strict(self) -> None:
        """Test validation of JSON file without $schema key in strict mode."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "test"}, f)
            f.flush()

            result = validate_json_file(Path(f.name), strict=True)
            Path(f.name).unlink()

        assert result is False

    def test_invalid_json(self) -> None:
        """Test validation of invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            f.flush()

            result = validate_json_file(Path(f.name))
            Path(f.name).unlink()

        assert result is False

    def test_invalid_schema_reference(self) -> None:
        """Test validation with invalid schema reference."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "$schema": "https://invalid-schema-url.com/nonexistent.json",
                    "name": "test",
                },
                f,
            )
            f.flush()

            result = validate_json_file(Path(f.name))
            Path(f.name).unlink()

        assert result is False

    def test_schema_property_not_rejected(self) -> None:
        """Test that $schema property itself is not rejected as additional property."""
        # First create a strict schema that doesn't allow additional properties
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as schema_file:
            schema_data = {
                "$schema": "https://json-schema.org/draft/2019-09/schema",
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "additionalProperties": False,
            }
            json.dump(schema_data, schema_file)
            schema_file.flush()
            schema_url = f"file://{schema_file.name}"

            # Now create a JSON document that references this strict schema
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as data_file:
                json.dump(
                    {
                        "$schema": schema_url,
                        "name": "test value",  # Only this property should be allowed
                    },
                    data_file,
                )
                data_file.flush()

                # This should pass because $schema is excluded from validation
                result = validate_json_file(Path(data_file.name))
                Path(data_file.name).unlink()

            Path(schema_file.name).unlink()

        assert result is True

    def test_schema_store_host_json_with_refs(self) -> None:
        """Test validation of host.json with schema store schema that contains $ref."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "$schema": "https://www.schemastore.org/schemas/json/host.json",
                    "version": "2.0",
                },
                f,
            )
            f.flush()

            result = validate_json_file(Path(f.name))
            Path(f.name).unlink()

        assert result is True

    def test_schema_store_package_json_with_refs(self) -> None:
        """Test validation of package.json with schema store schema that contains $ref.

        Uses a real production package.json configuration to test $ref resolution.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "$schema": "https://www.schemastore.org/schemas/json/package.json",
                    "name": "test-package",
                    "version": "1.0.0",
                    "description": "A test package for schema validation",
                    "main": "index.js",
                    "scripts": {
                        "test": "echo \"Error: no test specified\" && exit 1"
                    },
                    "keywords": ["test"],
                    "author": "Test Author",
                    "license": "MIT"
                },
                f,
            )
            f.flush()

            result = validate_json_file(Path(f.name))
            Path(f.name).unlink()

        assert result is True

    def test_local_schema_with_refs(self) -> None:
        """Test validation with local schema that uses $ref to demonstrate ref resolution.

        This test creates two schema files where one references the other via $ref.
        Without proper $ref resolution, validation would fail.
        """
        # Create a definitions schema file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as def_schema:
            definitions = {
                "$schema": "https://json-schema.org/draft/2019-09/schema",
                "$id": "https://example.com/definitions.json",
                "definitions": {
                    "person": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer", "minimum": 0},
                        },
                        "required": ["name", "age"],
                    }
                },
            }
            json.dump(definitions, def_schema)
            def_schema.flush()
            def_schema_url = f"file://{def_schema.name}"

            # Create a main schema that references the definitions
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as main_schema:
                main_schema_data = {
                    "$schema": "https://json-schema.org/draft/2019-09/schema",
                    "$id": "https://example.com/team.json",
                    "type": "object",
                    "properties": {
                        "team_name": {"type": "string"},
                        "members": {
                            "type": "array",
                            "items": {"$ref": f"{def_schema_url}#/definitions/person"},
                        },
                    },
                    "required": ["team_name", "members"],
                }
                json.dump(main_schema_data, main_schema)
                main_schema.flush()
                main_schema_url = f"file://{main_schema.name}"

                # Create a test JSON file that should validate against the schema
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as test_file:
                    test_data = {
                        "$schema": main_schema_url,
                        "team_name": "Development Team",
                        "members": [
                            {"name": "Alice", "age": 30},
                            {"name": "Bob", "age": 25},
                        ],
                    }
                    json.dump(test_data, test_file)
                    test_file.flush()

                    # This should pass because $ref resolution works
                    result = validate_json_file(Path(test_file.name))
                    Path(test_file.name).unlink()

                Path(main_schema.name).unlink()
            Path(def_schema.name).unlink()

        assert result is True

    def test_local_schema_with_refs_validation_failure(self) -> None:
        """Test that $ref resolution properly validates and catches errors.

        This test demonstrates that with proper $ref resolution, validation errors
        in referenced schemas are correctly detected.
        """
        # Create a definitions schema file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as def_schema:
            definitions = {
                "$schema": "https://json-schema.org/draft/2019-09/schema",
                "$id": "https://example.com/definitions.json",
                "definitions": {
                    "person": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer", "minimum": 0},
                        },
                        "required": ["name", "age"],
                    }
                },
            }
            json.dump(definitions, def_schema)
            def_schema.flush()
            def_schema_url = f"file://{def_schema.name}"

            # Create a main schema that references the definitions
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as main_schema:
                main_schema_data = {
                    "$schema": "https://json-schema.org/draft/2019-09/schema",
                    "$id": "https://example.com/team.json",
                    "type": "object",
                    "properties": {
                        "team_name": {"type": "string"},
                        "members": {
                            "type": "array",
                            "items": {"$ref": f"{def_schema_url}#/definitions/person"},
                        },
                    },
                    "required": ["team_name", "members"],
                }
                json.dump(main_schema_data, main_schema)
                main_schema.flush()
                main_schema_url = f"file://{main_schema.name}"

                # Create a test JSON file with invalid data (missing required field)
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as test_file:
                    test_data = {
                        "$schema": main_schema_url,
                        "team_name": "Development Team",
                        "members": [
                            {"name": "Alice", "age": 30},
                            {"name": "Bob"},  # Missing required 'age' field
                        ],
                    }
                    json.dump(test_data, test_file)
                    test_file.flush()

                    # This should fail because of validation error in referenced schema
                    result = validate_json_file(Path(test_file.name))
                    Path(test_file.name).unlink()

                Path(main_schema.name).unlink()
            Path(def_schema.name).unlink()

        assert result is False


class TestMain:
    """Test the main function."""

    def test_main_with_valid_files(self) -> None:
        """Test main function with valid JSON files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
            json.dump(
                {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "string",
                },
                f1,
            )
            f1.flush()

            with patch("sys.argv", ["check_json_schema_meta", f1.name]):
                result = main()

            Path(f1.name).unlink()

        assert result == 0

    def test_main_with_invalid_files(self) -> None:
        """Test main function with invalid JSON files (default behavior)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
            json.dump({"name": "test"}, f1)  # No $schema
            f1.flush()

            with patch("sys.argv", ["check_json_schema_meta", f1.name]):
                result = main()

            Path(f1.name).unlink()

        assert result == 0  # Default behavior is to gracefully skip

    def test_main_with_nonexistent_file(self) -> None:
        """Test main function with nonexistent file."""
        with patch("sys.argv", ["check_json_schema_meta", "nonexistent.json"]):
            result = main()

        assert result == 1

    def test_main_with_non_json_file(self) -> None:
        """Test main function with non-JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f1:
            f1.write("not json")
            f1.flush()

            with patch("sys.argv", ["check_json_schema_meta", f1.name]):
                result = main()

            Path(f1.name).unlink()

        assert result == 1  # Should fail on invalid JSON files

    def test_main_with_json_file_no_extension(self) -> None:
        """Test main function with JSON file without .json extension."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".babelrc", delete=False
        ) as f1:
            json.dump(
                {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "presets": ["@babel/preset-env"],
                },
                f1,
            )
            f1.flush()

            with patch("sys.argv", ["check_json_schema_meta", f1.name]):
                result = main()

            Path(f1.name).unlink()

        assert result == 0  # Should succeed and validate the JSON file

    def test_main_with_strict_flag(self) -> None:
        """Test main function with --strict flag and missing schema."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
            json.dump({"name": "test"}, f1)  # No $schema
            f1.flush()

            with patch("sys.argv", ["check_json_schema_meta", "--strict", f1.name]):
                result = main()

            Path(f1.name).unlink()

        assert result == 1  # Should fail with --strict

    def test_main_without_strict_flag(self) -> None:
        """Test main function without --strict flag and missing schema."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
            json.dump({"name": "test"}, f1)  # No $schema
            f1.flush()

            with patch("sys.argv", ["check_json_schema_meta", f1.name]):
                result = main()

            Path(f1.name).unlink()

        assert result == 0  # Should succeed without --strict

    def test_main_with_mixed_files(self) -> None:
        """Test main function with mix of valid and invalid files."""
        with (
            tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1,
            tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f2,
        ):
            # Valid file
            json.dump(
                {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "string",
                },
                f1,
            )
            f1.flush()

            # Invalid file (no schema)
            json.dump({"name": "test"}, f2)
            f2.flush()

            with patch("sys.argv", ["check_json_schema_meta", f1.name, f2.name]):
                result = main()

            Path(f1.name).unlink()
            Path(f2.name).unlink()

        assert result == 0  # Should succeed in non-strict mode

    def test_renovate_json_with_schema(self) -> None:
        """Test validation of renovate.json with proper schema."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "$schema": "https://docs.renovatebot.com/renovate-schema.json",
                    "extends": ["config:recommended"],
                    "packageRules": [
                        {"matchUpdateTypes": ["minor", "patch"], "automerge": True}
                    ],
                },
                f,
            )
            f.flush()

            result = validate_json_file(Path(f.name))
            Path(f.name).unlink()

        assert result is True

    def test_json_array_non_strict(self) -> None:
        """Test validation of JSON array in non-strict mode."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"name": "item1"}, {"name": "item2"}], f)
            f.flush()

            result = validate_json_file(Path(f.name), strict=False)
            Path(f.name).unlink()

        assert result is True

    def test_json_array_strict(self) -> None:
        """Test validation of JSON array in strict mode."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"name": "item1"}, {"name": "item2"}], f)
            f.flush()

            result = validate_json_file(Path(f.name), strict=True)
            Path(f.name).unlink()

        assert result is False
