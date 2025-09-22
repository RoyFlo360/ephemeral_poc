# Integration Tests

This directory contains integration tests that test the system as a whole, including database connections, performance, and web browser automation.

## Test Types

### PostgreSQL Tests
- **test_postgres_connection.py**: Tests basic database connectivity and operations
- **test_postgres_performance.py**: Tests database performance, indexing, and concurrency
- **test_postgres_transactions.py**: Tests transaction handling and rollback scenarios

### Selenium Browser Tests
- **tests/browser_tests/**: Contains Selenium browser automation tests in a separate directory

## Running the Tests

### PostgreSQL Tests
```bash
# Run PostgreSQL integration tests
docker-compose -f docker-compose.integration.yml up --build

# Or use the test runner
python test_runner.py integration
```

### Selenium Tests
```bash
# Run Selenium tests
docker-compose -f docker-compose.selenium.yml up --build

# Or use the test runner
python test_runner.py selenium
```

### All Tests
```bash
# Run all tests sequentially
python test_runner.py all
```

## Test Results

Test results are stored in the `test-results/` directory:
- `test-results/integration/` - PostgreSQL test results
- `test-results/selenium/` - Selenium test results

## Selenium Test Details

The Selenium tests run in a headless Chrome browser container and test:
1. **Basic webpage loading** - Verifies page loading, title, and content
2. **Form interaction** - Tests form filling, validation, and element interaction

These tests use httpbin.org as test targets to avoid external dependencies.
