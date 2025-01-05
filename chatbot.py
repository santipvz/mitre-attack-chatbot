"""
Implementación de un chatbot experto en MITRE ATT&CK con OpenAI, Langchain y FAISS.
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

TEXTO = ("Eres un asistente experto en MITRE ATT&CK. "
         "Proporcionas información clara y precisa sobre técnicas de ataque, "
         "tácticas y contramedidas basadas en la base de conocimientos de MITRE. "
         "También puedes recordar detalles relevantes de la conversación "
         "para responder de manera más eficiente y contextualizada. "
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

# Cargar variables de entorno
load_dotenv()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small",
                                   api_key=os.environ["OPENAI_API_KEY"])

# Cargar el índice previamente generado
def load_index():
    """
    Carga el índice previamente generado desde el almacenamiento local.

    Returns:
        local_vector_store: El índice cargado desde el almacenamiento local.
    """
    try:
        local_vector_store = FAISS.load_local("vector_store_index",
                                              embedding_model, allow_dangerous_deserialization=True)
        print("Índice cargado correctamente.")
        return local_vector_store
    except (FileNotFoundError, ValueError) as error:
        print("Error al cargar el índice:", error)
        sys.exit("Asegúrate de haber generado el índice correctamente con el módulo de indexación.")

vector_store = load_index()

# Configuración del modelo
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])

# Función para construir el contexto dinámico
def build_context(user_query):
    """
    Recupera documentos relevantes y construye un contexto enriquecido con datos relacionados.

    Args:
        query (str): La consulta del usuario.

    Returns:
        str: El contexto enriquecido.
    """
    docs = vector_store.similarity_search(user_query, k=4)
    context = ""
    for doc in docs:
        mitigation_details = "\n".join(
            [f"- {m.get('name', 'Sin nombre')}: {m.get('description', 'Descripción no disponible')}"
             for m in doc.metadata.get("mitigations", [])]
        )
        context += (
            f"Técnica: {doc.metadata.get('name', 'Desconocida')} "
            f"(ID: {doc.metadata.get('id', 'N/A')})\n"
            f"Tácticas: {', '.join(doc.metadata.get('tactics', []))}\n"
            f"Descripción: {doc.page_content}\n"
            f"Detección: {doc.metadata.get('detection', 'No disponible')}\n"
            f"Fuentes de datos: {', '.join(doc.metadata.get('datasources', []))}\n"
            f"Permisos requeridos: {', '.join(doc.metadata.get('permissions_required', []))}\n"
            f"Métodos de mitigación:\n{mitigation_details}\n"
            f"URL: {doc.metadata.get('url', 'No disponible')}\n\n"
        )
    return context

# Lógica del chatbot
def call_model(message_state: MessagesState):
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
    context = build_context(user_query)

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

# Configuración principal
memory = MemorySaver()
workflow = StateGraph(state_schema=MessagesState)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
app = workflow.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "session_001"}}

if __name__ == "__main__":
    # Función principal para interactuar con el chatbot
    print("\n======= CHATBOT EXPERTO EN MITRE ATT&CK =======")
    print("Hazme preguntas sobre tácticas, técnicas o contramedidas.")
    print("Finaliza la sesión con los comandos :salir, :exit o :terminar.")
    print("===============================================")

    state = {"messages": [SystemMessage(content="Eres un asistente experto en MITRE ATT&CK.")]}
    while True:
        query = input("\nUsuario: ")
        if query.lower() in [":salir", ":exit", ":terminar"]:
            print("\nGracias por hablar conmigo. ¡Hasta luego!")
            break

        state["messages"].append(HumanMessage(content=query))
        response = app.invoke(state, config)
        print("\nAsistente:", end=" ")
        response["messages"][-1].pretty_print()
