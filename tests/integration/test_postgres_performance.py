import pytest
import psycopg2
from time import time
from psycopg2.extras import execute_values


class TestPostgreSQLPerformance:
    """Test PostgreSQL performance and advanced features"""
    
    @pytest.fixture(scope="class")
    def db_connection(self, postgres_connection):
        """Create a database connection for the test class"""
        yield postgres_connection
    
    def test_bulk_insert_performance(self, db_connection):
        """Test bulk insert performance with execute_values"""
        with db_connection.cursor() as cursor:
            # Create a test table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bulk_insert_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    value INTEGER,
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Generate test data
            test_data = []
            for i in range(1000):
                test_data.append((
                    f"Item_{i}",
                    i,
                    f"Category_{i % 10}"
                ))
            
            # Measure bulk insert time
            start_time = time()
            
            execute_values(
                cursor,
                """
                INSERT INTO bulk_insert_test (name, value, category) 
                VALUES %s;
                """,
                test_data
            )
            
            db_connection.commit()
            bulk_insert_time = time() - start_time
            
            # Verify all data was inserted
            cursor.execute("SELECT COUNT(*) FROM bulk_insert_test;")
            count = cursor.fetchone()[0]
            assert count == 1000
            
            # Test individual insert for comparison
            cursor.execute("DELETE FROM bulk_insert_test;")
            db_connection.commit()
            
            start_time = time()
            for name, value, category in test_data[:100]:  # Test with 100 records
                cursor.execute("""
                    INSERT INTO bulk_insert_test (name, value, category) 
                    VALUES (%s, %s, %s);
                """, (name, value, category))
            
            db_connection.commit()
            individual_insert_time = time() - start_time
            
            # Bulk insert should be significantly faster
            # (1000 records vs 100 records, but bulk should still be faster per record)
            assert bulk_insert_time < individual_insert_time * 5  # Allow some variance
            
            # Clean up
            cursor.execute("DROP TABLE bulk_insert_test;")
            db_connection.commit()
    
    def test_index_performance(self, db_connection):
        """Test the performance impact of database indexes"""
        with db_connection.cursor() as cursor:
            # Create a test table without indexes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS index_performance_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    age INTEGER,
                    city VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            test_data = []
            for i in range(5000):
                test_data.append((
                    f"User_{i}",
                    f"user{i}@example.com",
                    20 + (i % 60),
                    f"City_{i % 20}"
                ))
            
            execute_values(
                cursor,
                """
                INSERT INTO index_performance_test (name, email, age, city) 
                VALUES %s;
                """,
                test_data
            )
            db_connection.commit()
            
            # Test query performance without index
            start_time = time()
            cursor.execute("""
                SELECT * FROM index_performance_test 
                WHERE age > 30 AND city = 'City_5';
            """)
            results_without_index = cursor.fetchall()
            time_without_index = time() - start_time
            
            # Create indexes
            cursor.execute("CREATE INDEX idx_age ON index_performance_test(age);")
            cursor.execute("CREATE INDEX idx_city ON index_performance_test(city);")
            cursor.execute("CREATE INDEX idx_age_city ON index_performance_test(age, city);")
            
            # Test query performance with indexes
            start_time = time()
            cursor.execute("""
                SELECT * FROM index_performance_test 
                WHERE age > 30 AND city = 'City_5';
            """)
            results_with_index = cursor.fetchall()
            time_with_index = time() - start_time
            
            # Verify results are the same
            assert len(results_without_index) == len(results_with_index)
            
            # Indexed query should be faster (though in small datasets difference might be minimal)
            # We'll just verify the query works and results are consistent
            
            # Test index usage in query plan
            cursor.execute("""
                EXPLAIN (FORMAT JSON) 
                SELECT * FROM index_performance_test 
                WHERE age > 30 AND city = 'City_5';
            """)
            query_plan = cursor.fetchone()[0]
            
            # Verify that indexes are being used
            plan_text = str(query_plan)
            assert "Index Scan" in plan_text or "Bitmap Index Scan" in plan_text
            
            # Clean up
            cursor.execute("DROP TABLE index_performance_test;")
            db_connection.commit()
    
    def test_connection_pooling_and_concurrency(self, db_connection):
        """Test handling multiple concurrent connections"""
        import threading
        import queue
        
        # Create a test table
        with db_connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concurrency_test (
                    id SERIAL PRIMARY KEY,
                    thread_id INTEGER,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            db_connection.commit()
        
        # Function to be executed by each thread
        def worker_thread(thread_id, result_queue):
            try:
                # Create a new connection for this thread
                conn = psycopg2.connect(
                    host="postgres",
                    database="test",
                    user="test",
                    password="test",
                    port=5432
                )
                
                with conn.cursor() as cursor:
                    # Insert data
                    cursor.execute("""
                        INSERT INTO concurrency_test (thread_id, message) 
                        VALUES (%s, %s);
                    """, (thread_id, f"Message from thread {thread_id}"))
                    
                    # Query data
                    cursor.execute("""
                        SELECT COUNT(*) FROM concurrency_test 
                        WHERE thread_id = %s;
                    """, (thread_id,))
                    
                    count = cursor.fetchone()[0]
                    result_queue.put((thread_id, True, count))
                    
                conn.commit()
                conn.close()
                
            except Exception as e:
                result_queue.put((thread_id, False, str(e)))
        
        # Start multiple threads
        num_threads = 5
        threads = []
        result_queue = queue.Queue()
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=worker_thread, 
                args=(i, result_queue)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # Verify all threads succeeded
        assert len(results) == num_threads
        
        for thread_id, success, data in results:
            assert success, f"Thread {thread_id} failed: {data}"
            assert data >= 1, f"Thread {thread_id} didn't insert data properly"
        
        # Verify total count
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM concurrency_test;")
            total_count = cursor.fetchone()[0]
            assert total_count == num_threads
        
        # Clean up
        with db_connection.cursor() as cursor:
            cursor.execute("DROP TABLE concurrency_test;")
            db_connection.commit()
    
    def test_database_statistics_and_monitoring(self, db_connection):
        """Test database statistics and monitoring capabilities"""
        with db_connection.cursor() as cursor:
            # Create and populate a test table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    value NUMERIC(10,2)
                );
            """)
            
            # Insert some data
            for i in range(100):
                cursor.execute("""
                    INSERT INTO stats_test (name, value) 
                    VALUES (%s, %s);
                """, (f"Item_{i}", 10.0 + i))
            
            db_connection.commit()
            
            # Test table statistics
            cursor.execute("""
                SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                FROM pg_stat_user_tables 
                WHERE tablename = 'stats_test';
            """)
            
            stats = cursor.fetchone()
            assert stats is not None
            assert stats[1] == "stats_test"  # tablename
            assert stats[2] >= 100  # n_tup_ins (inserts)
            
            # Test index statistics
            cursor.execute("""
                SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE tablename = 'stats_test';
            """)
            
            index_stats = cursor.fetchall()
            # Should have at least the primary key index
            assert len(index_stats) >= 1
            
            # Test database size information
            cursor.execute("""
                SELECT pg_size_pretty(pg_total_relation_size('stats_test'));
            """)
            
            table_size = cursor.fetchone()[0]
            assert table_size is not None
            assert "bytes" in table_size or "KB" in table_size or "MB" in table_size
            
            # Clean up
            cursor.execute("DROP TABLE stats_test;")
            db_connection.commit()
