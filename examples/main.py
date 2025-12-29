"""
Main Agent Application
======================

This file demonstrates how to use the 'create_agent_app' factory to build
a production-ready FastAPI application for your Orca Agent with one line.
"""

import asyncio
from orca import ChatMessage
from orca.utils.app_utils import create_agent_app

async def process_message(data: ChatMessage):
    """
    Core agent logic.
    Uses the 'orca' handler defined below to manage the session.
    """
    # Start the session (multi-step interaction)
    session = orca.begin(data)
    
    try:
        # 1. Start thinking
        session.loading.start("thinking")
        await asyncio.sleep(1)  # Simulate AI thinking
        
        # 2. Generate response
        response = f"Orca SEO Agent processed: '{data.message}'"
        
        # 3. Stop thinking and stream
        session.loading.end("thinking")
        session.stream(response)
        
        # 4. Finalize
        session.close()
        
    except Exception as e:
        session.error(f"Agent Error: {str(e)}", exception=e)
        raise

# Create the app and handler using the factory
# Returns a tuple: (fastapi_app, orca_handler)
app, orca = create_agent_app(
    process_message_func=process_message,
    title="Orca SEO Agent",
    version="1.0.0",
    description="Professional SEO Expert Agent powered by Orca SDK."
)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Orca SEO Agent...")
    uvicorn.run(app, host="0.0.0.0", port=5001)
