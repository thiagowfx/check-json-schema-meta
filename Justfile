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

# Create a new release
release version:
	@sed -i "s/^version = .*/version = \"{{version}}\"/" pyproject.toml
	@git add pyproject.toml
	@git commit -m "chore: release {{version}}"
	@git tag "v{{version}}"
	@echo "Released {{version}}"
	@echo "Now run: git push --follow-tags"
