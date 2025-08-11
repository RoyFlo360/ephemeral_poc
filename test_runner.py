# test_runner.py
import docker
import sys
from typing import Tuple

def run_tests_in_ephemeral_container(
    image_name: str = "myephemeral-test",
    dockerfile_path: str = "C:\\repos\\ephemeral_poc\\dockerfile.unit_test",
    build_context: str = ".",
    container_timeout: int = 600
) -> Tuple[bool, str]:
    """
    Run tests in an ephemeral Docker container.
    
    Args:
        image_name: Name for the Docker image
        dockerfile_path: Path to Dockerfile
        build_context: Build context path
        container_timeout: Max time in seconds to wait for tests
    
    Returns:
        Tuple of (success: bool, logs: str)
    """
    client = docker.from_env()
    
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
        print("Starting ephemeral test container...")
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

if __name__ == "__main__":
    success, logs = run_tests_in_ephemeral_container()
    
    print("\nTest Output:")
    print(logs)
    
    if success:
        print("\nTests passed successfully!")
    else:
        print("\nTests failed!")
    
    sys.exit(0 if success else 1)
