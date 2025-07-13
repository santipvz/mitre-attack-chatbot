# MITRE ATT&CK Expert Chatbot

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com/)

An intelligent chatbot specialized in the **MITRE ATT&CK** framework, built with advanced technologies like **OpenAI**, **LangChain**, and **Chroma** to provide clear and precise answers about attack techniques, tactics, and countermeasures. The chatbot includes conversational memory to maintain context across sessions.

## 🌟 Features

- **MITRE ATT&CK Knowledge Base**: Provides detailed information about techniques, tactics, and mitigations
- **Conversational Memory**: Remembers context and relevant details within a session
- **Query Optimization**: Uses Chroma for fast and efficient searches within the data index
- **OpenAI Models**: Leverages lightweight and cost-effective models like `gpt-4o-mini` for chat and `text-embedding-3-small` for embeddings
- **CLI Interface**: Command-line interface with multiple configuration options
- **Flexible Embedding Options**: Support for both OpenAI and local Sentence Transformers models

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API Key (for OpenAI embeddings and chat model)

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:santipvz/mitre-attack-chatbot.git
   cd mitre-attack-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Generate the index**
   ```bash
   python3 indexer.py
   ```

5. **Run the chatbot**
   ```bash
   python3 chatbot.py
   ```

## 📁 Project Structure

```
mitre-attack-chatbot/
├── src/
│   ├── __init__.py
│   ├── chatbot.py              # Main chatbot module
│   ├── indexer.py              # Data indexing module
│   ├── config.py               # Configuration settings
│   └── utils/
│       ├── __init__.py
│       └── text_processing.py  # Text processing utilities
├── data/
│   └── techniques_enterprise_attack.json  # MITRE ATT&CK data
├── tests/
│   ├── __init__.py
│   ├── test_chatbot.py         # Chatbot functionality tests
│   ├── test_indexer.py         # Indexer functionality tests
│   └── test_text_processing.py # Text processing tests
├── docs/
│   ├── installation.md         # Installation guide
│   └── usage.md               # Usage documentation
├── vector_store_mitre/         # Generated vector store (after indexing)
├── .env.example               # Environment variables template
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── README.md               # This file
└── LICENSE                # MIT License
```

## 🔧 Usage

### Indexing MITRE ATT&CK Data

Before using the chatbot, you need to index the MITRE ATT&CK data:

```bash
python3 indexer.py
```

**Indexing Options:**
```bash
python3 indexer.py -h

usage: indexer.py [-h] [-t TECHNIQUES] [-v VECTOR_STORE] [-o] [-s]

Index MITRE ATT&CK techniques from JSON format with embeddings and Chroma

options:
  -h, --help            show this help message and exit
  -t TECHNIQUES, --techniques TECHNIQUES
                        Path to the MITRE ATT&CK techniques JSON file
  -v VECTOR_STORE, --vector-store VECTOR_STORE
                        Path to the Chroma vector store directory (creates if not exists)
  -o, --openai          Use OpenAI embedding models
  -s, --sentence-transformers
                        Use local Sentence Transformers embedding models
```

### Running the Chatbot

Once the index is generated, run the chatbot:

```bash
python3 chatbot.py
```

**Chatbot Options:**
```bash
python3 chatbot.py -h

usage: chatbot.py [-h] [-v VECTOR_STORE] [-o] [-s] [-n NUM_SIMILAR] [-d]

MITRE ATT&CK Expert Chatbot

options:
  -h, --help            show this help message and exit
  -v VECTOR_STORE, --vector-store VECTOR_STORE
                        Path to the Chroma vector store directory
  -o, --openai          Use OpenAI embedding models (requires API key in .env)
  -s, --sentence-transformers
                        Use local Sentence Transformers embedding models
  -n NUM_SIMILAR, --num-similar NUM_SIMILAR
                        Number of documents to use in context
  -d, --debug           Enable DEBUG mode for RAG steps
```

### Example Queries

The chatbot can answer questions like:
- "What is technique T1059?"
- "What are the mitigations for Credential Dumping?"
- "How does PowerShell relate to MITRE ATT&CK?"
- "Show me detection methods for lateral movement"

### Session Commands

- `:exit`, `:quit`, or `:terminate` - End the chat session

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes (for OpenAI models) |

### Model Configuration

The chatbot supports two embedding options:

1. **OpenAI Embeddings** (default, requires API key)
   - Model: `text-embedding-3-small`
   - Higher quality but requires internet connection

2. **Local Sentence Transformers** (offline)
   - Model: `sentence-transformers/all-MiniLM-L6-v2`
   - No API key required, runs locally


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
