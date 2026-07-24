# Phase 5 — RAG Knowledge Base

Makes the AI *uniquely yours*: index your notes, writeups, PDFs, and cert docs,
then `/ask` answers from **your** knowledge with citations.

```
Your PDFs / writeups / notes  →  chunk  →  embed  →  store
                                                        ↓
/ask "How does Kerberoasting work?"  →  retrieve top-k  →  grounded AI answer + sources
```

## Commands

| Command | What it does |
|---------|--------------|
| `/kb-add <file>` | Attach a PDF / Markdown / text file → indexed into your KB. |
| `/kb-list` | List indexed documents (doc + chunk counts). |
| `/kb-search <query>` | Semantic search over your KB (pure retrieval, no AI). |
| `/ask <question>` | Now **RAG-grounded**: if your KB has relevant context, the answer is drawn from it and cites the source documents; otherwise it falls back to general knowledge. |

Plus **bulk ingest**: drop `.pdf` / `.md` / `.txt` files into the mounted
`knowledge/` folder on the server — the KB monitor ingests new ones automatically
(deduped by content hash, bounded per run).

## How it works

1. **Embed** — chunks and questions are embedded with Ollama's `nomic-embed-text`
   (768-dim), local and free.
2. **Store** — chunks + embeddings live in `kb_chunks` as `float8[]`. The
   `postgres:16` image has no `pgvector`, so cosine similarity is computed in
   Python with numpy (trivial at personal-KB scale; no infra change).
3. **Retrieve** — `/ask` embeds the question, ranks all chunks by cosine, and if
   the best match clears `KB_MIN_SIMILARITY` it grounds the answer in the top-k
   chunks and lists the source documents.

## Architecture

```
knowledge/                   ← NEW
├── embedder.py              ← Ollama /api/embeddings (nomic-embed-text)
├── chunker.py               ← paragraph-aware overlapping chunks
├── ingest.py                ← parse (pdf/md/txt) → chunk → embed → store, dedup
└── retriever.py             ← cosine top-k + RAG context builder
cogs/knowledge.py            ← /kb-add, /kb-list, /kb-search
cogs/ai.py                   ← /ask upgraded to RAG-ground when KB is relevant
tasks/kb_monitor.py          ← folder ingest from KNOWLEDGE_DIR (BaseMonitor)
```

## Database

New tables (migration `docs/migrations/005_phase5.sql`, auto-applied):

- `kb_documents` — one row per ingested file (title, type, content hash, chunk count).
- `kb_chunks` — chunk text + 768-dim embedding (`float8[]`), FK to the document.

## Configuration (`.env`)

```
KB_ENABLED=true
EMBED_MODEL=nomic-embed-text     # ollama pull nomic-embed-text
KB_CHUNK_SIZE=800
KB_CHUNK_OVERLAP=120
KB_TOP_K=5
KB_MIN_SIMILARITY=0.35           # below this → /ask uses general knowledge
KNOWLEDGE_DIR=/app/knowledge     # bulk-ingest folder (mounted in docker/bot.yml)
```

## Prerequisites

- Pull the embedding model once: `ollama pull nomic-embed-text`.
- `docker/bot.yml` mounts `../knowledge → /app/knowledge` for bulk ingest.

## Testing checklist

- [ ] `/kb-add` a PDF/markdown → "indexed, N chunks".
- [ ] `/kb-list` shows the document.
- [ ] `/kb-search kerberoasting` returns ranked snippets with similarity %.
- [ ] `/ask` a question covered by your notes → answer cites the source doc
      (footer shows "KB-grounded").
- [ ] `/ask` an unrelated question → answers normally (footer "general").
- [ ] Dropping files in `knowledge/` ingests them within a cycle; re-adding a
      duplicate is skipped.

## Rollback

Additive. `KB_ENABLED=false` disables retrieval (/ask reverts to plain
generation) and the folder monitor. Tables are harmless to leave; drop with
`DROP TABLE IF EXISTS kb_chunks, kb_documents;` if desired.

## Notes / honest scope

- This grounds answers in **your** documents. Live external sources (Microsoft
  docs, MITRE ATT&CK) would be a web-retrieval add-on — a natural Phase 5.5.
- Embedding is CPU-bound (~0.2–0.5 s/chunk here); large PDFs ingest in the
  background via the folder monitor rather than blocking a command.
