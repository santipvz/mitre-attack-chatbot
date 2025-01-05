import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Cargar variables de entorno
load_dotenv()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.environ["OPENAI_API_KEY"])

# Cargar el índice previamente generado
def load_index():
    try:
        vector_store = FAISS.load_local("vector_store_index", embedding_model, allow_dangerous_deserialization=True)
        print("Índice cargado correctamente.")
        return vector_store
    except Exception as e:
        print("Error al cargar el índice:", e)
        sys.exit("Asegúrate de haber generado el índice correctamente con el módulo de indexación.")

vector_store = load_index()

# Configuración del modelo
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])

# Definir el grafo de estados
workflow = StateGraph(state_schema=MessagesState)

# Función que llama al modelo
def call_model(state: MessagesState):
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
texto = ("Eres un asistente experto en MITRE ATT&CK. "
         "Proporcionas información clara y precisa sobre técnicas de ataque, tácticas y contramedidas basadas en la base de conocimientos de MITRE. "
         "También puedes recordar detalles relevantes de la conversación para responder de manera más eficiente y contextualizada. "
         "Usa un lenguaje sencillo y directo para ahorrar tokens.")
prompt_base = SystemMessage(texto)
# Cargar el system prompt inicial en la memoria
output = app.invoke({"messages": [prompt_base]}, config)

# Función principal para el chatbot
def main():
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
        output = app.invoke({"messages": input_messages}, config)
        print("\nAsistente:", end=" ")
        output["messages"][-1].pretty_print()  # Mostrar la última respuesta

if __name__ == "__main__":
    main()
