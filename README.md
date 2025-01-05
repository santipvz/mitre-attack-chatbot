# Chatbot Experto en MITRE ATT&CK

Este proyecto implementa un chatbot experto en el framework **MITRE ATT&CK**, utilizando tecnologías avanzadas como **OpenAI**, **LangChain** y **FAISS** para ofrecer respuestas claras y precisas sobre técnicas de ataque, tácticas y contramedidas. Además, el chatbot incluye memoria para recordar el contexto de las conversaciones.

## Características
- **Conocimiento basado en MITRE ATT&CK**: Proporciona información detallada sobre técnicas, tácticas y mitigaciones.
- **Memoria conversacional**: Recuerda el contexto y detalles relevantes dentro de una sesión.
- **Optimización de consultas**: Utiliza FAISS para búsquedas rápidas y eficaces dentro del índice de datos.
- **Modelos OpenAI**: Se apoya en modelos ligeros y económicos, como `gpt-4o-mini` para el chatbot y `text-embedding-3-small` para los embeddings.

---

## Requisitos

### Dependencias
Este proyecto utiliza las siguientes librerías y herramientas:

```
langchain
langchain_community
langchain_core
langchain_openai
langgraph
python-dotenv
faiss-cpu
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
Esto creará un índice local llamado `vector_store_index`.

### 2. Ejecutar el Chatbot
Una vez generado el índice, ejecuta el chatbot:

```bash
python chatbot.py
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
El índice generado utiliza archivos pickle, lo que requiere habilitar `allow_dangerous_deserialization=True`. Asegúrate de confiar en la fuente del índice antes de cargarlo.

---

## Créditos
- **LangChain y LangGraph** para la creación del grafo de estados y gestión del flujo conversacional.
- **FAISS** para un acceso rápido a los datos indexados.
- **OpenAI** para los modelos de lenguaje y embeddings.

---

## Contribuciones
Si tienes sugerencias o mejoras, no dudes en contribuir enviando un pull request o abriendo un issue en el repositorio.

---

## Licencia
Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo según tus necesidades.

