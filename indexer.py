"""
Este módulo indexa datos de un archivo JSON y almacena embeddings en un almacén vectorial FAISS.
"""

import json
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Configurar embeddings
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

def process_json(file_path):
    """
    Procesa el archivo JSON con el listado de técnicas y subtécnicas de MITRE ATT&CK.
    Crea documentos para almacenar en un vector store.

    Args:
        file_path (str): Ruta al archivo JSON.

    Returns:
        list[Document]: Lista de documentos procesados.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    documents = []
    for entry in data:
        # Construir contenido principal
        mitigation_details = "\n".join(
            [f"- {m.get('name', 'Sin nombre')}: {m.get('description', 'Descripción no disponible')}"
             for m in entry.get("mitigation_methods", [])]
        )
        page_content = (
            f"Technique Name: {entry.get('name', 'Desconocido')}\n"
            f"Description: {entry.get('description', 'Descripción no disponible')}\n"
            f"Detection: {entry.get('detection', 'No disponible')}\n"
            f"Mitigation Methods:\n{mitigation_details}"
        )

        # Construir metadatos
        metadata = {
            "id": entry["id"],
            "url": entry.get("url", "No disponible"),
            "tactics": entry.get("tactics", []),
            "platforms": entry.get("platforms", []),
            "datasources": entry.get("datasources", []),
            "permissions_required": entry.get("permissions_required", [])
        }

        # Crear documento
        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents

def index_data(file_path, output_path):
    """
    Procesa datos y los almacena en un almacén vectorial FAISS.

    Args:
        file_path (str): Ruta al archivo JSON con los datos a indexar.
        output_path (str): Ruta donde se guardará el índice FAISS.
    """
    documents = process_json(file_path)
    vector_store = FAISS.from_documents(documents, embedding_model)
    vector_store.save_local(output_path)
    print(f"Índice creado y almacenado localmente en '{output_path}'.")

if __name__ == "__main__":
    # Procesar archivo y almacenar índice
    json_file_path = "techniques_enterprise_attack.json"  # Ruta al archivo JSON
    output_index_path = "vector_store_index"  # Carpeta de salida para el índice FAISS
    index_data(json_file_path, output_index_path)
