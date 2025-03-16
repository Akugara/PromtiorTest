import streamlit as st
from Components.ragMaker import RAGMaker, DEFAULT_PDF_PATH
import os
from datetime import datetime
import time

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_instance" not in st.session_state:
    st.session_state.rag_instance = None

if "conversations" not in st.session_state:
    st.session_state.conversations = {}  # {conversation_id: {"messages": [], "timestamp": datetime, "rag": RAGMaker}}

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None

# Set page config
st.set_page_config(
    page_title="Promtior AI CHAT",
    page_icon="🤖",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
    /* Chat container styles */
    .stChatFloatingInputContainer {
        padding: 0;
        margin: 0;
        max-width: none;
    }
    .stTextInput {
        position: fixed;
        bottom: 20px;
        width: calc(100% - 40px);
        max-width: none;
        margin: 0;
    }
    .main {
        margin-bottom: 80px;
        padding: 0;
    }
    /* Main content area */
    .main .block-container {
        padding: 0;
        max-width: none;
    }
    /* Remove default padding */
    .css-1544g2n {
        padding: 0;
    }
    .css-1y4p8pa {
        padding: 0;
    }
    /* Conversation styles */
    .chat-history {
        margin-bottom: 20px;
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
    }
    .conversation-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
    }
    .conversation-item:hover {
        background-color: #e0e2e6;
    }
    .selected-conversation {
        background-color: #d0d2d6;
    }
    /* Suggested questions styles */
    .stButton {
        width: 100%;
        padding: 0;
        margin: 0;
    }
    .stButton > button {
        background-color: rgba(248, 249, 250, 0.1);
        border: 1px solid rgba(222, 226, 230, 0.2);
        padding: 12px 16px;
        text-align: left;
        font-size: 0.9em;
        min-height: 45px;
        height: auto;
        white-space: normal;
        margin: 4px 0;
        width: 100%;
        border-radius: 4px;
        color: inherit !important;
    }
    .stButton > button:hover {
        background-color: rgba(233, 236, 239, 0.2);
        border-color: rgba(173, 181, 189, 0.5);
        color: inherit !important;
    }
    /* Hide empty elements */
    .element-container:has(> div:empty) {
        display: none;
        margin: 0;
        padding: 0;
    }
    /* Chat message container */
    .stChatMessage {
        width: 100%;
        max-width: none;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

def create_new_conversation():
    """Create a new conversation and set it as current"""
    conversation_id = str(len(st.session_state.conversations))
    timestamp = datetime.now()
    rag = RAGMaker()
    if os.path.exists(DEFAULT_PDF_PATH):
        rag.process_document()
    
    st.session_state.conversations[conversation_id] = {
        "messages": [],
        "timestamp": timestamp,
        "rag": rag
    }
    st.session_state.current_conversation = conversation_id
    return conversation_id

def switch_conversation(conversation_id):
    """Switch to a different conversation"""
    st.session_state.current_conversation = conversation_id
    st.session_state.messages = st.session_state.conversations[conversation_id]["messages"]
    st.session_state.rag_instance = st.session_state.conversations[conversation_id]["rag"]

# Sidebar
with st.sidebar:
    st.title("Chat with Promtior")
    
    # New chat button
    if st.button("Create a New Chat"):
        create_new_conversation()
        st.rerun()
    
    # Display conversation history
    st.markdown("### Chat History")
    # Sort conversations by timestamp in reverse order (newest first)
    sorted_conversations = sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1]["timestamp"],
        reverse=True
    )
    
    for conv_id, conv_data in sorted_conversations:
        timestamp = conv_data["timestamp"].strftime("%Y-%m-%d %H:%M")
        messages = conv_data["messages"]
        preview = messages[0]["content"][:30] + "..." if messages else "Empty conversation"
        
        if st.button(
            f"{timestamp}\n{preview}",
            key=f"conv_{conv_id}",
            use_container_width=True,
            help="Click to switch to this conversation"
        ):
            switch_conversation(conv_id)
            st.rerun()

# Create initial conversation if none exists
if not st.session_state.conversations:
    create_new_conversation()

# Ensure current conversation is set
if st.session_state.current_conversation is None:
    st.session_state.current_conversation = next(iter(st.session_state.conversations.keys()))

# Get current conversation data
current_conv = st.session_state.conversations[st.session_state.current_conversation]
st.session_state.messages = current_conv["messages"]
st.session_state.rag_instance = current_conv["rag"]

# Add suggested questions
if not st.session_state.messages:  # Only show suggestions for empty conversations
    suggested_questions = [
        "How can Promtior help my business?",
        "Why do I need an AI-assisted solution?",
        "What are the main features of Promtior?",
        "Why should I hire Agustin Garagorry?",
    ]
    
    # Create a container for the questions
    for i, question in enumerate(suggested_questions):
        if st.button(question, key=f"suggest_{i}", use_container_width=True):
            # Generate response
            if st.session_state.rag_instance is not None:
                # Store the response in session state to persist through reruns
                if "temp_response" not in st.session_state:
                    response = st.session_state.rag_instance.query(question)
                    st.session_state.temp_response = response
                    st.session_state.temp_question = question
                    
                    # Update messages in session state
                    st.session_state.messages = [
                        {"role": "user", "content": question},
                        {
                            "role": "assistant", 
                            "content": response["answer"],
                            "sources": response["sources"] if response["sources"] else None
                        }
                    ]
                    current_conv["messages"] = st.session_state.messages
                    st.rerun()
                
                # After rerun, display the stored response
                if "temp_response" in st.session_state:
                    response = st.session_state.temp_response
                    question = st.session_state.temp_question
                    
                    # Display messages and sources
                    with st.chat_message("user"):
                        st.write(question)
                    
                    with st.chat_message("assistant"):
                        st.write(response["answer"])
                        
                        # Show sources if available
                        if response["sources"]:
                            with st.expander("View Sources", expanded=False):
                                st.markdown("*The following chunks from the document were used to generate this response:*")
                                for source in response["sources"]:
                                    st.markdown("---")
                                    if "page" in source:
                                        st.markdown(f"**Page {source['page']}**")
                                    if "page_content" in source:
                                        st.markdown(source["page_content"])
                    
                    # Clear temporary storage
                    del st.session_state.temp_response
                    del st.session_state.temp_question

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("View Sources", expanded=False):
                st.markdown("*The following chunks from the document were used to generate this response:*")
                for source in message["sources"]:
                    st.markdown("---")
                    if "page" in source:
                        st.markdown(f"**Page {source['page']+1}**")
                    if "page_content" in source:
                        st.markdown(source["page_content"])

# Chat input
if prompt := st.chat_input("Ask a question about us!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    current_conv["messages"] = st.session_state.messages
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    if st.session_state.rag_instance is not None:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.rag_instance.query(prompt)
                st.write(response["answer"])
                
                # Show sources if available
                if response["sources"]:
                    with st.expander("View Sources", expanded=False):
                        st.markdown("*The following chunks from the document were used to generate this response:*")
                        for source in response["sources"]:
                            st.markdown("---")
                            if "page" in source:
                                st.markdown(f"**Page {source['page']}**")
                            if "page_content" in source:
                                st.markdown(source["page_content"])
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response["answer"],
            "sources": response["sources"] if response["sources"] else None
        })
        current_conv["messages"] = st.session_state.messages
    else:
        with st.chat_message("assistant"):
            st.write("No document loaded. Using the default document or upload a custom PDF to start the conversation.")
