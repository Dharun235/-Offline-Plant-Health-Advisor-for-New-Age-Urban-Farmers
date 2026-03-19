# Offline Plant Health Advisor

This project is a local chatbot for plant health support. You can chat with text, upload a plant image, and get guidance on common disease or care issues.

It is set up to run offline using a local model folder.

## What it does

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

- `LOCAL_MULTIMODAL_MODEL_DIR` (default: `./models/SmolVLM-256M-Instruct`)
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- `MAX_NEW_TOKENS`
- `TEMPERATURE`
- `MAX_HISTORY_TURNS`

## Docker (macOS + Raspberry Pi)

Files used:

- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [.env.example](.env.example)

### 1) Download model files once

Do this on a machine with internet:

```bash
huggingface-cli download HuggingFaceTB/SmolVLM-256M-Instruct --local-dir ./models/SmolVLM-256M-Instruct
```

### 2) Create env file

```bash
cp .env.example .env
```

### 3) Run with Docker

```bash
docker compose up --build
```

Open http://localhost:7860

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
```

## License

[MIT](LICENSE)
