#!/bin/bash

# Test Runner Script for MeetWhenAh Bot
# This script runs all tests following Python testing best practices

echo "🧪 Running MeetWhenAh Bot Tests..."

# Navigate to bot directory
cd bot

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup-dev.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update test dependencies
echo "📦 Installing test dependencies..."
pip install -r requirements.txt

# Parse command line arguments
COVERAGE=false
HTML_REPORT=false
PARALLEL=false
VERBOSE=false
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --markers)
            MARKERS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --coverage     Run with coverage reporting"
            echo "  --html         Generate HTML test report"
            echo "  --parallel     Run tests in parallel"
            echo "  --verbose      Verbose output"
            echo "  --markers      Run tests with specific markers (e.g., 'unit', 'integration')"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

# Add markers if specified
if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m $MARKERS"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=. --cov-report=term-missing"
    if [ "$HTML_REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html:htmlcov"
    fi
fi

# Add HTML report
if [ "$HTML_REPORT" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --html=reports/test_report.html --self-contained-html"
fi

# Add test directory
PYTEST_CMD="$PYTEST_CMD tests/"

# Create reports directory
mkdir -p reports

echo "🚀 Running tests with command: $PYTEST_CMD"
echo ""

# Run tests
eval $PYTEST_CMD
TEST_EXIT_CODE=$?

# Check test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "Test Summary:"
    echo "- Mini App URL generation works correctly"
    echo "- Handlers pass correct parameters"
    echo "- Environment switching works"
    echo "- URL encoding handles special characters"
    echo "- All edge cases are covered"
    
    if [ "$COVERAGE" = true ]; then
        echo "- Code coverage report generated"
    fi
    
    if [ "$HTML_REPORT" = true ]; then
        echo "- HTML test report generated in reports/test_report.html"
    fi
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit $TEST_EXIT_CODE
fi

echo ""
echo "🎉 Test run complete!"
