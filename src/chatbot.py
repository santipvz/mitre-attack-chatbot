"""
Implementation of a MITRE ATT&CK expert chatbot with OpenAI, LangChain and Chroma.
"""

import os
import sys
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Import configuration
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config
except ImportError:
    # Fallback if config.py is not available
    load_dotenv()
    class Config:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        CHAT_MODEL = "gpt-4o-mini"
        EMBEDDING_MODEL = "text-embedding-3-small"
        VECTOR_STORE_PATH = "vector_store_mitre"
        COLLECTION_NAME = "mitre_attack_techniques"
        NUM_SIMILAR_DOCS = 6
        LOCAL_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
        EXIT_COMMANDS = [":exit", ":quit", ":terminate"]
        SYSTEM_PROMPT = (
            "You are an expert assistant in MITRE ATT&CK. "
            "Provide clear and precise information about attack techniques, "
            "tactics, and countermeasures based on the MITRE knowledge base."
        )
    config = Config()

def load_vector_store(vector_store_path: str, embedding_model) -> Chroma:
    """
    Load the previously generated index from local storage.

    Args:
        vector_store_path (str): Path to the vector store directory.
        embedding_model: Embedding model to use.

    Returns:
        Chroma: The loaded index from local storage.
    """
    try:
        local_vector_store = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=embedding_model,
            persist_directory=vector_store_path
        )
        print(f"✅ Index successfully loaded from: {vector_store_path}")
        return local_vector_store
    except Exception as error:
        print(f"❌ Error loading index: {error}")
        sys.exit(
            "Please make sure you have generated the index correctly "
            "with the indexing module by running: python indexer.py"
        )

def build_context(user_query: str, vector_store: Chroma, num_similar_docs: int) -> str:
    """
    Retrieve relevant documents and build an enriched context with related data.

    Args:
        user_query (str): The user's query.
        vector_store (Chroma): Vector store for similarity search.
        num_similar_docs (int): Number of documents to retrieve.

    Returns:
        str: The enriched context.
    """
    try:
        docs = vector_store.similarity_search(user_query, k=num_similar_docs)
        context = ""
        
        for doc in docs:
            mitigation_details = "\n".join([
                f"- {m.get('name', 'No name')}: {m.get('description', 'Description not available')}"
                for m in doc.metadata.get("mitigations", [])
            ])
            
            context += (
                f"Technique: {doc.metadata.get('name', 'Unknown')} "
                f"(ID: {doc.metadata.get('id', 'N/A')})\n"
                f"Tactics: {doc.metadata.get('tactics', 'Unknown')}\n"
                f"Description: {doc.page_content}\n"
                f"Detection: {doc.metadata.get('detection', 'Not available')}\n"
                f"Data sources: {doc.metadata.get('datasources', 'Not available')}\n"
                f"Required permissions: {doc.metadata.get('permissions_required', 'Not available')}\n"
                f"Mitigation methods:\n{mitigation_details}\n"
                f"URL: {doc.metadata.get('url', 'Not available')}\n\n"
            )
        return context
    except Exception as e:
        print(f"⚠️ Error building context: {e}")
        return "Error retrieving context information."

