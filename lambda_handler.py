from orca import ChatMessage, OrcaHandler
from orca.utils import create_hybrid_handler

async def process_message(data: ChatMessage):
    """
    Core agent logic. This is where you implement your agent's reasoning
    and response generation.
    """
    # 1. Initialize Orca session
    orca_handler = OrcaHandler()
    session = orca_handler.begin(data)
    
    try:
        # 2. Add visual indicator of thinking/processing
        session.loading.start("thinking")
        
        # 3. Dummy response logic (Replace with your actual AI logic)
        response = f"Orca Agent received: {data.message}"
        
        session.loading.end("thinking")
        
        # 4. Stream response back to user
        session.stream(response)
        
        # 5. Finalize session
        session.close()
        
    except Exception as e:
        # Handle errors gracefully via Orca SDK
        session.error(f"Execution Error: {str(e)}", exception=e)

# --- Entry Point ---
# create_hybrid_handler automatically routes HTTP (FastAPI) and SQS/Cron events.
handler = create_hybrid_handler(process_message, app_title="Orca Production Agent")
