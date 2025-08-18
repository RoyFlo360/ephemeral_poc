import pytest
from psycopg2.extras import RealDictCursor


class TestPostgreSQLConnection:
    """Test PostgreSQL connection and basic operations"""
    
    @pytest.fixture(scope="class")
    def db_connection(self, postgres_connection):
        """Create a database connection for the test class"""
        yield postgres_connection
    
    def test_database_connection(self, db_connection):
        """Test that we can connect to the PostgreSQL database"""
        assert db_connection is not None
        assert not db_connection.closed
        
        # Test basic connection properties
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            assert "PostgreSQL" in version
            assert "14" in version
    
    def test_database_creation_and_deletion(self, db_connection):
        """Test creating and dropping a test table"""
        with db_connection.cursor() as cursor:
            # Create a test table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            db_connection.commit()
            
            # Verify table exists
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'test_table';
            """)
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'test_table'
            
            # Drop the test table
            cursor.execute("DROP TABLE test_table;")
            db_connection.commit()
            
            # Verify table is dropped
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'test_table';
            """)
            result = cursor.fetchone()
            assert result is None
    
    def test_data_insertion_and_retrieval(self, db_connection):
        """Test inserting and retrieving data from a table"""
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Create a test table
            cursor.execute("""
                CREATE TABLE test_data (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    value INTEGER,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
            
            # Insert test data
            test_data = [
                ("Alice", 25, True),
                ("Bob", 30, False),
                ("Charlie", 35, True)
            ]
            
            for name, value, is_active in test_data:
                cursor.execute("""
                    INSERT INTO test_data (name, value, is_active) 
                    VALUES (%s, %s, %s);
                """, (name, value, is_active))
            
            db_connection.commit()
            
            # Retrieve and verify data
            cursor.execute("SELECT * FROM test_data ORDER BY id;")
            results = cursor.fetchall()
            
            assert len(results) == 3
            
            # Check first record
            assert results[0]['name'] == "Alice"
            assert results[0]['value'] == 25
            assert results[0]['is_active'] is True
            
            # Check second record
            assert results[1]['name'] == "Bob"
            assert results[1]['value'] == 30
            assert results[1]['is_active'] is False
            
            # Check third record
            assert results[2]['name'] == "Charlie"
            assert results[2]['value'] == 35
            assert results[2]['is_active'] is True
            
            # Test filtering
            cursor.execute("SELECT * FROM test_data WHERE is_active = TRUE;")
            active_users = cursor.fetchall()
            assert len(active_users) == 2
            
            # Clean up
            cursor.execute("DROP TABLE test_data;")
            db_connection.commit()
