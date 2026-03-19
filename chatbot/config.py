"""
Configuration for the Offline Plant Health Advisor chatbot.
Edit this file to change models, paths, and the system prompt.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Local model settings
# ---------------------------------------------------------------------------

# Resolve repo-local model path by default so local + Docker can run fully offline.
_DEFAULT_LOCAL_MODEL_DIR = (
	Path(__file__).resolve().parent.parent / "models" / "SmolVLM-256M-Instruct"
)

# Optional local directory for fully offline deployment.
# Example: /home/pi/models/SmolVLM-256M-Instruct
LOCAL_MULTIMODAL_MODEL_DIR: str = os.getenv(
	"LOCAL_MULTIMODAL_MODEL_DIR",
	str(_DEFAULT_LOCAL_MODEL_DIR),
)

# Generation limits for local inference.
MAX_NEW_TOKENS: int = int(os.getenv("MAX_NEW_TOKENS", "256"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))

# Keep only the latest N user/assistant turns when building prompt history.
MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "4"))

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
