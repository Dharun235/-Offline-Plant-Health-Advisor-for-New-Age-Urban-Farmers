"""
RAG (Retrieval-Augmented Generation) helpers.

Handles loading, chunking, and indexing uploaded documents (PDF, TXT, MD)
into a local ChromaDB vector store so the chatbot can answer questions
grounded in the user's own farming documents.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    OLLAMA_BASE_URL,
    TEXT_MODEL,
    TOP_K_DOCS,
    UPLOAD_DIR,
    VECTORSTORE_DIR,
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Supported file extensions → loader mapping
# ---------------------------------------------------------------------------
LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
}


def _get_embeddings() -> OllamaEmbeddings:
    """Return an Ollama embeddings instance using the configured text model."""
    return OllamaEmbeddings(model=TEXT_MODEL, base_url=OLLAMA_BASE_URL)


def _load_documents(file_path: str):
    """Load a single document and return a list of LangChain Document objects."""
    ext = Path(file_path).suffix.lower()
    loader_cls = LOADER_MAP.get(ext)
    if loader_cls is None:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {list(LOADER_MAP.keys())}"
        )
    loader = loader_cls(file_path)
    return loader.load()


def ingest_documents(file_paths: List[str]) -> int:
    """
    Load, chunk, and index the given files into the vector store.

    Returns the total number of chunks added.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    all_chunks = []
    for path in file_paths:
        docs = _load_documents(path)
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)

    if not all_chunks:
        return 0

    embeddings = _get_embeddings()
    Chroma.from_documents(
        all_chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR,
    )
    return len(all_chunks)


def get_retriever():
    """
    Return a LangChain retriever backed by the persisted Chroma vector store.
    Returns None if no documents have been indexed yet.
    """
    if not _has_indexed_documents():
        return None

    embeddings = _get_embeddings()
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": TOP_K_DOCS})


def retrieve_context(query: str) -> str:
    """
    Retrieve the most relevant document chunks for *query* and return them
    as a single formatted string ready to be injected into a prompt.
    Returns an empty string when no documents are indexed.
    """
    retriever = get_retriever()
    if retriever is None:
        return ""

    docs = retriever.invoke(query)
    if not docs:
        return ""

    sections = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "uploaded document")
        sections.append(f"[Document {i} — {Path(source).name}]\n{doc.page_content}")

    return "\n\n".join(sections)


def clear_documents() -> None:
    """Delete all indexed documents and the upload cache."""
    if os.path.exists(VECTORSTORE_DIR):
        shutil.rmtree(VECTORSTORE_DIR)
        os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)


def _has_indexed_documents() -> bool:
    """Return True if the vector store directory contains any data."""
    if not os.path.exists(VECTORSTORE_DIR):
        return False
    return any(True for _ in Path(VECTORSTORE_DIR).iterdir())
