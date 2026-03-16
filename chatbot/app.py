"""
Gradio web UI for the Offline Plant Health Advisor.

Run with:
    python chatbot/app.py

Then open http://localhost:7860 in your browser.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

import gradio as gr

# Make sibling modules importable when running from the repo root.
sys.path.insert(0, os.path.dirname(__file__))

from chatbot import chat, check_ollama_available, list_available_models
from config import TEXT_MODEL, UPLOAD_DIR, VISION_MODEL
from rag import clear_documents, ingest_documents

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Gradio event handlers
# ---------------------------------------------------------------------------

def handle_send(
    user_text: str,
    image: str | None,
    history: List[Tuple[str, str]],
) -> Tuple[str, str | None, List[Tuple[str, str]]]:
    """
    Called when the user clicks Send.

    Returns:
        - Cleared text box value
        - Cleared image value
        - Updated chat history
    """
    if not user_text.strip() and image is None:
        return "", None, history

    response = chat(
        user_text=user_text.strip(),
        history=history,
        image_path=image,
    )
    history = history + [(user_text.strip() or "📷 [image]", response)]
    return "", None, history


def handle_upload_docs(files: List[str]) -> str:
    """
    Index uploaded documents into the vector store.
    Gradio passes a list of temporary file paths.
    """
    if not files:
        return "⚠️ No files selected."

    saved_paths = []
    for tmp_path in files:
        dest = os.path.join(UPLOAD_DIR, Path(tmp_path).name)
        shutil.copy(tmp_path, dest)
        saved_paths.append(dest)

    try:
        num_chunks = ingest_documents(saved_paths)
        names = ", ".join(Path(p).name for p in saved_paths)
        return f"✅ Indexed {len(saved_paths)} file(s) ({num_chunks} chunks): {names}"
    except Exception as exc:
        return f"❌ Error indexing documents: {exc}"


def handle_clear_docs() -> str:
    """Wipe the vector store and upload cache."""
    clear_documents()
    return "🗑️ All uploaded documents cleared."


def _status_message() -> str:
    """Build the status string shown at startup."""
    if check_ollama_available():
        models = list_available_models()
        model_list = ", ".join(models) if models else "none downloaded yet"
        text_ok = TEXT_MODEL in " ".join(models)
        vision_ok = VISION_MODEL in " ".join(models)
        warnings = []
        if not text_ok:
            warnings.append(f"`{TEXT_MODEL}` not found — run: ollama pull {TEXT_MODEL}")
        if not vision_ok:
            warnings.append(f"`{VISION_MODEL}` not found — run: ollama pull {VISION_MODEL}")
        status = f"✅ Ollama connected. Available models: {model_list}"
        if warnings:
            status += "\n⚠️ " + "\n⚠️ ".join(warnings)
    else:
        status = (
            "❌ Ollama is not running. "
            "Please start it with `ollama serve` and refresh this page."
        )
    return status


# ---------------------------------------------------------------------------
# Gradio UI layout
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="🌿 Offline Plant Health Advisor",
    theme=gr.themes.Soft(primary_hue="green"),
) as demo:

    gr.Markdown(
        """
        # 🌿 Offline Plant Health Advisor
        **AI-powered crop health assistant — runs 100% offline on your PC.**
        Upload plant photos or farming documents and ask anything about your crops.
        """
    )

    with gr.Row():
        status_box = gr.Textbox(
            label="Ollama Status",
            value=_status_message(),
            interactive=False,
            lines=2,
        )

    # Chat area
    chatbot_ui = gr.Chatbot(label="Chat", height=420, bubble_full_width=False)

    with gr.Row():
        text_input = gr.Textbox(
            placeholder="Ask about your plants, crops, pests, or soil…",
            label="Your message",
            scale=5,
            lines=2,
        )
        image_input = gr.Image(
            label="📷 Plant photo (optional)",
            type="filepath",
            scale=2,
        )

    with gr.Row():
        send_btn = gr.Button("Send 💬", variant="primary", scale=3)
        clear_chat_btn = gr.Button("Clear chat 🗑️", scale=1)

    gr.Markdown("---")
    gr.Markdown("### 📄 Upload Documents (PDF / TXT / Markdown)")
    gr.Markdown(
        "Upload farming guides, crop manuals, or research papers. "
        "The chatbot will answer questions using their content."
    )

    with gr.Row():
        doc_upload = gr.File(
            label="Select files",
            file_count="multiple",
            file_types=[".pdf", ".txt", ".md"],
            scale=4,
        )
        with gr.Column(scale=2):
            upload_btn = gr.Button("Index documents 📚", variant="secondary")
            clear_docs_btn = gr.Button("Clear documents 🗑️")

    doc_status = gr.Textbox(label="Document status", interactive=False)

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

    upload_btn.click(
        fn=handle_upload_docs,
        inputs=[doc_upload],
        outputs=[doc_status],
    )

    clear_docs_btn.click(
        fn=handle_clear_docs,
        outputs=[doc_status],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
