# Offline Plant Health Advisor 🌿

An offline AI-powered chatbot for urban farmers that runs entirely on your PC (or Raspberry Pi 5). Upload photos of your plants and farming documents to get smart, real-time crop health insights — **no internet required**.

---

## Features

- 🌱 **Offline-first** — powered by [Ollama](https://ollama.com/) with free, locally-run LLMs
- 📷 **Image analysis** — upload plant photos for disease/pest identification using a vision model
- 📄 **Document chat** — upload PDFs, text files, or notes; the chatbot uses RAG to answer from them
- 🧑‍🌾 **Agriculture-tuned prompts** — system prompt fine-tuned for plant health, crop care, and urban farming
- 🖥️ **Web UI** — clean browser-based interface via [Gradio](https://gradio.app/)
- 🔌 **No cloud, no API keys** — fully local and private

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM runtime | [Ollama](https://ollama.com/) |
| Text model | `llama3.2` (default, swappable) |
| Vision model | `llava` (for image uploads) |
| Document RAG | [LangChain](https://python.langchain.com/) + [ChromaDB](https://www.trychroma.com/) |
| Web UI | [Gradio](https://gradio.app/) |
| Language | Python 3.10+ |

---

## Prerequisites

1. **Python 3.10+** — [python.org](https://www.python.org/downloads/)
2. **Ollama** — [Install Ollama](https://ollama.com/download) for your OS (Windows/macOS/Linux)

After installing Ollama, pull the required models:

```bash
# Text model (used for document chat and text-only questions)
ollama pull llama3.2

# Vision model (used when you upload a plant photo)
ollama pull llava
```

> **Note:** `llama3.2` is ~2 GB and `llava` is ~4 GB. Both are free and run entirely offline after the initial download.

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/Dharun235/-Offline-Plant-Health-Advisor-for-New-Age-Urban-Farmers.git
cd -Offline-Plant-Health-Advisor-for-New-Age-Urban-Farmers

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r chatbot/requirements.txt

# 4. Start the chatbot
python chatbot/app.py
```

Open your browser at **http://localhost:7860** to start chatting.

---

## Usage

### Text Chat
Type any farming or plant health question in the chat box and press **Send**.

### Image Upload (Plant Diagnosis)
1. Click the **🖼 Upload Image** button in the UI.
2. Select a photo of your plant (JPG, PNG, WEBP).
3. Optionally add a text question like *"What's wrong with this leaf?"*.
4. Press **Send** — the vision model will analyse the image offline.

### Document Upload (RAG)
1. Click the **📄 Upload Documents** button.
2. Upload one or more PDF / TXT / Markdown files (e.g. farming guides, crop manuals).
3. The documents are indexed locally; subsequent questions will be answered using their content.
4. Click **Clear Documents** to remove the current document index.

---

## Configuration

Edit `chatbot/config.py` to customise:

| Setting | Default | Description |
|---------|---------|-------------|
| `TEXT_MODEL` | `llama3.2` | Ollama model for text chat |
| `VISION_MODEL` | `llava` | Ollama model for image analysis |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `CHUNK_SIZE` | `800` | RAG document chunk size (tokens) |
| `TOP_K_DOCS` | `4` | Number of document chunks retrieved per query |

---

## Project Structure

```
chatbot/
├── app.py            # Gradio web UI
├── chatbot.py        # LLM interaction logic
├── rag.py            # Document ingestion & retrieval (RAG)
├── config.py         # Models, paths, and prompt configuration
└── requirements.txt  # Python dependencies
```

---

## Fine-Tuning / Customisation

To make the assistant more specialised for your crops:

1. **Improve the system prompt** in `chatbot/config.py` → `SYSTEM_PROMPT`
2. **Upload your own farming documents** via the UI (crop guides, pest manuals, soil reports)
3. **Swap the model** — any Ollama-compatible model works; e.g. `ollama pull mistral` and set `TEXT_MODEL = "mistral"` in `config.py`

---

## Roadmap

- [x] Offline text chat with agriculture-tuned prompt
- [x] Plant image diagnosis via vision model
- [x] Document/PDF upload with RAG
- [ ] Raspberry Pi 5 deployment guide
- [ ] Android companion app (Kotlin)
- [ ] Yocto-based embedded image for Raspberry Pi 5
- [ ] Rust service layer for Pi hardware integration

---

## License

[MIT](LICENSE)