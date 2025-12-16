"""
Simple Lambda Deployment Example
=================================

This is the SIMPLEST production-ready Lambda handler.
Copy this file to your project as `lambda_handler.py` and customize!

Usage:
1. Copy this file to your project root as `lambda_handler.py`
2. Add your agent logic in the process_message function
3. Build Docker image: `docker build -f Dockerfile.lambda -t my-agent:latest .`
4. Deploy: `orca ship my-agent --image my-agent:latest --env-file .env`

That's it! 🚀
"""

from orca import OrcaHandler, LambdaAdapter

# Initialize handler
handler = OrcaHandler(dev_mode=False)

# Initialize Lambda adapter
adapter = LambdaAdapter()


@adapter.message_handler
async def process_message(data):
    """
    Your agent logic goes here!
    Replace this with your actual implementation.
    """
    session = handler.begin(data)
    
    try:
        # Start loading indicator
        session.loading.start("thinking")
        
        # ==========================================
        # YOUR AGENT LOGIC HERE
        # ==========================================
        
        # Example: Simple echo
        response = f"You said: {data.message}"
        
        # Example with OpenAI (uncomment to use):
        # from openai import AsyncOpenAI
        # client = AsyncOpenAI()
        # completion = await client.chat.completions.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": data.message}]
        # )
        # response = completion.choices[0].message.content
        
        # Example with streaming (uncomment to use):
        # session.loading.end("thinking")
        # async for chunk in stream:
        #     if chunk.choices[0].delta.content:
        #         session.stream(chunk.choices[0].delta.content)
        
        # ==========================================
        # END YOUR LOGIC
        # ==========================================
        
        # Stop loading
        session.loading.end("thinking")
        
        # Stream the response
        session.stream(response)
        
        # Optional: Add buttons
        # session.button.link("Learn More", "https://example.com")
        # session.button.action("Regenerate", "regenerate")
        
        # Close session
        session.close()
        
    except Exception as e:
        # Error handling is automatic!
        session.error(f"An error occurred: {str(e)}", exception=e)
        raise


# Optional: Add scheduled tasks (cron)
@adapter.cron_handler
async def scheduled_task(event):
    """
    Optional: Handle scheduled/cron events.
    Remove this if you don't need scheduled tasks.
    """
    print("[CRON] Running scheduled task...")
    
    # Your maintenance logic here
    # Example: Database cleanup, cache refresh, etc.
    
    print("[CRON] Task completed!")


# Lambda entry point (DO NOT MODIFY)
def handler(event, context):
    """
    Main Lambda handler - delegates everything to LambdaAdapter.
    
    LambdaAdapter automatically handles:
    - HTTP requests (Function URL)
    - SQS events (async processing)
    - EventBridge (cron jobs)
    - Event loop management
    - Error handling
    - Automatic SQS queuing (if SQS_QUEUE_URL exists)
    """
    return adapter.handle(event, context)


# Optional: Print configuration on cold start
if __name__ == "__main__":
    import os
    print("[INIT] Lambda function ready!")
    print(f"[INIT] SQS queue: {os.environ.get('SQS_QUEUE_URL', 'Not configured (direct mode)')}")

