"""
Gradio web UI for the Offline Plant Health Advisor.

Run with:
    python chatbot/app.py

Then open http://localhost:7860 in your browser.
"""

from __future__ import annotations

import os
import sys
from typing import Any, List

import gradio as gr

# Make sibling modules importable when running from the repo root.
sys.path.insert(0, os.path.dirname(__file__))

from chatbot import chat, check_backend_available, list_available_models
from config import FALLBACK_LOCAL_MODEL_DIR, LOCAL_MULTIMODAL_MODEL_DIR

# ---------------------------------------------------------------------------
# Gradio event handlers
# ---------------------------------------------------------------------------

def _content_to_text(content: Any) -> str:
    """Convert Gradio Chatbot content payloads to plain text."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                # Gradio message segments can look like:
                # {"type": "text", "text": "..."}
                text = item.get("text") or item.get("value")
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(p for p in parts if p).strip()

    return ""

def handle_send(user_text: str, image: str | None, history: List[dict] | None):
    history = history or []
    if not user_text.strip() and image is None:
        return "", None, history

    # Convert Gradio history to list of (user, assistant) tuples expected by backend
    tuple_history = []
    pending_user = ""
    for message in history:
        role = message.get("role")
        text = _content_to_text(message.get("content", ""))

        if role == "user":
            pending_user = text
        elif role == "assistant":
            if pending_user or text:
                tuple_history.append((pending_user, text))
            pending_user = ""

    # Ignore trailing unmatched user turn, because current user turn is sent separately.

    try:
        response = chat(
            user_text=user_text.strip(),
            history=tuple_history,
            image_path=image,
        )
    except Exception as exc:
        response = (
            "Unable to get a response from the local model. "
            "This usually means the model ran out of memory or failed to load. "
            "Please check your model path/config and try again. "
            f"\n\nDetails: {exc}"
        )

    # Append new messages in Gradio format
    history = history + [
        {"role": "user", "content": user_text.strip() or "[image]"},
        {"role": "assistant", "content": response},
    ]
    return "", None, history


def _status_message() -> str:
    """Build the status string shown at startup."""
    if check_backend_available():
        model_list = ", ".join(list_available_models())
        configured_source = LOCAL_MULTIMODAL_MODEL_DIR
        status = (
            "Local multimodal backend is ready. "
            f"Configured model: {configured_source}"
        )
        if model_list:
            status += f"\nActive model source: {model_list}"
        if FALLBACK_LOCAL_MODEL_DIR:
            status += f"\nFallback model source: {FALLBACK_LOCAL_MODEL_DIR}"
    else:
        status = (
            "Local multimodal model is not ready. "
            "Set LOCAL_MULTIMODAL_MODEL_DIR in config for offline use."
        )
    return status


# ---------------------------------------------------------------------------
# Gradio UI layout
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="Offline Plant Health Advisor",
) as demo:

    gr.Markdown(
        """
        # Offline Plant Health Advisor
        Local assistant for plant health guidance using text and image input.
        """
    )

    with gr.Row():
        gr.Textbox(
            label="Backend Status",
            value=_status_message(),
            interactive=False,
            lines=2,
        )

    # Chat area
    chatbot_ui = gr.Chatbot(label="Chat", height=420)

    with gr.Row():
        text_input = gr.Textbox(
            placeholder="Ask about your plants, crops, pests, or soil…",
            label="Your message",
            scale=5,
            lines=2,
        )
        image_input = gr.Image(
            label="Plant image (optional)",
            type="filepath",
            scale=2,
        )

    with gr.Row():
        send_btn = gr.Button("Send", variant="primary", scale=3)
        clear_chat_btn = gr.Button("Clear", scale=1)

    # -----------------------------------------------------------------------
    # Wire up events
    # -----------------------------------------------------------------------
    send_btn.click(
        fn=handle_send,
        inputs=[text_input, image_input, chatbot_ui],
        outputs=[text_input, image_input, chatbot_ui],
    )

    text_input.submit(
        fn=handle_send,
        inputs=[text_input, image_input, chatbot_ui],
        outputs=[text_input, image_input, chatbot_ui],
    )

    clear_chat_btn.click(
        fn=lambda: ([], "", None),
        outputs=[chatbot_ui, text_input, image_input],
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(primary_hue="green"),
    )
