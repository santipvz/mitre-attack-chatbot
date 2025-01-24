"""
Implementación de un chatbot experto en MITRE ATT&CK con OpenAI, Langchain y Chroma.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

TEXTO = ("Eres un asistente experto en MITRE ATT&CK. "
         "Proporcionas información clara y precisa sobre técnicas de ataque, "
         "tácticas y contramedidas basadas en la base de conocimientos de MITRE. "
         "También puedes recordar detalles relevantes de la conversación "
         "para responder de manera más eficiente y contextualizada "
         "en caso de que se pregunten casos anteriormente vistos."
         "Usa un lenguaje sencillo y directo para ahorrar tokens. "
         "Cuando respondas, sigue esta estructura:"
         "\n1. Técnica relevante: Identifica la técnica o técnicas relacionadas con la consulta. "
         "Proporciona el nombre, el ID de la técnica y la táctica asociada."
         "\n2. Explicación: Describe cómo se relaciona el escenario con la técnica de MITRE ATT&CK "
         "identificada."
         "\n3. Mitigaciones: Proporciona pasos específicos y prácticos para mitigar los riesgos "
         "relacionados con la técnica."
         "\nEstructura tus respuestas de forma clara y profesional, "
         "enfocándote en las necesidades del usuario."
         "\nUsa un lenguaje sencillo, claro y directo para asegurar que el usuario"
         " pueda implementar las recomendaciones fácilmente."
        )

# Cargar el índice previamente generado
def load_index(vector_store_path, embedding_model_param):
    """
    Carga el índice previamente generado desde el almacenamiento local.

    Args:
        vector_store_path (str): Path al directorio del vector store.
        embedding_model: Modelo de embeddings a utilizar.

    Returns:
        local_vector_store: El índice cargado desde el almacenamiento local.
    """
    try:
        local_vector_store = Chroma(
            collection_name="mitre_attack_techniques",
            embedding_function=embedding_model_param,
            persist_directory=vector_store_path
        )
        print("Índice cargado correctamente desde:", vector_store_path)
        return local_vector_store
    except FileNotFoundError as error:
        print("Error al cargar el índice:", error)
        sys.exit("Asegúrate de haber generado el índice correctamente con el módulo de indexación.")

# Función para construir el contexto dinámico
def build_context(user_query, local_vector_store, num_similar_docs):
    """
    Recupera documentos relevantes y construye un contexto enriquecido con datos relacionados.

    Args:
        user_query (str): La consulta del usuario.
        vector_store: Vector store para realizar la búsqueda de similitud.
        num_similar_docs (int): Número de documentos a recuperar.

    Returns:
        str: El contexto enriquecido.
    """
    docs = local_vector_store.similarity_search(user_query, k=num_similar_docs)
    context = ""
    for doc in docs:
        mitigation_details = "\n".join(
            [f"- {m.get('name', 'Sin nombre')}: {m.get('description', 'Descripción no disponible')}"
             for m in doc.metadata.get("mitigations", [])]
        )
        context += (
            f"Técnica: {doc.metadata.get('name', 'Desconocida')} "
            f"(ID: {doc.metadata.get('id', 'N/A')})\n"
            f"Tácticas: {doc.metadata.get('tactics', 'Desconocida')}\n"
            f"Descripción: {doc.page_content}\n"
            f"Detección: {doc.metadata.get('detection', 'No disponible')}\n"
            f"Fuentes de datos: {doc.metadata.get('datasources', 'No disponible')}\n"
            f"Permisos requeridos: {doc.metadata.get('permissions_required', 'No disponible')}\n"
            f"Métodos de mitigación:\n{mitigation_details}\n"
            f"URL: {doc.metadata.get('url', 'No disponible')}\n\n"
        )
    return context

# Lógica del chatbot
def call_model(message_state: MessagesState, local_vector_store, num_similar):
    """
    Llama al modelo de lenguaje con el estado actual de los mensajes.

    Args:
        state (MessagesState): El estado actual de los mensajes.

    Returns:
        dict: Un diccionario con el historial de mensajes actualizado.
    """
    user_query = message_state["messages"][-1].content  # La última consulta del usuario

    # Construir historial de conversación
    conversation_history = "\n".join([
        f"Usuario: {msg.content}" if isinstance(msg, HumanMessage) else f"Asistente: {msg.content}"
        for msg in message_state["messages"]
    ])

    # Construir contexto relevante
    context = build_context(user_query, local_vector_store, num_similar)

    # Generar el prompt con historial y contexto
    prompt = (
        f"{TEXTO}\n\nHistorial de conversación:\n{conversation_history}\n\n"
        f"Contexto relevante:\n{context}\n\nPregunta: {user_query}"
    )

    # Llamar al modelo
    model_response = llm.invoke([SystemMessage(content=prompt)])
    response_content = model_response.content

    # Agregar la respuesta al historial de mensajes
    message_state["messages"].append(SystemMessage(content=response_content))
    return {"messages": message_state["messages"]}

# Argumentos de línea de comandos
def parse_args():
    """
    Parsea los argumentos de línea de comandos.

    Returns:
        argparse.Namespace: Un objeto que contiene los argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(description='Chatbot experto en MITRE ATT&CK.')
    parser.add_argument('-v', '--vector-store',
                        type=str, default='vector_store_mitre', required=False,
                        help='Path al directorio con el vector store Chroma.')
    parser.add_argument('-o', '--openai',
                        action='store_true', required=False, default=True,
                        help=('Usa los embedding model del API de OpenAI '
                              '(requiere aportar API key en .env).'))
    parser.add_argument('-s', '--sentence-transformers',
                        action='store_true', required=False, default=False,
                        help='Usa los embedding models locales de Sentence Transformers.')
    parser.add_argument('-n', '--num-similares',
                        type=int, default=6, required=False,
                        help='Número de documentos a utilizar en el contexto.')
    parser.add_argument('-d', '--debug',
                        action='store_true', required=False, default=False,
                        help='Activar DEBUG en los pasos del RAG.')
    return parser.parse_args()

