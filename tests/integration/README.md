# PostgreSQL Integration Tests

This directory contains integration tests that verify PostgreSQL 14 functionality using Docker containers.

## Test Cases

### 1. `test_postgres_connection.py`
Tests basic PostgreSQL connection functionality:
- Database connection establishment
- Table creation and deletion
- Data insertion and retrieval
- Basic SQL operations

### 2. `test_postgres_transactions.py`
Tests PostgreSQL transaction handling:
- Transaction commit and rollback
- Nested transactions with savepoints
- Concurrent transaction handling
- Constraint violations and error handling

### 3. `test_postgres_performance.py`
Tests PostgreSQL performance and advanced features:
- Bulk insert performance with `execute_values`
- Index performance impact
- Connection pooling and concurrency
- Database statistics and monitoring

## Running the Tests

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)
```bash
# Run all integration tests
docker-compose -f docker-compose.integration.yml up --build --abort-on-container-exit

# Run tests in background
docker-compose -f docker-compose.integration.yml up -d --build

# View logs
docker-compose -f docker-compose.integration.yml logs -f app

# Stop and clean up
docker-compose -f docker-compose.integration.yml down
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=test
export POSTGRES_USER=test
export POSTGRES_PASSWORD=test

# Start PostgreSQL container
docker run -d \
  --name postgres-test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_USER=test \
  -e POSTGRES_DB=test \
  -p 5432:5432 \
  postgres:14

# Wait for PostgreSQL to be ready
sleep 10

# Run tests
pytest tests/integration/ -v

# Clean up
docker stop postgres-test
docker rm postgres-test
```

## Test Configuration

The tests use the following PostgreSQL configuration:
- **Host**: `postgres` (Docker service name) or `localhost` (local)
- **Port**: `5432`
- **Database**: `test`
- **User**: `test`
- **Password**: `test`

## Test Results

Test results are generated in JUnit XML format and saved to:
- `test-results/integration/results.xml` (when running in Docker)
- Console output (when running locally)

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL container is running and healthy
- Check that ports are not conflicting
- Verify environment variables are set correctly

### Permission Issues
- Ensure the test user has appropriate database permissions
- Check that the test database exists and is accessible

### Performance Issues
- Some performance tests may vary based on system resources
- Consider adjusting test data sizes for your environment
- Monitor system resources during test execution

## Adding New Tests

When adding new integration tests:

1. Create a new test file in this directory
2. Use the `postgres_connection` fixture for database access
3. Follow the existing test patterns and naming conventions
4. Ensure proper cleanup in test teardown
5. Add appropriate error handling and assertions
6. Document any new dependencies or requirements
