# Makefile for attendance-analyzer
# Uses uv package manager

.PHONY: help install install-uv dev-install update sync clean lint format check test run build docs dev-setup pre-commit

# Default target
help:
	@echo "Available targets:"
	@echo "  install-uv  - Install UV using standalone installer"
	@echo "  install     - Install UV and sync dependencies"
	@echo "  update      - Update all dependencies"
	@echo "  sync        - Sync virtual environment with lock file"
	@echo "  clean       - Clean cache and temporary files"
	@echo "  lint        - Run ruff linter"
	@echo "  format      - Format code with ruff"
	@echo "  check       - Run all checks (lint + format check)"
	@echo "  run         - Run the application"

# Install UV and dependencies
install: install-uv sync

# Install UV using standalone installer
install-uv:
	@echo "Installing UV using standalone installer..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "UV not found, installing..."; \
		if command -v curl >/dev/null 2>&1; then \
			curl -LsSf https://astral.sh/uv/install.sh | sh; \
		elif command -v wget >/dev/null 2>&1; then \
			wget -qO- https://astral.sh/uv/install.sh | sh; \
		else \
			echo "Error: Neither curl nor wget is available. Please install one of them first."; \
			exit 1; \
		fi; \
		echo "UV installed successfully. You may need to restart your shell or run: source ~/.bashrc (or ~/.zshrc)"; \
	else \
		echo "UV is already installed."; \
	fi

# Update dependencies
update:
	uv lock --upgrade

# Sync virtual environment
sync:
	uv sync

# Clean cache and temporary files
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true

# Lint code with ruff
lint:
	uv run ruff check .

# Format code with ruff
format:
	uv run ruff format .

# Check code (lint + format check)
check:
	uv run ruff check .
	uv run ruff format --check .

# Run the application
run:
	uv run python main.py
