# Ephemeral POC - Test Suite

This project provides a comprehensive test suite with unit tests, integration tests, and Selenium browser tests, all running in Docker containers for consistent and isolated testing environments.

## 🏗️ Project Structure

```
ephemeral_poc/
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/            # Integration tests
│   │   └── test_postgres_*.py  # PostgreSQL tests
│   └── browser_tests/          # Selenium browser tests
├── docker-compose.integration.yml  # PostgreSQL integration tests
├── docker-compose.selenium.yml     # Selenium browser tests
├── dockerfile.integration          # PostgreSQL test container
├── dockerfile.selenium             # Selenium test container
├── dockerfile.unit_test            # Unit test container
├── test_runner.py                  # Main test runner
├── run_selenium_tests.py           # Selenium test runner
└── requirements.txt                 # Python dependencies
```

## 🧪 Test Types

### 1. Unit Tests
- Run in isolated containers
- Test individual components
- Fast execution
- No external dependencies

### 2. Integration Tests (PostgreSQL)
- Test database connectivity and operations
- Performance testing with bulk operations
- Transaction handling and concurrency
- Index performance analysis

### 3. Selenium Browser Tests
- Headless Chrome browser automation
- Web page loading and validation
- Form interaction and element testing
- System-level web testing

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for local development)

### Running All Tests
```bash
# Run all tests sequentially
python test_runner.py all

# Or run specific test types
python test_runner.py unit        # Unit tests only
python test_runner.py integration # PostgreSQL tests only
python test_runner.py selenium    # Selenium tests only
```

### Running Individual Test Suites

#### Unit Tests
```bash
docker build -f dockerfile.unit_test -t unit-test .
docker run --rm unit-test
```

#### PostgreSQL Integration Tests
```bash
docker-compose -f docker-compose.integration.yml up --build
```

#### Selenium Tests
```bash
# Using Docker Compose
docker-compose -f docker-compose.selenium.yml up --build

# Using the dedicated script
python run_selenium_tests.py
```

## 📊 Test Results

Test results are stored in the `test-results/` directory:
- `test-results/unit/` - Unit test results
- `test-results/integration/` - PostgreSQL test results  
- `test-results/selenium/` - Selenium test results

Results are generated in JUnit XML format for CI/CD integration.

## 🔧 Configuration

### Environment Variables
- `POSTGRES_HOST`: PostgreSQL host (default: `postgres`)
- `POSTGRES_PORT`: PostgreSQL port (default: `5432`)
- `POSTGRES_DB`: Database name (default: `test`)
- `POSTGRES_USER`: Database user (default: `test`)
- `POSTGRES_PASSWORD`: Database password (default: `test`)

### Docker Configuration
- **Integration Tests**: Uses PostgreSQL 14 with health checks
- **Selenium Tests**: Uses Chrome browser with ChromeDriver in headless mode
- **Unit Tests**: Minimal Python environment for fast execution

## 🧪 Selenium Test Details

The Selenium tests provide system-level web testing capabilities:

1. **Basic Webpage Loading Test**
   - Navigates to httpbin.org
   - Verifies page title and content
   - Checks page loading completion

2. **Form Interaction Test**
   - Fills out a pizza order form
   - Tests various input types (text, select, checkboxes)
   - Validates form data entry

### Selenium Test Features
- Headless Chrome browser for CI/CD compatibility
- Automatic ChromeDriver installation
- Robust element waiting and validation
- Clean test isolation and cleanup

## 🐛 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Clean up containers and images
docker-compose -f docker-compose.*.yml down
docker system prune -f

# Rebuild containers
docker-compose -f docker-compose.*.yml up --build --force-recreate
```

#### Selenium Issues
- Ensure Chrome and ChromeDriver versions are compatible
- Check container has sufficient memory for browser
- Verify network connectivity for external test sites

#### PostgreSQL Issues
- Check container health status
- Verify port mappings
- Ensure database credentials are correct

### Debug Mode
```bash
# Run with verbose output
docker-compose -f docker-compose.selenium.yml up --build
docker-compose -f docker-compose.selenium.yml logs -f selenium-tests
```

## 🔄 CI/CD Integration

The test suite is designed for CI/CD environments:

- **JUnit XML output** for test reporting
- **Docker-based execution** for consistent environments
- **Exit codes** for build success/failure
- **Cleanup automation** to prevent resource leaks

### GitHub Actions Example
```yaml
- name: Run Selenium Tests
  run: |
    python run_selenium_tests.py
```

## 📝 Adding New Tests

### New Unit Tests
1. Create test file in `tests/unit/`
2. Follow pytest naming conventions
3. Ensure tests are isolated and fast

### New Integration Tests
1. Create test file in `tests/integration/`
2. Use appropriate fixtures for database access
3. Include proper cleanup in test teardown

### New Selenium Tests
1. Add test methods to `TestSeleniumBrowser` class
2. Use the `driver` fixture for browser access
3. Test against reliable external sites or mock services
4. Include proper assertions and error handling

## 🤝 Contributing

1. Follow existing test patterns and naming conventions
2. Ensure all tests pass in Docker containers
3. Update documentation for new test types
4. Include appropriate error handling and cleanup

## 📄 License

This project is provided as-is for demonstration and testing purposes.
