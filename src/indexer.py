"""
This module indexes MITRE ATT&CK techniques from a JSON file using embeddings and Chroma.
"""

import sys
import os
import argparse
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

# Import configuration
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config
except ImportError:
    # Fallback if config.py is not available
    load_dotenv()
    class Config:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        EMBEDDING_MODEL = "text-embedding-3-small"
        VECTOR_STORE_PATH = "vector_store_mitre"
        COLLECTION_NAME = "mitre_attack_techniques"
        CHUNK_SIZE = 1024
        CHUNK_OVERLAP = 64
        LOCAL_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
        DEFAULT_TECHNIQUES_FILE = "data/techniques_enterprise_attack.json"
    config = Config()

def extract_metadata(record: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a MITRE ATT&CK technique record.
    
    Args:
        record (dict): The technique record from JSON.
        metadata (dict): Existing metadata dictionary.
    
    Returns:
        dict: Updated metadata dictionary.
    """
    metadata['id'] = record.get('id', 'Unknown')
    metadata['name'] = record.get('name', 'No name')
    metadata['url'] = record.get('url', 'Not available')
    metadata['tactics'] = ', '.join(record.get('tactics', []))
    metadata['platforms'] = ', '.join(record.get('platforms', []))
    metadata['datasources'] = ', '.join(record.get('datasources', []))
    metadata['permissions_required'] = ', '.join(record.get('permissions_required', []))
    metadata['detection'] = record.get('detection', 'Not available')
    metadata['mitigations'] = record.get('mitigations', [])
    return metadata

def load_documents(techniques_file: str) -> List:
    """
    Load MITRE ATT&CK techniques from JSON file.
    
    Args:
        techniques_file (str): Path to the techniques JSON file.
    
    Returns:
        list: List of loaded documents.
    """
    if not os.path.exists(techniques_file):
        sys.exit(f"❌ Error: Techniques file not found: {techniques_file}")
    
    try:
        loader = JSONLoader(
            file_path=techniques_file,
            jq_schema='.[]',
            text_content=False,
            content_key='description',
            metadata_func=extract_metadata
        )
        docs = loader.load()
        print(f"✅ Loaded {len(docs)} documents from {techniques_file}")
        return docs
    except Exception as e:
        sys.exit(f"❌ Error loading documents: {e}")

def split_documents(docs: List, use_openai: bool = True) -> List:
    """
    Split documents into chunks for processing.
    
    Args:
        docs (list): List of documents to split.
        use_openai (bool): Whether to use OpenAI-optimized chunk sizes.
    
    Returns:
        list: List of document chunks.
    """
    try:
        if use_openai:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.CHUNK_SIZE, 
                chunk_overlap=config.CHUNK_OVERLAP
            )
        else:
            # Smaller chunks for local models
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=256, 
                chunk_overlap=64
            )
        
        all_splits = text_splitter.split_documents(docs)
        print(f"✅ Created {len(all_splits)} document chunks")
        return all_splits
    except Exception as e:
        sys.exit(f"❌ Error splitting documents: {e}")

def setup_embeddings(use_openai: bool, use_local: bool):
    """
    Setup embedding model based on user preferences.
    
    Args:
        use_openai (bool): Whether to use OpenAI embeddings.
        use_local (bool): Whether to use local embeddings.
    
    Returns:
        Embedding model instance.
    """
    if use_openai and config.OPENAI_API_KEY:
        try:
            embeddings = OpenAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                api_key=config.OPENAI_API_KEY
            )
            print(f"✅ Using OpenAI embeddings: {config.EMBEDDING_MODEL}")
            return embeddings
        except Exception as e:
            print(f"⚠️ Error setting up OpenAI embeddings: {e}")
            print("Falling back to local embeddings...")
            use_local = True
    
    if use_local or not config.OPENAI_API_KEY:
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=config.LOCAL_EMBEDDING_MODEL
            )
            print(f"✅ Using local embeddings: {config.LOCAL_EMBEDDING_MODEL}")
            return embeddings
        except Exception as e:
            sys.exit(f"❌ Error setting up local embeddings: {e}")
    
    sys.exit("❌ No valid embedding configuration found")

def create_vector_store(documents: List, embeddings, vector_store_path: str) -> None:
    """
    Create and populate the vector store.
    
    Args:
        documents (list): List of document chunks.
        embeddings: Embedding model instance.
        vector_store_path (str): Path to store the vector database.
    """
    try:
        print("🔄 Creating vector store and computing embeddings...")
        vector_store = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=vector_store_path
        )
        
        # Add documents in batches to avoid memory issues
        batch_size = 100
        total_docs = len(documents)
        
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i+batch_size]
            vector_store.add_documents(documents=batch)
            print(f"📊 Processed {min(i+batch_size, total_docs)}/{total_docs} documents")
        
        print(f"✅ Vector store created successfully at: {vector_store_path}")
        print(f"📈 Total documents indexed: {total_docs}")
        
    except Exception as e:
        sys.exit(f"❌ Error creating vector store: {e}")

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Object containing command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Index MITRE ATT&CK techniques from JSON format with embeddings and Chroma',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python indexer.py                           # Index with default settings
  python indexer.py -t custom_data.json      # Use custom techniques file
  python indexer.py -s                       # Use local embeddings only
  python indexer.py -v custom_store          # Use custom vector store path
        """
    )
    
    parser.add_argument(
        '-t', '--techniques',
        type=str, default=config.DEFAULT_TECHNIQUES_FILE, required=False,
        help='Path to the MITRE ATT&CK techniques JSON file'
    )
    
    parser.add_argument(
        '-v', '--vector-store',
        type=str, default=config.VECTOR_STORE_PATH, required=False,
        help='Path to the Chroma vector store directory (creates if not exists)'
    )
    
    parser.add_argument(
        '-o', '--openai',
        action='store_true', required=False, default=True,
        help='Use OpenAI embedding models'
    )
    
    parser.add_argument(
        '-s', '--sentence-transformers',
        action='store_true', required=False, default=False,
        help='Use local Sentence Transformers embedding models'
    )
    
    parser.add_argument(
        '--force',
        action='store_true', required=False, default=False,
        help='Force re-indexing even if vector store already exists'
    )
    
    return parser.parse_args()

