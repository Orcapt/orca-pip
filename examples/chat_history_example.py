"""
Example: Using Chat History with LangChain
===========================================

Demonstrates how to use ChatHistoryHelper with LangChain/LangGraph.
"""

from orca import ChatMessage, ChatHistoryHelper, Variables
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def process_message(data: ChatMessage):
    """Process a message with conversation history."""
    
    # Get variables
    variables = Variables(data.variables)
    openai_key = variables.get("OPENAI_API_KEY")
    
    # Initialize chat history helper
    history = ChatHistoryHelper(data.chat_history)
    
    print(f"Conversation has {history.count()} previous messages")
    
    # Convert to LangChain messages
    system_msg = data.system_message or "You are a helpful assistant."
    messages = history.to_langchain_messages(include_system=system_msg)
    
    # Add current user message
    messages.append(HumanMessage(content=data.message))
    
    # Use with LangChain
    model = ChatOpenAI(api_key=openai_key, model=data.model)
    response = model.invoke(messages)
    
    return response.content


# Example with LangGraph state
def create_graph_with_history(data: ChatMessage):
    """Example using chat history in LangGraph state."""
    from langgraph.graph import StateGraph, MessagesState
    
    # Get history as LangChain messages
    history = ChatHistoryHelper(data.chat_history)
    
    # Initialize state with history
    initial_state = {
        "messages": history.to_langchain_messages(
            include_system=data.system_message
        )
    }
    
    # Add current message
    initial_state["messages"].append(HumanMessage(content=data.message))
    
    # Build your graph...
    # graph = StateGraph(MessagesState)
    # ... define your nodes and edges ...
    
    return initial_state


# Example: Get only recent context
def process_with_recent_history(data: ChatMessage):
    """Use only the last 10 messages for context."""
    
    history = ChatHistoryHelper(data.chat_history)
    
    # Get last 10 messages as LangChain objects
    recent_messages = history.get_last_n_langchain_messages(
        10, 
        include_system=data.system_message
    )
    
    # Add current message
    recent_messages.append(HumanMessage(content=data.message))
    
    # Use with your model...
    variables = Variables(data.variables)
    openai_key = variables.get("OPENAI_API_KEY")
    
    model = ChatOpenAI(api_key=openai_key, model=data.model)
    response = model.invoke(recent_messages)
    
    return response.content


# Example: Format as context string
def get_context_summary(data: ChatMessage):
    """Get conversation history as a formatted string."""
    
    history = ChatHistoryHelper(data.chat_history)
    
    # Get as formatted string (last 5 messages)
    context = history.get_context_string(max_messages=5)
    
    print("Recent conversation:")
    print(context)
    
    return context


# Example: Check conversation state
def analyze_conversation(data: ChatMessage):
    """Analyze the conversation history."""
    
    history = ChatHistoryHelper(data.chat_history)
    
    print(f"Total messages: {history.count()}")
    print(f"User messages: {len(history.get_user_messages())}")
    print(f"Assistant messages: {len(history.get_assistant_messages())}")
    
    if not history.is_empty():
        print(f"Last user message: {history.get_last_user_message()}")
        print(f"Last assistant message: {history.get_last_assistant_message()}")
    else:
        print("No conversation history available")


# Example: Working with raw message data
def extract_conversation_topics(data: ChatMessage):
    """Extract topics from conversation history."""
    
    history = ChatHistoryHelper(data.chat_history)
    
    # Get all messages as raw dictionaries
    messages = history.get_messages()
    
    # Process messages
    topics = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        # Simple topic extraction (you could use NLP here)
        if role == "user" and len(content) > 10:
            topics.append(content[:50] + "..." if len(content) > 50 else content)
    
    print(f"Conversation topics: {topics}")
    return topics


# Example: Advanced LangGraph integration with checkpointing
def create_stateful_graph(data: ChatMessage):
    """Create a LangGraph workflow that uses chat history with checkpointing."""
    from langgraph.graph import StateGraph, MessagesState, END
    from langgraph.checkpoint.memory import MemorySaver
    
    # Initialize chat history
    history = ChatHistoryHelper(data.chat_history)
    
    # Create graph
    workflow = StateGraph(MessagesState)
    
    def agent_node(state):
        """Agent node that processes messages."""
        messages = state["messages"]
        
        # Get variables
        variables = Variables(data.variables)
        openai_key = variables.get("OPENAI_API_KEY")
        
        # Create model
        model = ChatOpenAI(api_key=openai_key, model=data.model)
        
        # Process
        response = model.invoke(messages)
        
        return {"messages": [response]}
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    
    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    # Initialize with conversation history
    initial_messages = history.to_langchain_messages(
        include_system=data.system_message
    )
    initial_messages.append(HumanMessage(content=data.message))
    
    # Run
    config = {"configurable": {"thread_id": data.thread_id}}
    result = app.invoke({"messages": initial_messages}, config=config)
    
    return result


# Example: Conditional logic based on history
def smart_response_with_history(data: ChatMessage):
    """Adjust response based on conversation history."""
    
    history = ChatHistoryHelper(data.chat_history)
    variables = Variables(data.variables)
    openai_key = variables.get("OPENAI_API_KEY")
    
    # Decide strategy based on conversation length
    if history.is_empty():
        # First message - use simple greeting
        system_msg = "You are a helpful assistant. Greet the user warmly."
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=data.message)
        ]
    elif history.count() < 5:
        # Early conversation - build rapport
        system_msg = data.system_message or "You are a friendly assistant."
        messages = history.to_langchain_messages(include_system=system_msg)
        messages.append(HumanMessage(content=data.message))
    else:
        # Ongoing conversation - focus on last 10 messages for efficiency
        system_msg = data.system_message or "You are a helpful assistant."
        messages = history.get_last_n_langchain_messages(10, include_system=system_msg)
        messages.append(HumanMessage(content=data.message))
    
    # Process with model
    model = ChatOpenAI(api_key=openai_key, model=data.model)
    response = model.invoke(messages)
    
    return response.content


if __name__ == "__main__":
    # Example usage (simulated)
    print("Chat History Helper Examples")
    print("=" * 50)
    
    # Simulate a ChatMessage with history
    from orca import Variable
    
    sample_data = ChatMessage(
        thread_id="test-thread-123",
        model="gpt-4",
        message="What was my previous question about?",
        conversation_id=1,
        response_uuid="test-uuid",
        message_uuid="msg-uuid",
        channel="test-channel",
        variables=[
            Variable(name="OPENAI_API_KEY", value="sk-test-key", id="1", type="text")
        ],
        url="http://example.com",
        chat_history=[
            {"role": "user", "content": "Hello, I'm interested in learning Python"},
            {"role": "assistant", "content": "Great! I'd be happy to help you learn Python. What's your current level?"},
            {"role": "user", "content": "I'm a complete beginner"},
            {"role": "assistant", "content": "Perfect! Let's start with the basics. Python is a versatile programming language..."},
        ]
    )
    
    # Test the examples
    history = ChatHistoryHelper(sample_data.chat_history)
    
    print(f"\nMessage count: {history.count()}")
    print(f"Is empty: {history.is_empty()}")
    print(f"\nLast user message: {history.get_last_user_message()}")
    print(f"\nContext string (last 2):")
    print(history.get_context_string(max_messages=2))
    
    print("\n" + "=" * 50)
    print("See the function implementations above for more examples!")
