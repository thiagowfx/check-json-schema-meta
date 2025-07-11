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
        """Test validation of JSON file without $schema key."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "test"}, f)
            f.flush()

            result = validate_json_file(Path(f.name))
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
        """Test main function with invalid JSON files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
            json.dump({"name": "test"}, f1)  # No $schema
            f1.flush()

            with patch("sys.argv", ["check_json_schema_meta", f1.name]):
                result = main()

            Path(f1.name).unlink()

        assert result == 1

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

        assert result == 1  # Should fail due to invalid file

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
