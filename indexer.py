"""
Este módulo indexa técnicas MITRE ATT&CK desde un archivo JSON utilizando embeddings y Chroma.
"""

import sys
import os
import argparse
from dotenv import load_dotenv

from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

def main(arguments):
    """
    Función principal para indexar técnicas MITRE ATT&CK desde un archivo JSON
    utilizando embeddings y Chroma.

    Args:
        arguments (argparse.Namespace): Argumentos de la línea de comandos.
    """
    if os.path.exists(arguments.vector_store):
        sys.exit(
            f"El índice {arguments.vector_store} ya existe, no se han indexado nuevos documentos.\n"
            "Programa finalizado"
        )

    print("(1) Cargando documentos ...")
    path_documentos = arguments.techniques

    def extraer_metadatos(record: dict, metadata: dict) -> dict:
        metadata['id'] = record.get('id', 'Desconocido')
        metadata['name'] = record.get('name', 'Sin nombre')
        metadata['url'] = record.get('url', 'No disponible')
        metadata['tactics'] = ', '.join(record.get('tactics', []))
        metadata['platforms'] = ', '.join(record.get('platforms', []))
        metadata['datasources'] = ', '.join(record.get('datasources', []))
        metadata['permissions_required'] = ', '.join(record.get('permissions_required', []))
        return metadata


    loader = JSONLoader(
        file_path=path_documentos,
        jq_schema='.[]',
        text_content=False,
        content_key='description',
        metadata_func=extraer_metadatos
    )

    docs = loader.load()
    print(f"\t- {len(docs)} documentos cargados")

    print("(2) Pre-procesando documentos ...")
    if arguments.openai:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    else:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=64)

    all_splits = text_splitter.split_documents(docs)
    print(f"\t- {len(all_splits)} chunks creados")

    print("(3) Indexando documentos ...")
    if arguments.openai:
        load_dotenv()
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", api_key=os.environ["OPENAI_API_KEY"]
        )
    else:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = Chroma(
        collection_name="mitre_attack_techniques",
        embedding_function=embeddings,
        persist_directory=arguments.vector_store
    )
    vector_store.add_documents(documents=all_splits)
    print(f"\t- índice {arguments.vector_store} creado")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Indexación de técnicas MITRE ATT&CK en formato JSON con embeddings y Chroma'
    )
    parser.add_argument('-t', '--techniques',
                        type=str, default='techniques_enterprise_attack.json', required=False,
                        help='Path al fichero con las técnicas de MITRE ATT&CK en formato JSON')
    parser.add_argument('-v', '--vector-store',
                        type=str, default='chroma_mitre_attack', required=False,
                        help='Path al directorio con el vector store Chroma (lo crea si no existe)')
    parser.add_argument('-o', '--openai',
                        action='store_true', required=False, default=True,
                        help='Usa los embedding model del API de OpenAI')
    parser.add_argument('-s', '--sentence-transformers',
                        action='store_true', required=False, default=False,
                        help='Usa los embedding models locales de Sentence Transformers')

    args = parser.parse_args()
    main(args)
