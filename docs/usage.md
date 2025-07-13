# Usage Guide

This guide provides detailed instructions on how to use the MITRE ATT&CK Expert Chatbot effectively.

## Quick Start

1. **Generate the index** (first time only):
   ```bash
   python src/indexer.py
   ```

2. **Start the chatbot**:
   ```bash
   python src/chatbot.py
   ```

3. **Ask questions** about MITRE ATT&CK:
   ```
   You: What is technique T1059?
   Assistant: T1059 is the Command and Scripting Interpreter technique...
   ```

## Indexing Data

### Basic Indexing

The simplest way to index MITRE ATT&CK data:

```bash
python src/indexer.py
```

This will:
- Use the default `techniques_enterprise_attack.json` file
- Create a vector store at `vector_store_mitre/`
- Use OpenAI embeddings (requires API key)

### Advanced Indexing Options

**Use custom data file:**
```bash
python src/indexer.py -t /path/to/custom_techniques.json
```

**Use local embeddings (no API key required):**
```bash
python src/indexer.py -s
```

**Custom vector store location:**
```bash
python src/indexer.py -v /custom/path/vector_store
```

**Force re-indexing:**
```bash
python src/indexer.py --force
```

### Indexing Performance

**For faster indexing:**
- Use OpenAI embeddings (requires internet and API key)
- Ensure good internet connection
- Use SSD storage

**For offline indexing:**
- Use Sentence Transformers with `-s` flag
- First run will download the model (~90MB)
- Subsequent runs are fully offline

## Using the Chatbot

### Basic Usage

Start the chatbot:
```bash
python src/chatbot.py
```

**Example conversation:**
```
💬 You: What is PowerShell execution?
🤖 Assistant: PowerShell execution relates to MITRE ATT&CK technique T1059.001...

💬 You: How can I detect this?
🤖 Assistant: To detect PowerShell execution, you can monitor...

💬 You: :exit
🤖 Assistant: Thank you for using the MITRE ATT&CK Expert Chatbot. Goodbye! 👋
```

### Advanced Options

**Use custom vector store:**
```bash
python src/chatbot.py -v /path/to/custom_vector_store
```

**Increase context size:**
```bash
python src/chatbot.py -n 10  # Use 10 similar documents instead of 6
```

**Use local embeddings:**
```bash
python src/chatbot.py -s
```

**Enable debug mode:**
```bash
python src/chatbot.py --debug
```

### Query Types

The chatbot can handle various types of questions:

**1. Technique-specific queries:**
- "What is T1059?"
- "Tell me about PowerShell"
- "Explain command and scripting interpreter"

**2. Tactic-based queries:**
- "What techniques are used for lateral movement?"
- "Show me persistence techniques"
- "What is privilege escalation?"

**3. Mitigation queries:**
- "How to prevent credential dumping?"
- "What are mitigations for T1003?"
- "How to detect malicious PowerShell?"

**4. Detection queries:**
- "How to detect lateral movement?"
- "What logs should I monitor for T1059?"
- "Data sources for persistence detection"

**5. Platform-specific queries:**
- "Windows-specific attack techniques"
- "Linux privilege escalation"
- "macOS persistence methods"

### Session Commands

- `:exit` - End the chat session
- `:quit` - End the chat session
- `:terminate` - End the chat session

## Best Practices

### Query Optimization

**Good queries:**
- "What is lateral movement and how to detect it?"
- "T1003 credential dumping mitigations"
- "PowerShell logging and detection"

**Less effective queries:**
- "Help" (too vague)
- Single words like "malware"
- Very long, complex questions with multiple topics

### Memory and Context

The chatbot remembers conversation context within a session:

```
You: What is T1059?
Assistant: T1059 is Command and Scripting Interpreter...

You: What are its sub-techniques?
Assistant: The sub-techniques of T1059 include...
```

**Tips for better context:**
- Ask follow-up questions in the same session
- Reference previous techniques by ID or name
- Build conversations progressively

### Performance Optimization

**For faster responses:**
- Use OpenAI embeddings
- Reduce number of similar documents (`-n` parameter)
- Use SSD storage for vector store

**For resource-constrained environments:**
- Use local embeddings with `-s`
- Reduce context size
- Close other applications

## Configuration Options

### Environment Variables

Create a `.env` file to customize behavior:

```env
# Model configuration
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Performance tuning
NUM_SIMILAR_DOCS=6
CHUNK_SIZE=1024
CHUNK_OVERLAP=64

# Paths
VECTOR_STORE_PATH=vector_store_mitre
```

### Command Line Arguments

Both `indexer.py` and `chatbot.py` support command line arguments:

```bash
# View all options
python src/indexer.py --help
python src/chatbot.py --help
```

## Troubleshooting

### Common Issues

**1. "Index not found" error:**
```bash
python src/indexer.py  # Generate the index first
```

**2. Slow responses:**
- Check internet connection (for OpenAI)
- Reduce context size with `-n 3`
- Use local embeddings with `-s`

**3. API key errors:**
- Verify `.env` file exists and contains valid API key
- Check OpenAI account credits

**4. Memory issues:**
- Use smaller chunk sizes
- Reduce number of similar documents
- Use local embeddings

### Debug Mode

Enable debug mode for detailed information:

```bash
python src/chatbot.py --debug
```

This shows:
- Vector search results
- Context building process
- Model interaction details
- Error stack traces

## Advanced Usage

### Batch Processing

For processing multiple queries:

```python
from src.chatbot import setup_embedding_model, load_vector_store

# Setup
embedding_model = setup_embedding_model(True, False)
vector_store = load_vector_store("vector_store_mitre", embedding_model)

# Process queries
queries = ["What is T1059?", "Lateral movement techniques"]
for query in queries:
    # Process each query...
```

### Custom Data Sources

To use custom MITRE data:

1. Format your data as JSON array
2. Include required fields: `id`, `name`, `description`, etc.
3. Index with custom file:
   ```bash
   python src/indexer.py -t custom_data.json
   ```