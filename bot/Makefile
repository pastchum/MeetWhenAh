# Makefile for MeetWhenAh Bot Testing
# Provides convenient commands for running tests

.PHONY: help test test-unit test-integration test-e2e test-coverage test-html test-parallel clean install

# Default target
help:
	@echo "MeetWhenAh Bot Testing Commands:"
	@echo ""
	@echo "  make test              Run all tests"
	@echo "  make test-unit         Run unit tests only"
	@echo "  make test-integration  Run integration tests only"
	@echo "  make test-e2e          Run end-to-end tests only"
	@echo "  make test-coverage     Run tests with coverage report"
	@echo "  make test-html         Run tests with HTML report"
	@echo "  make test-parallel     Run tests in parallel"
	@echo "  make test-fast         Run fast tests only (unit + integration)"
	@echo "  make clean             Clean test artifacts"
	@echo "  make install           Install test dependencies"
	@echo ""

# Install dependencies
install:
	@echo "Installing test dependencies..."
	pip install -r requirements.txt

# Run all tests
test:
	@echo "Running all tests..."
	python -m pytest tests/ -v

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	python -m pytest tests/ -m "unit" -v

# Run integration tests only
test-integration:
	@echo "Running integration tests..."
	python -m pytest tests/ -m "integration" -v

# Run end-to-end tests only
test-e2e:
	@echo "Running end-to-end tests..."
	python -m pytest tests/ -m "e2e" -v

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html:htmlcov -v

# Run tests with HTML report
test-html:
	@echo "Running tests with HTML report..."
	python -m pytest tests/ --html=reports/test_report.html --self-contained-html -v

# Run tests in parallel
test-parallel:
	@echo "Running tests in parallel..."
	python -m pytest tests/ -n auto -v

# Run fast tests only
test-fast:
	@echo "Running fast tests..."
	python -m pytest tests/ -m "unit or integration" -v

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run specific test file
test-file:
	@echo "Usage: make test-file FILE=test_mini_app_url.py"
	python -m pytest tests/$(FILE) -v

# Run tests with specific marker
test-marker:
	@echo "Usage: make test-marker MARKER=slow"
	python -m pytest tests/ -m $(MARKER) -v

# Debug mode
test-debug:
	@echo "Running tests in debug mode..."
	python -m pytest tests/ -v -s --pdb

# Watch mode (requires pytest-watch)
test-watch:
	@echo "Running tests in watch mode..."
	ptw tests/ --runner "python -m pytest tests/ -v"
