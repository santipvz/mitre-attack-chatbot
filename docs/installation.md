# Installation Guide

This guide will help you install and set up the MITRE ATT&CK Expert Chatbot on your system.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM (8GB recommended for local embeddings)
- **Storage**: At least 2GB free space
- **Internet Connection**: Required for OpenAI API and initial setup

## Installation Methods

### Method 1: Quick Install (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mitre-attack-chatbot.git
   cd mitre-attack-chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv mitre_env
   
   # On Windows
   mitre_env\Scripts\activate
   
   # On macOS/Linux
   source mitre_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

5. **Generate the index**
   ```bash
   python src/indexer.py
   ```

6. **Run the chatbot**
   ```bash
   python src/chatbot.py
   ```

### Method 2: Development Install

If you plan to contribute or modify the code:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mitre-attack-chatbot.git
   cd mitre-attack-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install in development mode**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt  # If available
   ```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following content:

```env
# Required for OpenAI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional configurations
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_PATH=vector_store_mitre
NUM_SIMILAR_DOCS=6
```

### Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Verification

Test your installation:

```bash
# Test the indexer
python src/indexer.py --help

# Test the chatbot
python src/chatbot.py --help

# Run basic tests (if available)
python -m pytest tests/
```

## Troubleshooting

### Common Issues

**1. ImportError: No module named 'langchain'**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**2. OpenAI API Key Error**
- Make sure your `.env` file is in the root directory
- Verify your API key is correct and has sufficient credits
- Check if the key has the necessary permissions

**3. ChromaDB Issues**
```bash
pip install --upgrade chromadb
```

**4. Memory Issues with Local Embeddings**
- Reduce batch size in indexer
- Use OpenAI embeddings instead
- Increase system memory or use swap space

**5. Permission Errors**
```bash
# On Linux/macOS
sudo chown -R $USER:$USER vector_store_mitre/

# On Windows, run as Administrator
```