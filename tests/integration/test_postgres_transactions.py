import pytest
import psycopg2


class TestPostgreSQLTransactions:
    """Test PostgreSQL transaction handling and rollback functionality"""
    
    @pytest.fixture(scope="class")
    def db_connection(self, postgres_connection):
        """Create a database connection for the test class"""
        yield postgres_connection
    
    def test_transaction_commit(self, db_connection):
        """Test that committed transactions persist data"""
        with db_connection.cursor() as cursor:
            # Create a test table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_test (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    amount DECIMAL(10,2)
                );
            """)
            
            # Insert data and commit
            cursor.execute("""
                INSERT INTO transaction_test (message, amount) 
                VALUES (%s, %s);
            """, ("Test transaction", 100.50))
            
            db_connection.commit()
            
            # Verify data is persisted
            cursor.execute("SELECT * FROM transaction_test WHERE message = %s;", ("Test transaction",))
            result = cursor.fetchone()
            assert result is not None
            assert result[1] == "Test transaction"
            assert float(result[2]) == 100.50
            
            # Clean up
            cursor.execute("DROP TABLE transaction_test;")
            db_connection.commit()
    
    def test_transaction_rollback(self, db_connection):
        """Test that rolled back transactions don't persist data"""
        with db_connection.cursor() as cursor:
            # Create a test table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rollback_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100)
                );
            """)
            
            # Insert initial data and commit
            cursor.execute("""
                INSERT INTO rollback_test (name) VALUES (%s);
            """, ("Initial data",))
            db_connection.commit()
            
            # Start a new transaction
            cursor.execute("BEGIN;")
            
            # Insert data that will be rolled back
            cursor.execute("""
                INSERT INTO rollback_test (name) VALUES (%s);
            """, ("Rollback data",))
            
            # Rollback the transaction
            db_connection.rollback()
            
            # Verify only initial data exists
            cursor.execute("SELECT COUNT(*) FROM rollback_test;")
            count = cursor.fetchone()[0]
            assert count == 1
            
            cursor.execute("SELECT name FROM rollback_test;")
            result = cursor.fetchone()
            assert result[0] == "Initial data"
            
            # Clean up
            cursor.execute("DROP TABLE rollback_test;")
            db_connection.commit()
    
    def test_nested_transactions(self, db_connection):
        """Test nested transaction behavior with savepoints"""
        with db_connection.cursor() as cursor:
            # Create a test table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nested_transaction_test (
                    id SERIAL PRIMARY KEY,
                    level INTEGER,
                    description TEXT
                );
            """)
            
            # Start main transaction
            cursor.execute("BEGIN;")
            
            # Insert at main level
            cursor.execute("""
                INSERT INTO nested_transaction_test (level, description) 
                VALUES (%s, %s);
            """, (1, "Main transaction"))
            
            # Create savepoint
            cursor.execute("SAVEPOINT level2;")
            
            # Insert at savepoint level
            cursor.execute("""
                INSERT INTO nested_transaction_test (level, description) 
                VALUES (%s, %s);
            """, (2, "Savepoint level"))
            
            # Rollback to savepoint
            cursor.execute("ROLLBACK TO SAVEPOINT level2;")
            
            # Verify only main transaction data exists
            cursor.execute("SELECT COUNT(*) FROM nested_transaction_test;")
            count = cursor.fetchone()[0]
            assert count == 1
            
            cursor.execute("SELECT level, description FROM nested_transaction_test;")
            result = cursor.fetchone()
            assert result[0] == 1
            assert result[1] == "Main transaction"
            
            # Commit main transaction
            db_connection.commit()
            
            # Clean up
            cursor.execute("DROP TABLE nested_transaction_test;")
            db_connection.commit()
    
    def test_concurrent_transactions(self, db_connection):
        """Test handling of concurrent transactions"""
        with db_connection.cursor() as cursor:
            # Create a test table with a unique constraint
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concurrent_test (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(100) UNIQUE,
                    name VARCHAR(100)
                );
            """)
            
            # Insert initial data
            cursor.execute("""
                INSERT INTO concurrent_test (email, name) 
                VALUES (%s, %s);
            """, ("alice@example.com", "Alice"))
            db_connection.commit()
            
            # Start a transaction that will conflict
            cursor.execute("BEGIN;")
            
            try:
                # Try to insert duplicate email (should fail)
                cursor.execute("""
                    INSERT INTO concurrent_test (email, name) 
                    VALUES (%s, %s);
                """, ("alice@example.com", "Alice Duplicate"))
                
                # This should raise an exception
                pytest.fail("Expected duplicate key violation")
                
            except psycopg2.IntegrityError as e:
                # Verify it's a duplicate key violation
                assert "duplicate key value violates unique constraint" in str(e)
                
                # Rollback the failed transaction
                db_connection.rollback()
                
                # Verify original data is still intact
                cursor.execute("SELECT COUNT(*) FROM concurrent_test;")
                count = cursor.fetchone()[0]
                assert count == 1
                
                cursor.execute("SELECT email, name FROM concurrent_test;")
                result = cursor.fetchone()
                assert result[0] == "alice@example.com"
                assert result[1] == "Alice"
            
            # Clean up
            cursor.execute("DROP TABLE concurrent_test;")
            db_connection.commit()
