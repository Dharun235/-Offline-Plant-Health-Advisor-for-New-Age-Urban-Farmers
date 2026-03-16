"""
Configuration for the Offline Plant Health Advisor chatbot.
Edit this file to change models, paths, and the system prompt.
"""

import os

# ---------------------------------------------------------------------------
# Ollama settings
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Model used for plain text conversations and RAG-backed answers.
# Run `ollama pull llama3.2` to download it before starting the app.
TEXT_MODEL: str = os.getenv("TEXT_MODEL", "llama3.2")

# Model used when an image is attached to the user's message.
# Run `ollama pull llava` to download it before starting the app.
VISION_MODEL: str = os.getenv("VISION_MODEL", "llava")

# ---------------------------------------------------------------------------
# RAG / document settings
# ---------------------------------------------------------------------------

# Where uploaded files are stored on disk.
UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "data", "uploads")

# Where ChromaDB persists the vector store.
VECTORSTORE_DIR: str = os.path.join(os.path.dirname(__file__), "data", "vectorstore")

# Characters per document chunk (approximate; overlapping chunks help context).
CHUNK_SIZE: int = 800
CHUNK_OVERLAP: int = 100

# Number of document chunks retrieved for each user query.
TOP_K_DOCS: int = 4

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT: str = """You are an expert Plant Health Advisor and Urban Farming Assistant.
Your role is to help new-age urban farmers diagnose plant diseases, identify pests,
recommend treatments, and improve crop health — all with practical, actionable advice.

Guidelines:
- Focus on plant health, crop care, soil management, pest/disease control, and urban farming.
- When analyzing a photo, describe visible symptoms in detail before suggesting a cause.
- Suggest organic or low-cost remedies where possible.
- If you are unsure, say so clearly rather than guessing.
- Keep answers concise and farmer-friendly; avoid excessive jargon.
- When relevant document context is provided, prioritise information from those documents.
"""
