"""
Advanced Usage Example
======================

Demonstrates advanced Lexia SDK features.
"""

from lexia import (
    LexiaHandler,
    setup_logging,
    retry,
    log_execution,
    measure_time,
    StreamError,
)
from lexia.common import LoggingContext
from lexia.config import LoadingKind, ButtonColor, TokenType
import logging

# Setup logging
setup_logging(level=logging.DEBUG, log_file="lexia_advanced.log")

@retry(max_attempts=3, delay=0.5)
@measure_time
def process_with_retry(session, text: str):
    """Process text with automatic retry."""
    session.stream(text)


@log_execution(include_args=True, include_result=True)
def generate_response(handler, data) -> str:
    """Generate AI response with logging."""
    session = handler.begin(data)
    
    # Progressive loading
    session.start_loading(LoadingKind.ANALYZING.value)
    session.stream("Analyzing your request...\n\n")
    session.end_loading(LoadingKind.ANALYZING.value)
    
    # Main content
    session.start_loading(LoadingKind.GENERATING.value)
    process_with_retry(session, "Generated response here!")
    session.end_loading(LoadingKind.GENERATING.value)
    
    # Track usage
    session.usage.track(150, TokenType.PROMPT.value, label="input")
    session.usage.track(200, TokenType.COMPLETION.value, label="output")
    
    # Add tracing
    session.tracing("Processing completed successfully", visibility="dev")
    
    # Add action buttons
    session.button.begin(default_color=ButtonColor.PRIMARY.value)
    session.button.add_link("Documentation", "https://docs.example.com")
    session.button.add_action("Regenerate", "regenerate_action")
    session.button.end()
    
    return session.close()


def advanced_example():
    """Advanced features demonstration."""
    # Initialize with custom configuration
    handler = LexiaHandler(dev_mode=True)
    
    # Create mock data
    class MockData:
        response_uuid = "adv-test-uuid"
        thread_id = "adv-test-thread"
        channel = "adv-test-channel"
    
    data = MockData()
    
    # Use logging context for debug
    with LoggingContext(logging.DEBUG):
        response = generate_response(handler, data)
        print(f"Advanced Response: {response}")


if __name__ == "__main__":
    advanced_example()

