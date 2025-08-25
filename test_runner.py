from docker import from_env
from sys import argv, exit
from subprocess import run, TimeoutExpired
from typing import Tuple

def run_unit_tests_in_ephemeral_container(
    image_name: str = "myephemeral-test",
    dockerfile_path: str = "dockerfile.unit_test",
    build_context: str = ".",
    container_timeout: int = 600
) -> Tuple[bool, str]:
    """
    Run unit tests in an ephemeral Docker container.
    
    Args:
        image_name: Name for the Docker image
        dockerfile_path: Path to Dockerfile
        build_context: Build context path
        container_timeout: Max time in seconds to wait for tests
    
    Returns:
        Tuple of (success: bool, logs: str)
    """
    client = from_env()
    
    try:
        # Build the Docker image
        print(f"Building Docker image from {dockerfile_path}...")
        image, build_logs = client.images.build(
            path=build_context,
            dockerfile=dockerfile_path,
            tag=image_name,
            rm=True
        )
        
        # Run container and execute tests
        print("Starting ephemeral test container for unit tests...")
        container = client.containers.run(
            image_name,
            detach=True,
            auto_remove=False,  # We'll remove manually after getting logs
            stdout=True,
            stderr=True,
            # Add any needed environment variables here
            # environment={
            #     "TEST_ENV": "true"
            # }
        )
        
        # Wait for container to finish (with timeout)
        try:
            result = container.wait(timeout=container_timeout)
            exit_code = result["StatusCode"]
            
            # Get container logs
            logs = container.logs().decode("utf-8")
            
            return (exit_code == 0, logs)
            
        finally:
            # Clean up container
            container.remove()
            
    except Exception as e:
        return (False, f"Error: {str(e)}")

def run_integration_tests_with_docker_compose(
    compose_file: str = "docker-compose.integration.yml",
    timeout: int = 600
) -> Tuple[bool, str]:
    """
    Run integration tests using Docker Compose.
    
    Args:
        compose_file: Path to Docker Compose file
        timeout: Max time in seconds to wait for tests
    
    Returns:
        Tuple of (success: bool, logs: str)
    """
    try:
        print(f"Starting integration tests with {compose_file}...")
        
        # Start the services
        print("Starting Docker Compose services...")
        start_result = run(
            ["docker-compose", "-f", compose_file, "up", "--build", "-d"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if start_result.returncode != 0:
            return (False, f"Failed to start services: {start_result.stderr}")
        
        # Wait a bit for services to be ready
        print("Waiting for services to be ready...")

        
        # Run the tests
        print("Running integration tests...")
        test_result = run(
            ["docker-compose", "-f", compose_file, "logs", "-f", "app"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Get the test results
        logs_result = run(
            ["docker-compose", "-f", compose_file, "logs", "app"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        logs = logs_result.stdout + logs_result.stderr
        
        # Check if tests passed by looking for test results
        success = "Integration tests completed" in logs and "FAILED" not in logs
        
        return (success, logs)
        
    except TimeoutExpired:
        return (False, "Integration tests timed out")
    except Exception as e:
        return (False, f"Error running integration tests: {str(e)}")
    finally:
        # Clean up
        print("Cleaning up Docker Compose services...")
        run(
            ["docker-compose", "-f", compose_file, "down"],
            capture_output=True,
            timeout=60
        )

def run_all_tests_sequentially(
    unit_timeout: int = 600,
    integration_timeout: int = 600
) -> Tuple[bool, str]:
    """
    Run both unit tests and integration tests sequentially.
    
    Args:
        unit_timeout: Max time in seconds to wait for unit tests
        integration_timeout: Max time in seconds to wait for integration tests
    
    Returns:
        Tuple of (overall_success: bool, combined_logs: str)
    """
    all_logs = []
    overall_success = True
    
    print("=== Running All Tests Sequentially ===")
    
    # Step 1: Run Unit Tests
    print("\n🔧 Step 1: Running Unit Tests...")
    unit_success, unit_logs = run_unit_tests_in_ephemeral_container(
        container_timeout=unit_timeout
    )
    
    all_logs.append("="*50)
    all_logs.append("UNIT TESTS OUTPUT:")
    all_logs.append("="*50)
    all_logs.append(unit_logs)
    
    if unit_success:
        print("✅ Unit tests passed!")
    else:
        print("❌ Unit tests failed!")
        overall_success = False
    
    # Step 2: Run Integration Tests
    print("\n🔧 Step 2: Running Integration Tests...")
    integration_success, integration_logs = run_integration_tests_with_docker_compose(
        timeout=integration_timeout
    )
    
    all_logs.append("\n" + "="*50)
    all_logs.append("INTEGRATION TESTS OUTPUT:")
    all_logs.append("="*50)
    all_logs.append(integration_logs)
    
    if integration_success:
        print("✅ Integration tests passed!")
    else:
        print("❌ Integration tests failed!")
        overall_success = False
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print("="*50)
    print(f"Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    print(f"Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    print("="*50)
    
    return overall_success, "\n".join(all_logs)

def run_tests_in_ephemeral_container(
    test_type: str = "unit",
    **kwargs
) -> Tuple[bool, str]:
    """
    Run tests based on the specified type.
    
    Args:
        test_type: Either "unit", "integration", or "all"
        **kwargs: Additional arguments passed to the specific test runner
    
    Returns:
        Tuple of (success: bool, logs: str)
    """
    if test_type.lower() == "integration":
        return run_integration_tests_with_docker_compose(**kwargs)
    elif test_type.lower() == "all":
        return run_all_tests_sequentially(**kwargs)
    else:
        return run_unit_tests_in_ephemeral_container(**kwargs)

if __name__ == "__main__":
    # Check command line arguments
    test_type = "all"  # default to running all tests
    if len(argv) > 1:
        test_type = argv[1]
    
    print(f"=== Test Runner ===")
    print(f"Test type: {test_type}")
    print(f"==================")
    
    if test_type.lower() == "integration":
        print("Running integration tests with Docker Compose...")
        success, logs = run_integration_tests_with_docker_compose()
    elif test_type.lower() == "unit":
        print("Running unit tests in ephemeral container...")
        success, logs = run_unit_tests_in_ephemeral_container()
    elif test_type.lower() == "all":
        print("Running all tests sequentially...")
        success, logs = run_all_tests_sequentially()
    else:
        print(f"Unknown test type: {test_type}. Defaulting to all tests...")
        success, logs = run_all_tests_sequentially()
    
    print("\n" + "="*50)
    print("FINAL TEST OUTPUT:")
    print("="*50)
    print(logs)
    print("="*50)
    
    if success:
        print(f"\n✅ All tests completed successfully!")
    else:
        print(f"\n❌ Some tests failed!")
    
    exit(0 if success else 1)
