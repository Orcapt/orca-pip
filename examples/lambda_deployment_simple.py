"""
Simple Lambda Handler - Single File Quick Start
===============================================

This example demonstrates the absolute minimum code needed for a production-ready 
Lambda handler that supports HTTP, SQS, and Cron events.
"""

import logging
from orca import create_hybrid_handler, ChatMessage

# 1. Define your agent logic directly in this file for simplicity
async def process_message(data: ChatMessage):
    """
    Core agent logic.
    In a real app, you would import this from another file.
    """
    # Note: create_hybrid_handler manages the OrcaHandler internally
    # You can also initialize your own OrcaHandler if needed.
    from orca import OrcaHandler
    orca = OrcaHandler()
    session = orca.begin(data)
    
    try:
        session.loading.start("thinking")
        response = f"Simple Lambda Agent received: '{data.message}'"
        session.loading.end("thinking")
        session.stream(response)
        session.close()
    except Exception as e:
        session.error(f"Error: {str(e)}", exception=e)

# 2. Create and export the universal handler
# This single export handles all routing, FastAPI, Mangum, and SQS logic.
handler = create_hybrid_handler(
    process_message_func=process_message,
    app_title="Simple Orca Agent",
    level=logging.INFO
)

# Usage: Set the Lambda entry point to 'lambda_deployment_simple.handler'
