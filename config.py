"""
Configuration settings for the MITRE ATT&CK Expert Chatbot.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the chatbot application."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "vector_store_mitre")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "mitre_attack_techniques")
    
    # Data Configuration
    DEFAULT_TECHNIQUES_FILE: str = "data/techniques_enterprise_attack.json"
    
    # Text Processing Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1024"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "64"))
    
    # Retrieval Configuration
    NUM_SIMILAR_DOCS: int = int(os.getenv("NUM_SIMILAR_DOCS", "6"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # Local Models Configuration
    LOCAL_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Chatbot Prompts and Messages
    SYSTEM_PROMPT: str = (
        "You are an expert assistant in MITRE ATT&CK. "
        "Provide clear and precise information about attack techniques, "
        "tactics, and countermeasures based on the MITRE knowledge base. "
        "You can also remember relevant details from the conversation "
        "to respond more efficiently and contextually "
        "in case previously seen cases are asked about. "
        "Use simple and direct language to save tokens. "
        "When responding, follow this structure:"
        "\n1. Relevant technique: Identify the technique or techniques related to the query. "
        "Provide the name, technique ID, and associated tactic."
        "\n2. Explanation: Describe how the scenario relates to the identified MITRE ATT&CK technique."
        "\n3. Mitigations: Provide specific and practical steps to mitigate risks "
        "related to the technique."
        "\nStructure your responses clearly and professionally, "
        "focusing on the user's needs."
        "\nUse simple, clear, and direct language to ensure the user "
        "can easily implement the recommendations."
    )
    
    EXIT_COMMANDS: list = [":exit", ":quit", ":terminate", ":salir"]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate the configuration."""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not found in environment variables.")
            print("OpenAI features will not be available.")
            return False
        return True

# Convenience instance
config = Config()
