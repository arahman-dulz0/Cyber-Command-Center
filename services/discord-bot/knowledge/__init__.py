"""RAG knowledge-base layer (Phase 5): ingest documents, retrieve, ground /ask."""

from knowledge.embedder import Embedder, embedder
from knowledge.ingest import IngestResult, ingest_document, ingest_file_bytes, is_supported
from knowledge.retriever import RagContext, RetrievedChunk, Retriever, retriever

__all__ = [
    "Embedder", "embedder",
    "IngestResult", "ingest_document", "ingest_file_bytes", "is_supported",
    "RagContext", "RetrievedChunk", "Retriever", "retriever",
]
