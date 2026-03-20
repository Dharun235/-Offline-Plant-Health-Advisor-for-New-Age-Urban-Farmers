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

3. In `.env`, keep these values (as requested):

```env
APP_AUTH_ENABLED=1
APP_USERNAME=dharun
APP_PASSWORD=dharun
```

4. Start:

```bash
docker compose up -d --build
```

## Access links

- Same Wi-Fi: http://<pi-ip>:7860

## Files

- [docker-compose.yml](docker-compose.yml)
- [.env.example](.env.example)
- [chatbot/config.py](chatbot/config.py)

## License

[MIT](LICENSE)

## Model attribution

See [MODEL_ATTRIBUTION.md](MODEL_ATTRIBUTION.md).
