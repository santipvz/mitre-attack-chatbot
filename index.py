import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.environ["OPENAI_API_KEY"])

def index_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    documents = []
    for entry in data:
        content = f"""Technique ID: {entry['id']}
Name: {entry['name']}
Description: {entry['description']}
Tactics: {', '.join(entry['tactics'])}
Mitigations: {', '.join([m['name'] for m in entry.get('mitigation_methods', [])])}"""
        metadata = {"url": entry['url'], "platforms": entry['platforms']}
        documents.append(Document(page_content=content, metadata=metadata))

    # Crear y almacenar embeddings en FAISS
    vector_store = FAISS.from_documents(documents, embedding_model)
    vector_store.save_local("vector_store_index")
    print("Índice creado y almacenado localmente en 'vector_store_index'.")

if __name__ == "__main__":
    index_data("techniques_enterprise_attack.json")
