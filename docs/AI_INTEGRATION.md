# KnightX_fsm - AI Integration Guide

## Overview

KnightX_fsm integrates with **Ollama** for local Large Language Model (LLM) processing. All AI features run locally - no data is sent to external cloud services.

## Features

| Feature | Description |
|---------|-------------|
| AI Chat Assistant | Conversational AI for file management questions |
| Directory Summarization | AI-generated summaries of folder contents |
| Security Tips | Practical cybersecurity advice |
| Cleanup Advice | Guidance on freeing disk space |
| Anomaly Detection | AI-powered file risk scoring (explorer integration) |

---

## Setup

### 1. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows
# Download from https://ollama.com/download
```

### 2. Start Ollama Server

```bash
ollama serve &
```

The server runs on `http://localhost:11434` by default.

### 3. Pull a Model

```bash
# Recommended model
ollama pull llama3.2

# Alternative models
ollama pull codellama
ollama pull mistral
ollama pull phi3
```

### 4. Configure in KnightX_fsm

1. Launch KnightX_fsm
2. Navigate to **AI Assistant** tab
3. Enter model name (default: `llama3.2`)
4. Click **Pull Model** if not already pulled
5. The AI status indicator will show "Online" when connected

---

## API Configuration

AI connection settings are in `config.py`:

```python
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"
AI_ANOMALY_THRESHOLD = 0.7
```

To change the model or server URL, edit `config.py` and restart the application.

---

## Using the AI Assistant

### Chat

Type any question in the input field and press Enter or click Send:

- "How do I free up disk space?"
- "What are the best security practices for file management?"
- "Explain what a duplicate file is"
- "How does ClamAV virus scanning work?"

### Quick Actions

Pre-built buttons for common queries:

- **Summarize Directory** - AI summary of your home directory
- **Security Tips** - 5 practical security recommendations
- **Cleanup Advice** - Guidance on safe file cleanup

---

## Anomaly Detection (Explorer)

When scanning files in the File Explorer, the AI can assign risk scores (0.0-1.0) based on:

- File location (unusual directories)
- File size anomalies
- Double extensions (e.g., `file.pdf.exe`)
- Hidden files
- Executable scripts in user directories

Risk scores are displayed in future UI updates.

---

## Privacy & Security

- **Local Processing** - All AI requests go to your local Ollama instance
- **No Cloud** - No data sent to external AI providers
- **Ollama Data** - Ollama stores models locally; review Ollama's privacy policy
- **Network** - Only local HTTP (localhost:11434) unless you configure a remote Ollama server

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| AI: Offline | Start Ollama: `ollama serve` |
| Model not found | Pull model: `ollama pull llama3.2` |
| Slow responses | Use a smaller model (phi3, mistral-7b) |
| Connection refused | Check Ollama is running: `curl http://localhost:11434/api/tags` |

### Verify Ollama

```bash
# Check if server is running
curl http://localhost:11434/api/tags

# List available models
ollama list

# Test a query
curl http://localhost:11434/api/generate -d '{"model":"llama3.2","prompt":"Hello","stream":false}'
```

---

## Custom Model Integration

To use a different LLM backend, modify `ai_integration.py`:

1. Substitute the `requests.post()` calls with your API provider
2. Update `AIManager.chat()` and `AIManager.analyze_file_anomaly()`
3. Adjust prompt formatting as needed

Example for OpenAI-compatible API:

```python
import openai

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
response = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": message}]
)
return response.choices[0].message.content
```
