#!/bin/bash
# Run test presentations for Presenton Enhancement-11

set -e

echo "=========================================="
echo "Presenton Test Presentations Runner"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if the API is running
echo "Checking if Presenton API is running..."
if ! curl -s http://localhost:5001/api/v1/ppt/presentation/all > /dev/null 2>&1; then
    echo "Error: Presenton API is not running on http://localhost:5001"
    echo "Please start the container with: docker-compose up -d"
    exit 1
fi

echo "✓ API is running"
echo ""

# Run the test script
echo "Starting test presentations..."
cd /home/usdaw/presenton
python3 test_presentations.py

# Check if results file was created
if [ -f "test_results_presentations.txt" ]; then
    echo ""
    echo "=========================================="
    echo "Test Results Summary"
    echo "=========================================="
    tail -20 test_results_presentations.txt
else
    echo "Error: Results file was not created"
    exit 1
fi
