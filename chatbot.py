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

# Definir el grafo de estados
workflow = StateGraph(state_schema=MessagesState)

# Función que llama al modelo
def call_model(state: MessagesState):
    """
    Llama al modelo de lenguaje con el estado actual de los mensajes.

    Args:
        state (MessagesState): El estado actual de los mensajes.

    Returns:
        dict: Un diccionario con el historial de mensajes actualizado.
    """
    response = llm.invoke(state["messages"])
    # Actualizar el historial de mensajes con la respuesta
    return {"messages": response}

# Añadir nodos y transiciones al grafo
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Añadir memoria al grafo
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Configuración de la sesión actual (thread_id=1111)
config = {"configurable": {"thread_id": "1111"}}

# System prompt específico para MITRE ATT&CK
TEXTO = ("Eres un asistente experto en MITRE ATT&CK. "
         "Proporcionas información clara y precisa sobre técnicas de ataque,"
         " tácticas y contramedidas basadas en la base de conocimientos de MITRE. "
         "También puedes recordar detalles relevantes de la conversación "
         " para responder de manera más eficiente y contextualizada. "
         "Usa un lenguaje sencillo y directo para ahorrar tokens.")
prompt_base = SystemMessage(TEXTO)
# Cargar el system prompt inicial en la memoria
initial_output = app.invoke({"messages": [prompt_base]}, config)

# Función principal para el chatbot
def main():
    """
    Función principal para el chatbot experto en MITRE ATT&CK.
    Maneja la entrada del usuario y proporciona respuestas basadas
    en el grafo de estados configurado.
    """
    print("\n======= CHATBOT EXPERTO EN MITRE ATT&CK =======")
    print("Hazme preguntas sobre tácticas, técnicas o contramedidas.")
    print("Finaliza la sesión con los comandos :salir, :exit o :terminar.")
    print("===============================================")

    while True:
        query = input("\nUsuario: ")
        if query.lower() in [":salir", ":exit", ":terminar"]:
            print("\nGracias por hablar conmigo. ¡Hasta luego!")
            sys.exit()

        input_messages = [HumanMessage(query)]
        response = app.invoke({"messages": input_messages}, config)
        print("\nAsistente:", end=" ")
        response["messages"][-1].pretty_print()  # Mostrar la última respuesta

if __name__ == "__main__":
    main()
