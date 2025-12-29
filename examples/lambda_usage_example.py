"""
Comprehensive Lambda Guide
==========================

This example serves as a complete guide for building and deploying Orca Agents 
on AWS Lambda using the high-level factory patterns.
"""

import logging
import asyncio
from orca import create_hybrid_handler, ChatMessage, OrcaHandler

# 1. Initialize Orca Core (Global instance for efficiency)
orca = OrcaHandler()

# 2. Define Advanced Agent Logic
async def process_message(data: ChatMessage):
    """
    A more comprehensive agent logic example with multi-step streaming.
    """
    session = orca.begin(data)
    
    try:
        # Step 1: Analyzing
        session.loading.start("analyzing")
        await asyncio.sleep(0.5)
        session.stream("I'm analyzing your request...\n\n")
        session.loading.end("analyzing")
        
        # Step 2: Generating
        session.loading.start("thinking")
        await asyncio.sleep(1)
        response = f"Analysis complete for: '{data.message}'.\n"
        response += "The Orca SDK makes Lambda deployment seamless."
        
        session.loading.end("thinking")
        session.stream(response)
        
        # Step 3: Interaction
        session.button.link("API Reference", "https://docs.orcapt.com/api")
        
        session.close()
        
    except Exception as e:
        session.error("An error occurred during processing", exception=e)

# 3. Dedicated Cron/Scheduled Handler (Optional)
# The factory runs this automatically for 'Scheduled Event' sources
# if it's decorated or part of the internal adapter state.
# For simplicity, create_hybrid_handler uses a default success logger for cron.

# 4. Create the Universal Handler
# This factory simplifies setup by wrapping FastAPI, Mangum, and SQS routing.
handler = create_hybrid_handler(
    process_message_func=process_message,
    app_title="Comprehensive Orca Agent",
    level=logging.INFO,
    dev_mode=True  # Enables verbose logging and direct streaming in dev
)

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================
#
# 1. Dockerfile:
#    CMD ["lambda_usage_example.handler"]
#
# 2. Environment Variables:
#    - SQS_QUEUE_URL: Set this to enable async offloading
#    - APP_VERSION: Overrides the default health check version
#
# 3. orca ship:
#    $ orca ship my-agent --image my-agent-tag
#
# ============================================================================

if __name__ == "__main__":
    print(__doc__)
    print("Use 'simulate_factory.py' to test this handler locally.")