# Configuración principal
if __name__ == "__main__":
    args = parse_args()
    load_dotenv()

    # Configurar embeddings según el argumento proporcionado
    EMBEDDING_MODEL = None
    if args.openai:
        EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small",
                                           api_key=os.environ["OPENAI_API_KEY"])
    elif args.sentence_transformers:
        raise NotImplementedError("El soporte para Sentence Transformers aún no está implementado.")

    # Cargar el índice
    vector_store = load_index(args.vector_store, EMBEDDING_MODEL)

    # Configurar el modelo de lenguaje
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])

    # Inicializar el flujo de trabajo del chatbot
    memory = MemorySaver()
    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_edge(START, "model")
    workflow.add_node("model", lambda message_state: call_model(message_state,
                                                                local_vector_store=vector_store,
                                                                num_similar=args.num_similares))
    app = workflow.compile(checkpointer=memory)
    config = {"configurable": {"thread_id": "1111"}}

    print("\n======= CHATBOT EXPERTO EN MITRE ATT&CK =======")
    print("Hazme preguntas sobre tácticas, técnicas o contramedidas.")
    print("Finaliza la sesión con los comandos :salir, :exit o :terminar.")
    print("===============================================")

    state = {"messages": [SystemMessage(content="Eres un asistente experto en MITRE ATT&CK.")]}
    while True:
        query = input("\n>> Usuario: ")
        if query.lower() in [":salir", ":exit", ":terminar"]:
            print("\n>> Asistente: Gracias por hablar conmigo. ¡Hasta luego!")
            break

        state["messages"].append(HumanMessage(content=query))
        response = app.invoke(state, config)
        print("\n>> Asistente:", end=" ")
        response["messages"][-1].pretty_print()
