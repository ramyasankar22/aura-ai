"""
journal_rag.py
──────────────
Adds RAG (Retrieval-Augmented Generation) on top of journal entries.

Flow:
  1. User writes a journal entry in the sidebar.
  2. We save it to your existing DB (via save_journal_fn, unchanged).
  3. We ALSO render it as a PDF on disk: journals/<username>/<title>.pdf
  4. We chunk + embed that text and add it to a per-user FAISS index
     stored at journals/<username>/index/
  5. When the user sends a chat message, retrieve_journal_context()
     does a similarity search over that user's index and returns the
     most relevant past journal snippets, which app.py injects into
     the prompt sent to your existing `chat()` function.

Dependencies (install once):
    pip install langchain langchain-community faiss-cpu sentence-transformers reportlab

Notes:
  - Embeddings: HuggingFaceEmbeddings (all-MiniLM-L6-v2) — local, free, no API key.
  - Vector store: FAISS, persisted to disk per user, loaded/saved on demand.
  - If a user has no journals yet, retrieve_journal_context() returns "" safely.
"""

import os
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import Optional

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
JOURNAL_ROOT = Path("journals")
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 3  # how many journal chunks to retrieve per chat message

# Embedding model is loaded once and reused (it's the slow part)
_embeddings = None


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    return _embeddings


def _user_dir(username: str) -> Path:
    safe_user = "".join(c for c in username if c.isalnum() or c in ("-", "_")) or "user"
    d = JOURNAL_ROOT / safe_user
    d.mkdir(parents=True, exist_ok=True)
    (d / "index").mkdir(parents=True, exist_ok=True)
    return d


def _index_dir(username: str) -> Path:
    return _user_dir(username) / "index"


# ──────────────────────────────────────────────
# PDF GENERATION
# ──────────────────────────────────────────────
def _write_journal_pdf(username: str, title: str, content: str) -> Path:
    """Renders a journal entry as a simple PDF and returns its path."""
    safe_title = "".join(c for c in title if c.isalnum() or c in ("-", "_", " ")).strip()
    pdf_path = _user_dir(username) / f"{safe_title}.pdf"

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=LETTER,
                             leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                             topMargin=0.9 * inch, bottomMargin=0.9 * inch)

    story = [
        Paragraph(f"<b>{title}</b>", styles["Title"]),
        Spacer(1, 0.25 * inch),
    ]
    # Preserve paragraph breaks
    for para in content.split("\n"):
        if para.strip():
            story.append(Paragraph(para.replace("&", "&amp;").replace("<", "&lt;"), styles["BodyText"]))
            story.append(Spacer(1, 0.12 * inch))

    doc.build(story)
    return pdf_path


# ──────────────────────────────────────────────
# INDEXING
# ──────────────────────────────────────────────
def _load_user_index(username: str) -> Optional[FAISS]:
    idx_dir = _index_dir(username)
    if not any(idx_dir.iterdir()):
        return None
    try:
        return FAISS.load_local(
            str(idx_dir), _get_embeddings(), allow_dangerous_deserialization=True
        )
    except Exception:
        return None


def _add_to_index(username: str, title: str, content: str) -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(content)
    if not chunks:
        return

    docs = [
        Document(page_content=chunk, metadata={"title": title, "username": username})
        for chunk in chunks
    ]

    idx_dir = _index_dir(username)
    existing = _load_user_index(username)

    if existing is None:
        store = FAISS.from_documents(docs, _get_embeddings())
    else:
        existing.add_documents(docs)
        store = existing

    store.save_local(str(idx_dir))


# ──────────────────────────────────────────────
# PUBLIC API
# ──────────────────────────────────────────────
def save_journal_with_rag(username: str, title: str, content: str, save_journal_fn) -> Path:
    """
    Saves the journal entry through your existing DB function (unchanged),
    renders it to PDF, and indexes it for retrieval.

    save_journal_fn: pass in your existing `save_journal` from database.py
                      so this stays a drop-in addition, not a replacement.
    Returns the path to the generated PDF.
    """
    # 1. Keep your existing DB save behavior exactly as-is
    save_journal_fn(username, title, content)

    # 2. Render PDF copy
    pdf_path = _write_journal_pdf(username, title, content)

    # 3. Embed + index for RAG retrieval
    try:
        _add_to_index(username, title, content)
    except Exception as e:
        # Indexing failure shouldn't block the journal save itself
        print(f"[journal_rag] Indexing failed for {username}: {e}")

    return pdf_path


def retrieve_journal_context(username: str, query: str, k: int = TOP_K) -> str:
    """
    Returns a formatted string of the most relevant past journal snippets
    for this user, given the current chat message. Returns "" if the user
    has no indexed journals yet or retrieval fails.
    """
    try:
        store = _load_user_index(username)
        if store is None:
            return ""

        results = store.similarity_search(query, k=k)
        if not results:
            return ""

        snippets = []
        for doc in results:
            title = doc.metadata.get("title", "Journal entry")
            snippets.append(f"- ({title}) {doc.page_content.strip()}")

        return "\n".join(snippets)
    except Exception as e:
        print(f"[journal_rag] Retrieval failed for {username}: {e}")
        return ""