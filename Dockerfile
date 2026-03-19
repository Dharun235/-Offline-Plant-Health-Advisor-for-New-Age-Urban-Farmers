FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_HOME=/models/cache \
    TRANSFORMERS_CACHE=/models/cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

COPY chatbot/requirements.txt /app/chatbot/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/chatbot/requirements.txt

COPY chatbot /app/chatbot

EXPOSE 7860

CMD ["python", "chatbot/app.py"]
