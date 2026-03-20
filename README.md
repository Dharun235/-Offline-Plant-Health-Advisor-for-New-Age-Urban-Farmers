# Offline Plant Health Advisor

Plant chatbot with text + image support.

## Run locally (Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r chatbot/requirements.txt
python chatbot/app.py
```

Open:

- http://localhost:7860

## Run with Docker (Raspberry Pi / Linux)

1. Download model once:

```bash
hf download HuggingFaceTB/SmolVLM-256M-Instruct --local-dir ./models/SmolVLM-256M-Instruct
```

2. Create env file:

```bash
cp .env.example .env
```

3. In `.env`, set your login values:

```env
APP_AUTH_ENABLED=1
APP_USERNAME=appuser
APP_PASSWORD=change-me
```

4. Start:

```bash
docker compose up -d --build
```

## Access links

- Same Wi-Fi: http://<pi-ip>:7860

## Hugging Face assets

Use these uploaded repos:

- Model: https://huggingface.co/Dharunkumar9/SmolVLM-256M-Instruct-Agri
- Fine-tuning dataset: https://huggingface.co/datasets/Dharunkumar9/agri-vision-ft-dataset
- RAG corpus dataset: https://huggingface.co/datasets/Dharunkumar9/agri-rag-corpus

Example download commands:

```bash
hf download Dharunkumar9/SmolVLM-256M-Instruct-Agri --repo-type model --local-dir ./models/SmolVLM-256M-Instruct-Agri
hf download Dharunkumar9/agri-rag-corpus --repo-type dataset --local-dir ./data/rag
```

This project is meant for offline deployment. Keep model files locally on the device.
When available, the app prefers `./models/SmolVLM-256M-Instruct-Agri` and falls back to `./models/SmolVLM-256M-Instruct`.

## Files

- [docker-compose.yml](docker-compose.yml)
- [.env.example](.env.example)
- [chatbot/config.py](chatbot/config.py)

## License

[MIT](LICENSE)

## Model attribution

See [MODEL_ATTRIBUTION.md](MODEL_ATTRIBUTION.md).
