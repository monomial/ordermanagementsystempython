#!/bin/bash

# Run schema tests with coverage
echo "Running schema tests with coverage..."
python -m pytest tests/unit/test_schemas.py tests/unit/test_v2_schemas.py --cov=app.schemas --cov-report=term --cov-report=html

# Open coverage report if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    open htmlcov/index.html
fi

echo "Tests completed. Coverage report generated in htmlcov/ directory." 