"""
Basic Usage Example
===================

Demonstrates basic Orca SDK usage patterns.
"""

from orca import OrcaHandler, setup_logging
from orca.config import LoadingKind, ButtonColor
import logging

# Setup logging
setup_logging(level=logging.INFO)

def basic_example():
    """Basic streaming example."""
    # Initialize handler
    handler = OrcaHandler(dev_mode=True)
    
    # Create mock data
    class MockData:
        response_uuid = "test-uuid"
        thread_id = "test-thread"
        channel = "test-channel"
    
    data = MockData()
    
    # Begin session
    session = handler.begin(data)
    
    # Start loading indicator
    session.loading.start(LoadingKind.THINKING.value)
    
    # Stream response
    session.stream("Hello, ")
    session.stream("world!")
    
    # End loading
    session.loading.end(LoadingKind.THINKING.value)
    
    # Add buttons
    session.button.link("Learn More", "https://example.com", color=ButtonColor.PRIMARY.value)
    session.button.action("Click Me", "action_id", color=ButtonColor.SUCCESS.value)
    
    # Close session
    response = session.close()
    print(f"Response: {response}")


if __name__ == "__main__":
    basic_example()

