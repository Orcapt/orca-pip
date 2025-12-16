"""
Error Handling Example
======================

Demonstrates comprehensive error handling with custom exceptions.
"""

from orca import (
    OrcaHandler,
    setup_logging,
    OrcaException,
    ValidationError,
    StreamError,
    handle_errors,
)
from orca.common import InvalidValueError, wrap_exception
import logging

# Setup logging
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


@handle_errors(default_return=None, exception_class=ValidationError)
def validate_input(value: str) -> str:
    """Validate input with automatic error handling."""
    if not value:
        raise InvalidValueError("value", value, "cannot be empty")
    return value.strip()


def error_handling_example():
    """Demonstrate error handling patterns."""
    handler = OrcaHandler(dev_mode=True)
    
    # Mock data
    class MockData:
        response_uuid = "error-test-uuid"
        thread_id = "error-test-thread"
        channel = "error-test-channel"
    
    data = MockData()
    
    try:
        # Begin session
        session = handler.begin(data)
        
        # Validate input
        user_input = validate_input("")  # This will return None due to @handle_errors
        if user_input is None:
            logger.warning("Input validation failed, using default")
            user_input = "default value"
        
        # Stream response
        session.stream(f"Processed: {user_input}")
        
        # Simulate error
        try:
            raise ValueError("Simulated error")
        except ValueError as e:
            # Wrap in Orca exception
            orca_error = wrap_exception(e, "Processing failed")
            logger.error(f"Error details: {orca_error.to_dict()}")
            
            # Send error to client
            session.error("An error occurred during processing")
        
        # Close normally
        response = session.close()
        print(f"Response: {response}")
        
    except OrcaException as e:
        # Catch all Orca exceptions
        logger.error(f"Orca error: {e}")
        logger.error(f"Error details: {e.to_dict()}")
    
    except Exception as e:
        # Catch unexpected errors
        logger.exception(f"Unexpected error: {e}")


if __name__ == "__main__":
    error_handling_example()

