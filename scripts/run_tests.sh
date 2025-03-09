#!/bin/bash

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest --cov=app tests/ --cov-report=term --cov-report=html

# Open coverage report if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    open htmlcov/index.html
fi

echo "Tests completed. Coverage report generated in htmlcov/ directory." 