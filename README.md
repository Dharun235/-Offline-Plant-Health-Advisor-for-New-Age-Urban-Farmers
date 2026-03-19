# Offline Plant Health Advisor

This project provides a local chatbot for plant health support. It accepts text and plant images and returns practical guidance for common disease and care issues.

The application is configured for offline operation with a local model directory.

## Features

- Text chat for plant and crop questions
- Image + text analysis for visible symptoms
- Browser UI using Gradio
- Local/offline model loading
- Docker support for macOS and Raspberry Pi

## Quick start (local Python)

```bash
git clone https://github.com/Dharun235/-Offline-Plant-Health-Advisor-for-New-Age-Urban-Farmers.git
cd -Offline-Plant-Health-Advisor-for-New-Age-Urban-Farmers

python -m venv .venv
source .venv/bin/activate
pip install -r chatbot/requirements.txt

python chatbot/app.py
```

Open http://localhost:7860

## Configuration

Main settings are in [chatbot/config.py](chatbot/config.py).

Important environment variables:

- `LOCAL_MULTIMODAL_MODEL_DIR` (default prefers `./models/SmolVLM-256M-Instruct-Agri`, fallback to base model)
- `FALLBACK_LOCAL_MODEL_DIR`
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- `MAX_NEW_TOKENS`
- `TEMPERATURE`
- `MAX_HISTORY_TURNS`
- `RAG_ENABLED`
- `RAG_TOP_K`
- `RAG_CORPUS_PATH`

## Docker (macOS and Raspberry Pi)

Files used:

- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [.env.example](.env.example)

### 1) Download model files

Run once on a machine with internet access:

```bash
huggingface-cli download HuggingFaceTB/SmolVLM-256M-Instruct --local-dir ./models/SmolVLM-256M-Instruct
```

### 2) Create the environment file

```bash
cp .env.example .env
```

### 3) Start the service

```bash
docker compose up --build
```

Open http://localhost:7860

## Fine-tuning for agriculture data

Use the single notebook:

[Full_Pipeline_Colab.ipynb](Full_Pipeline_Colab.ipynb)

This notebook runs the complete workflow:

- prepare dataset
- build RAG corpus
- fine-tune model
- export and zip artifacts for download

For macOS/no-CUDA, it automatically runs without CUDA quantization.

After pipeline completes, app connection behavior is automatic:

- If `models/SmolVLM-256M-Instruct-Agri` exists, the app uses it automatically.
- Otherwise it falls back to `models/SmolVLM-256M-Instruct`.

## Raspberry Pi notes

- Use 64-bit Raspberry Pi OS.
- Keep `LOCAL_MULTIMODAL_MODEL_DIR=/models/SmolVLM-256M-Instruct` in `.env`.
- Keep `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` in `.env`.
- Copy the `models/` folder to the Pi before going offline.

## Project structure

```text
chatbot/
├── app.py
├── chatbot.py
├── config.py
└── requirements.txt

Full_Pipeline_Colab.ipynb
```

## License

[MIT](LICENSE)

## Model attribution

This project uses the SmolVLM base model from Hugging Face TB:

- https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct

Fine-tuning implementation is based on the official Hugging Face reference notebook:

- https://github.com/huggingface/smollm/blob/main/vision/finetuning/Smol_VLM_FT.ipynb

Before redistribution, review the model card terms and license for the base model and any fine-tuned checkpoints.

See also [MODEL_ATTRIBUTION.md](MODEL_ATTRIBUTION.md).
