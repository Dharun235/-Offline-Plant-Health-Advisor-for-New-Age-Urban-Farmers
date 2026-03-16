"""
Core chatbot logic.

Handles communication with Ollama for:
  - Text-only chat (with optional RAG context from uploaded documents)
  - Vision chat (text + image sent to the vision model)

Maintains a rolling conversation history so the model has context across turns.
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import List, Tuple

import ollama

from config import OLLAMA_BASE_URL, SYSTEM_PROMPT, TEXT_MODEL, VISION_MODEL
from rag import retrieve_context

# Chat history type: list of (user_message, assistant_response) pairs.
History = List[Tuple[str, str]]


def _encode_image(image_path: str) -> str:
    """Return a base64-encoded string for the given image file."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _build_messages(
    user_text: str,
    history: History,
    rag_context: str = "",
    image_path: str | None = None,
) -> list:
    """
    Assemble the full message list to send to Ollama.

    Structure:
      1. System prompt (agriculture-tuned)
      2. Conversation history (alternating user/assistant)
      3. (Optional) RAG context injected as a system note
      4. Current user message (with optional image)
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Conversation history
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})

    # Inject retrieved document context before the current user turn
    if rag_context:
        context_note = (
            "The following excerpts are from documents the user uploaded. "
            "Use them to inform your answer where relevant.\n\n"
            f"{rag_context}"
        )
        messages.append({"role": "system", "content": context_note})

    # Current user message
    if image_path:
        messages.append(
            {
                "role": "user",
                "content": user_text or "What can you tell me about this plant?",
                "images": [_encode_image(image_path)],
            }
        )
    else:
        messages.append({"role": "user", "content": user_text})

    return messages


def chat(
    user_text: str,
    history: History,
    image_path: str | None = None,
) -> str:
    """
    Send a message to the appropriate Ollama model and return the response text.

    - If *image_path* is provided, the vision model is used.
    - Otherwise RAG context is retrieved and the text model is used.
    """
    rag_context = ""
    model = TEXT_MODEL

    if image_path:
        model = VISION_MODEL
    else:
        rag_context = retrieve_context(user_text)

    messages = _build_messages(
        user_text=user_text,
        history=history,
        rag_context=rag_context,
        image_path=image_path,
    )

    client = ollama.Client(host=OLLAMA_BASE_URL)
    response = client.chat(model=model, messages=messages)
    return response["message"]["content"]


def check_ollama_available() -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        client.list()
        return True
    except Exception:
        return False


def list_available_models() -> List[str]:
    """Return the names of all models downloaded in Ollama."""
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        result = client.list()
        return [m["name"] for m in result.get("models", [])]
    except Exception:
        return []
