# MITRE ATT&CK Expert Chatbot

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

##  Usage

### Indexing MITRE ATT&CK Data

Before using the chatbot, you need to index the MITRE ATT&CK data:

```bash
python3 indexer.py
```

**Main options:**
- `-o, --openai` - Use OpenAI embedding models
- `-s, --sentence-transformers` - Use local Sentence Transformers models
- `-t, --techniques` - Custom path to techniques JSON file

### Running the Chatbot

Once the index is generated, run the chatbot:

```bash
python3 chatbot.py
```

**Main options:**
- `-o, --openai` - Use OpenAI embedding models (requires API key)
- `-s, --sentence-transformers` - Use local models (offline)
- `-n, --num-similar` - Number of documents to use in context
- `-d, --debug` - Enable debug mode for RAG steps

### Example Queries

- "What is technique T1059 and its sub-techniques?"
- "What are the mitigations for Credential Dumping attacks?"
- "How does PowerShell relate to MITRE ATT&CK framework?"
- "Show me detection methods for lateral movement techniques"
- "What are the most common persistence techniques?"

## 🛠️ Configuration

### Environment Variables

Set your OpenAI API key in a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```
*Note: Only required when using OpenAI embedding models*

### Embedding Models

The chatbot supports two embedding options:

1. **OpenAI Embeddings** (default, requires API key)
   - Model: `text-embedding-3-small`
   - Higher quality, requires internet connection

2. **Local Sentence Transformers** (offline)
   - Model: `sentence-transformers/all-MiniLM-L6-v2`
   - No API key required, runs completely offline

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
