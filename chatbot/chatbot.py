"""
Core chatbot logic for Offline Plant Health Advisor.
"""

from __future__ import annotations
from functools import lru_cache
import io
from pathlib import Path
from typing import Any, List, Tuple

import torch
from PIL import Image
import transformers

from config import (
    LOCAL_MULTIMODAL_MODEL_DIR,
    MAX_HISTORY_TURNS,
    MAX_NEW_TOKENS,
    SYSTEM_PROMPT,
    TEMPERATURE,
)

# Chat history type: list of (user_message, assistant_response) pairs.
History = List[Tuple[str, str]]


def _model_source() -> str:
    model_dir = (LOCAL_MULTIMODAL_MODEL_DIR or "").strip()
    if not model_dir:
        raise RuntimeError(
            "LOCAL_MULTIMODAL_MODEL_DIR is not set. "
            "For full offline mode, point it to your local model folder."
        )

    resolved = Path(model_dir).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(
            f"Local model directory not found: {resolved}. "
            "Download/copy SmolVLM files into this folder."
        )
    return str(resolved)


@lru_cache(maxsize=1)
def _get_processor() -> Any:
    return transformers.AutoProcessor.from_pretrained(
        _model_source(),
        local_files_only=True,
        trust_remote_code=True,
    )


@lru_cache(maxsize=1)
def _get_model() -> Any:
    auto_model_cls = getattr(transformers, "AutoModelForImageTextToText")
    model = auto_model_cls.from_pretrained(
        _model_source(),
        local_files_only=True,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    model.eval()
    return model


def _normalize_image_bytes(image_path: str) -> bytes:
    """
    Read an image and normalize it to PNG bytes.

    This avoids crashes in some vision runners when they receive
    unsupported/corrupt bytes from temporary uploads.
    """
    from PIL import Image

    with open(image_path, "rb") as f:
        raw = f.read()

    try:
        with Image.open(io.BytesIO(raw)) as img:
            img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
    except Exception as exc:
        raise ValueError(
            "Invalid or unsupported image file. Please upload a standard JPG/PNG image."
        ) from exc


def _load_image(image_path: str) -> Image.Image:
    return Image.open(io.BytesIO(_normalize_image_bytes(image_path))).convert("RGB")


def _build_prompt_messages(
    user_text: str,
    history: History,
    image_path: str | None = None,
) -> tuple[list[dict[str, object]], list[Image.Image]]:
    """
    Assemble messages for the local multimodal model.
    """
    messages: list[dict[str, object]] = []
    images: list[Image.Image] = []

    history_to_use = history[-MAX_HISTORY_TURNS:] if MAX_HISTORY_TURNS > 0 else history

    messages.append(
        {
            "role": "system",
            "content": [{"type": "text", "text": SYSTEM_PROMPT}],
        }
    )

    for user_msg, assistant_msg in history_to_use:
        if user_msg:
            messages.append(
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_msg}],
                }
            )
        if assistant_msg:
            messages.append(
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": assistant_msg}],
                }
            )

    content: list[dict[str, str]] = []
    if image_path:
        images.append(_load_image(image_path))
        content.append({"type": "image"})
    content.append(
        {
            "type": "text",
            "text": user_text or "Please analyze this plant image.",
        }
    )
    messages.append({"role": "user", "content": content})

    return messages, images


def chat(
    user_text: str,
    history: History,
    image_path: str | None = None,
) -> str:
    """
    Send a message to the local multimodal model and return the reply.
    """
    messages, images = _build_prompt_messages(
        user_text=user_text,
        history=history,
        image_path=image_path,
    )

    processor = _get_processor()
    model = _get_model()
    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt, images=images or None, return_tensors="pt")

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=TEMPERATURE > 0,
            temperature=TEMPERATURE,
        )

    prompt_length = inputs["input_ids"].shape[1]
    response_ids = generated_ids[:, prompt_length:]
    return processor.batch_decode(response_ids, skip_special_tokens=True)[0].strip()


def check_backend_available() -> bool:
    """Return True if the configured local model can be resolved."""
    try:
        _get_processor()
        return True
    except Exception:
        return False


def list_available_models() -> List[str]:
    """Return the configured local model identifier."""
    try:
        return [_model_source()]
    except Exception:
        return []