#!/usr/bin/env just --justfile
# https://github.com/casey/just

# List available commands
@_list:
    just --list

# Run all pre-commit hooks in all files
lint:
	pre-commit run --all-files

# Run all unit tests
test:
	uv run pytest
