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

        assert result == 0  # Should succeed but skip non-JSON files

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
