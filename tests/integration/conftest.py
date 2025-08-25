import pytest
import psycopg2
from time import sleep
from os import getenv


@pytest.fixture(scope="session")
def postgres_connection():
    """Create a PostgreSQL connection for the entire test session"""
    # Get connection details from environment variables
    host = getenv("POSTGRES_HOST", "postgres")  # Default to postgres service name
    port = int(getenv("POSTGRES_PORT", "5432"))
    database = getenv("POSTGRES_DB", "test")
    user = getenv("POSTGRES_USER", "test")
    password = getenv("POSTGRES_PASSWORD", "test")
    
    # Wait for PostgreSQL to be ready
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
            conn.close()
            break
        except psycopg2.OperationalError:
            retry_count += 1
            sleep(2)
    
    if retry_count >= max_retries:
        pytest.fail("PostgreSQL connection failed after maximum retries")
    
    # Return a fresh connection
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    
    # Set autocommit to False for transaction testing
    conn.autocommit = False
    
    yield conn
    
    # Cleanup
    conn.close()


@pytest.fixture(autouse=True)
def setup_teardown(postgres_connection):
    """Setup and teardown for each test"""
    # Setup: ensure we start with a clean state
    with postgres_connection.cursor() as cursor:
        # List all user tables and drop them
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%' 
            AND tablename NOT LIKE 'sql_%';
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE;")
        
        postgres_connection.commit()
    
    yield
    
    # Teardown: clean up after each test
    with postgres_connection.cursor() as cursor:
        # List all user tables and drop them
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%' 
            AND tablename NOT LIKE 'sql_%';
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE;")
        
        postgres_connection.commit()
