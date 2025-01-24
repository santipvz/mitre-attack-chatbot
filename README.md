# Chatbot Experto en MITRE ATT&CK

Este proyecto implementa un chatbot experto en el framework **MITRE ATT&CK**, utilizando tecnologías avanzadas como **OpenAI**, **LangChain** y **Chroma** para ofrecer respuestas claras y precisas sobre técnicas de ataque, tácticas y contramedidas. Además, el chatbot incluye memoria para recordar el contexto de las conversaciones.

## Características

- **Conocimiento basado en MITRE ATT&CK**: Proporciona información detallada sobre técnicas, tácticas y mitigaciones.
- **Memoria conversacional**: Recuerda el contexto y detalles relevantes dentro de una sesión.
- **Optimización de consultas**: Utiliza Chroma para búsquedas rápidas y eficaces dentro del índice de datos.
- **Modelos OpenAI**: Se apoya en modelos ligeros y económicos, como `gpt-4o-mini` para el chatbot y `text-embedding-3-small` para los embeddings.

---

## Requisitos

### Dependencias

Este proyecto utiliza las siguientes librerías y herramientas:

```
chromadb
jq
langchain
langchain-chroma
langchain-community
langchain_core
langchain-huggingface
langchain-mistralai
langchain_openai
langchain-text-splitters
langchain_community
langgraph
python-dotenv
```

Instálalas con:

```bash
pip install -r requirements.txt
```

### Variables de Entorno

Crea un archivo `.env` en el directorio raíz con la siguiente configuración:

```
OPENAI_API_KEY=tu_clave_api_de_openai
```

Reemplaza `tu_clave_api_de_openai` con tu clave de API válida.

---

## Estructura del Proyecto

```
project/
├── chatbot.py       # Módulo principal del chatbot
├── indexer.py       # Módulo para indexar datos JSON
├── techniques_enterprise_attack.json # Archivo con datos de MITRE ATT&CK
├── requirements.txt # Dependencias del proyecto
├── .env             # Variables de entorno
└── README.md        # Documentación del proyecto
```

---

## Uso

### 1. Generar el Índice

Antes de usar el chatbot, es necesario indexar los datos de **MITRE ATT&CK**. Ejecuta el módulo de indexación:

```bash
python indexer.py
```

Esto creará un índice local utilizando **Chroma** llamado `vector_store_mitre`.

Si deseas personalizar la indexación, puedes usar las siguientes opciones:

```bash
python indexer.py -h

usage: indexer.py [-h] [-t TECHNIQUES] [-v VECTOR_STORE] [-o] [-s]

Indexación de técnicas MITRE ATT&CK en formato JSON con embeddings y Chroma

options:
  -h, --help            show this help message and exit
  -t TECHNIQUES, --techniques TECHNIQUES
                        Path al fichero con las técnicas de MITRE ATT&CK en formato JSON
  -v VECTOR_STORE, --vector-store VECTOR_STORE
                        Path al directorio con el vector store Chroma (lo crea si no existe)
  -o, --openai          Usa los embedding model del API de OpenAI
  -s, --sentence-transformers
                        Usa los embedding models locales de Sentence Transformers
```

### 2. Ejecutar el Chatbot

Una vez generado el índice, ejecuta el chatbot:

```bash
python chatbot.py
```

Si deseas personalizar los parametros o funcionamiento del chatbot, puedes usar las siguientes opciones:

```bash
usage: chatbot.py [-h] [-v VECTOR_STORE] [-o] [-s] [-n NUM_SIMILARES] [-d]

Chatbot experto en MITRE ATT&CK.

options:
  -h, --help            show this help message and exit
  -v VECTOR_STORE, --vector-store VECTOR_STORE
                        Path al directorio con el vector store Chroma.
  -o, --openai          Usa los embedding model del API de OpenAI (requiere aportar API key en .env).
  -s, --sentence-transformers
                        Usa los embedding models locales de Sentence Transformers.
  -n NUM_SIMILARES, --num-similares NUM_SIMILARES
                        Número de documentos a utilizar en el contexto.
  -d, --debug           Activar DEBUG en los pasos del RAG.
```

El chatbot estará listo para responder preguntas como:

- "¿Qué es la técnica T1059?"
- "¿Cuáles son las mitigaciones para Credential Dumping?"

### 3. Finalizar Sesión

Usa los comandos `:salir`, `:exit` o `:terminar` para cerrar la sesión.

---

## Mantenimiento y Extensibilidad

### Ampliar Datos

Puedes actualizar el archivo `techniques_enterprise_attack.json` con datos adicionales de MITRE ATT&CK antes de indexar nuevamente.

### Seguridad

El índice generado utiliza archivos persistidos por Chroma. Asegúrate de confiar en la fuente de los datos antes de cargarlo.

---

## Créditos

- **LangChain y LangGraph** para la creación del grafo de estados y gestión del flujo conversacional.
- **Chroma** para un acceso rápido a los datos indexados.
- **OpenAI** para los modelos de lenguaje y embeddings.

