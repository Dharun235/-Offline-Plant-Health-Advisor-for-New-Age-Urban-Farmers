"""
Configuration for the Offline Plant Health Advisor chatbot.
Edit this file to change models, paths, and the system prompt.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Local model settings
# ---------------------------------------------------------------------------

# Resolve repo-local model paths.
_DEFAULT_BASE_MODEL_DIR = (
	Path(__file__).resolve().parent.parent / "models" / "SmolVLM-256M-Instruct"
)
_DEFAULT_FINETUNED_MODEL_DIR = (
	Path(__file__).resolve().parent.parent / "models" / "SmolVLM-256M-Instruct-Agri"
)

_DEFAULT_LOCAL_MODEL_DIR = (
	_DEFAULT_FINETUNED_MODEL_DIR if _DEFAULT_FINETUNED_MODEL_DIR.exists() else _DEFAULT_BASE_MODEL_DIR
)

# Optional local directory for fully offline deployment.
# Example: /home/pi/models/SmolVLM-256M-Instruct
LOCAL_MULTIMODAL_MODEL_DIR: str = os.getenv(
	"LOCAL_MULTIMODAL_MODEL_DIR",
	str(_DEFAULT_LOCAL_MODEL_DIR),
)

# Fallback model folder (used if primary model path does not exist).
FALLBACK_LOCAL_MODEL_DIR: str = os.getenv(
	"FALLBACK_LOCAL_MODEL_DIR",
	str(_DEFAULT_BASE_MODEL_DIR),
)

# Generation limits for local inference.
MAX_NEW_TOKENS: int = int(os.getenv("MAX_NEW_TOKENS", "256"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))

# Keep only the latest N user/assistant turns when building prompt history.
MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "4"))

# ---------------------------------------------------------------------------
# Optional local RAG settings
# ---------------------------------------------------------------------------

RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "1").strip().lower() in {"1", "true", "yes"}
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
RAG_CORPUS_PATH: str = os.getenv(
	"RAG_CORPUS_PATH",
	str(Path(__file__).resolve().parent.parent / "data" / "rag" / "corpus.jsonl"),
)

# ---------------------------------------------------------------------------
# Server and access controls
# ---------------------------------------------------------------------------

SERVER_NAME: str = os.getenv("SERVER_NAME", "0.0.0.0")
SERVER_PORT: int = int(os.getenv("SERVER_PORT", "7860"))

# Optional Gradio share link (temporary public relay URL from Gradio service).
GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "0").strip().lower() in {"1", "true", "yes"}

# Optional app auth for basic protection.
APP_USERNAME: str = os.getenv("APP_USERNAME", "dharun").strip()
APP_PASSWORD: str = os.getenv("APP_PASSWORD", "dharun").strip()
APP_AUTH_ENABLED: bool = os.getenv("APP_AUTH_ENABLED", "1").strip().lower() in {"1", "true", "yes"}

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
"""
