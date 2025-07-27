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

# Create a new git tag
release version:
	@OLD_VERSION=$(just --evaluate OLD_VERSION="v$(grep '^version = "' pyproject.toml | cut -d'"' -f2)")
	@sed -i "s/^version = .*/version = \"{{version}}\"/" pyproject.toml
	@uv run git-cliff --tag "{{version}}" --prepend CHANGELOG.md -u -c cliff.toml
	@git add pyproject.toml CHANGELOG.md
	@git commit -m "chore: release {{version}}"
	@git tag "v{{version}}"
	@echo "Released {{version}}"
	@echo "Now run: git push --follow-tags"