def call_model(message_state: MessagesState, vector_store: Chroma, num_similar: int, llm) -> Dict[str, Any]:
    """
    Call the language model with the current message state.

    Args:
        message_state (MessagesState): Current message state.
        vector_store (Chroma): Vector store for context retrieval.
        num_similar (int): Number of similar documents to retrieve.
        llm: Language model instance.

    Returns:
        dict: Dictionary with updated message history.
    """
    user_query = message_state["messages"][-1].content

    # Build conversation history
    conversation_history = "\n".join([
        f"User: {msg.content}" if isinstance(msg, HumanMessage) else f"Assistant: {msg.content}"
        for msg in message_state["messages"]
    ])

    # Build relevant context
    context = build_context(user_query, vector_store, num_similar)

    # Generate prompt with history and context
    prompt = (
        f"{config.SYSTEM_PROMPT}\n\nConversation history:\n{conversation_history}\n\n"
        f"Relevant context:\n{context}\n\nQuestion: {user_query}"
    )

    try:
        # Call the model
        model_response = llm.invoke([SystemMessage(content=prompt)])
        response_content = model_response.content

        # Add response to message history
        message_state["messages"].append(SystemMessage(content=response_content))
        return {"messages": message_state["messages"]}
    except Exception as e:
        error_msg = f"❌ Error calling language model: {e}"
        print(error_msg)
        message_state["messages"].append(SystemMessage(content=error_msg))
        return {"messages": message_state["messages"]}

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Object containing command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='MITRE ATT&CK Expert Chatbot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chatbot.py                           # Run with default settings
  python chatbot.py -o -n 10                 # Use OpenAI with 10 similar docs
  python chatbot.py -s --debug               # Use local embeddings with debug mode
        """
    )
    
    parser.add_argument(
        '-v', '--vector-store',
        type=str, default=config.VECTOR_STORE_PATH, required=False,
        help='Path to the Chroma vector store directory'
    )
    
    parser.add_argument(
        '-o', '--openai',
        action='store_true', required=False, default=True,
        help='Use OpenAI embedding models (requires API key in .env)'
    )
    
    parser.add_argument(
        '-s', '--sentence-transformers',
        action='store_true', required=False, default=False,
        help='Use local Sentence Transformers embedding models'
    )
    
    parser.add_argument(
        '-n', '--num-similar',
        type=int, default=config.NUM_SIMILAR_DOCS, required=False,
        help='Number of documents to use in context'
    )
    
    parser.add_argument(
        '-d', '--debug',
        action='store_true', required=False, default=False,
        help='Enable DEBUG mode for RAG steps'
    )
    
    return parser.parse_args()

def setup_embedding_model(use_openai: bool, use_local: bool):
    """Setup embedding model based on arguments."""
    if use_openai and config.OPENAI_API_KEY:
        return OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY
        )
    elif use_local:
        return HuggingFaceEmbeddings(model_name=config.LOCAL_EMBEDDING_MODEL)
    else:
        if not config.OPENAI_API_KEY:
            print("⚠️ No OpenAI API key found. Falling back to local embeddings.")
            return HuggingFaceEmbeddings(model_name=config.LOCAL_EMBEDDING_MODEL)
        return OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY
        )

def main():
    """Main function to run the chatbot."""
    # Parse arguments
    args = parse_arguments()
    load_dotenv()

    print("🚀 Initializing MITRE ATT&CK Expert Chatbot...")

    # Validate OpenAI API key (required for chat model)
    if not config.OPENAI_API_KEY:
        print("❌ OpenAI API key is required for the chat model.")
        print("📝 Please add your API key to the .env file:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print("🔗 Get your API key at: https://platform.openai.com/api-keys")
        sys.exit(1)

    # Setup embedding model
    try:
        embedding_model = setup_embedding_model(args.openai, args.sentence_transformers)
        print(f"✅ Embedding model configured")
    except Exception as e:
        print(f"❌ Error setting up embedding model: {e}")
        sys.exit(1)

    # Load vector store
    vector_store = load_vector_store(args.vector_store, embedding_model)

    # Setup language model
    try:
        llm = ChatOpenAI(
            model=config.CHAT_MODEL,
            api_key=config.OPENAI_API_KEY
        )
        print(f"✅ Language model configured: {config.CHAT_MODEL}")
    except Exception as e:
        print(f"❌ Error setting up language model: {e}")
        sys.exit(1)

    # Initialize chatbot workflow
    try:
        memory = MemorySaver()
        workflow = StateGraph(state_schema=MessagesState)
        workflow.add_edge(START, "model")
        workflow.add_node(
            "model", 
            lambda message_state: call_model(
                message_state,
                vector_store=vector_store,
                num_similar=args.num_similar,
                llm=llm
            )
        )
        app = workflow.compile(checkpointer=memory)
        config_dict = {"configurable": {"thread_id": "mitre_chat_session"}}
        print("✅ Chatbot workflow initialized")
    except Exception as e:
        print(f"❌ Error initializing chatbot workflow: {e}")
        sys.exit(1)

    # Start chat interface
    print("\n" + "="*60)
    print("🛡️  MITRE ATT&CK EXPERT CHATBOT")
    print("="*60)
    print("Ask me questions about tactics, techniques, or countermeasures.")
    print("End the session with: :exit, :quit, or :terminate")
    print("="*60)

    state = {"messages": [SystemMessage(content="You are a MITRE ATT&CK expert assistant.")]}
    
    try:
        while True:
            query = input("\n💬 You: ").strip()
            
            if query.lower() in config.EXIT_COMMANDS:
                print("\n🤖 Assistant: Thank you for using the MITRE ATT&CK Expert Chatbot. Goodbye! 👋")
                break
            
            if not query:
                print("⚠️ Please enter a question or use an exit command.")
                continue

            state["messages"].append(HumanMessage(content=query))
            
            try:
                print("\n🤖 Assistant: ", end="", flush=True)
                response = app.invoke(state, config_dict)
                
                # Extract and print the last assistant message
                last_message = response["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(last_message.content)
                else:
                    print("I encountered an issue generating a response. Please try again.")
                    
                state = response
                
            except Exception as e:
                print(f"❌ Error processing your question: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
                print("Please try rephrasing your question.")
                
    except KeyboardInterrupt:
        print("\n\n🤖 Assistant: Session interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