def main():
    """
    Main function to index MITRE ATT&CK techniques.
    """
    args = parse_arguments()
    load_dotenv()
    
    print("🚀 Starting MITRE ATT&CK indexing process...")
    
    # Check if vector store already exists
    if os.path.exists(args.vector_store) and not args.force:
        print(f"⚠️ Vector store already exists at: {args.vector_store}")
        print("Use --force flag to re-index or choose a different path with -v")
        sys.exit(0)
    
    # Remove existing vector store if force flag is used
    if args.force and os.path.exists(args.vector_store):
        import shutil
        shutil.rmtree(args.vector_store)
        print(f"🗑️ Removed existing vector store: {args.vector_store}")
    
    # Step 1: Load documents
    print("\n📂 Step 1: Loading documents...")
    documents = load_documents(args.techniques)
    
    # Step 2: Split documents
    print("\n✂️ Step 2: Splitting documents...")
    document_chunks = split_documents(documents, args.openai)
    
    # Step 3: Setup embeddings
    print("\n🔧 Step 3: Setting up embeddings...")
    embeddings = setup_embeddings(args.openai, args.sentence_transformers)
    
    # Step 4: Create vector store
    print("\n💾 Step 4: Creating vector store...")
    create_vector_store(document_chunks, embeddings, args.vector_store)
    
    print("\n🎉 Indexing completed successfully!")
    print(f"📍 Vector store location: {os.path.abspath(args.vector_store)}")
    print("✨ You can now run the chatbot with: python chatbot.py")

if __name__ == '__main__':
    main()
