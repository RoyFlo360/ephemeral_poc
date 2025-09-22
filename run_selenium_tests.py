#!/usr/bin/env python3
"""
Simple script to run Selenium tests using Docker Compose.
"""

import subprocess
import sys
import time

def run_selenium_tests():
    """Run Selenium tests using Docker Compose."""
    print("🚀 Starting Selenium tests...")
    
    try:
        # Build and start the Selenium test container
        print("📦 Building and starting Selenium test container...")
        subprocess.run([
            "docker-compose", "-f", "docker-compose.selenium.yml", 
            "up", "--build", "-d"
        ], check=True)
        
        # Wait for container to be ready
        print("⏳ Waiting for container to be ready...")
        time.sleep(15)
        
        # Run the tests
        print("🧪 Running Selenium tests...")
        result = subprocess.run([
            "docker-compose", "-f", "docker-compose.selenium.yml", 
            "logs", "selenium-tests"
        ], capture_output=True, text=True, check=True)
        
        # Print test results
        print("\n" + "="*60)
        print("SELENIUM TEST RESULTS:")
        print("="*60)
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print("="*60)
        
        # Check if tests passed
        if "Selenium tests completed" in result.stdout and "FAILED" not in result.stdout:
            print("✅ Selenium tests completed successfully!")
            return True
        else:
            print("❌ Selenium tests failed!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Selenium tests: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Clean up
        print("🧹 Cleaning up containers...")
        try:
            subprocess.run([
                "docker-compose", "-f", "docker-compose.selenium.yml", "down"
            ], check=True)
            print("✅ Cleanup completed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Cleanup failed: {e}")

if __name__ == "__main__":
    success = run_selenium_tests()
    sys.exit(0 if success else 1)
