import datetime
import uuid
from typing import Dict, List

from exceptions import FileProcessingError
from models.models import ChunkedEmbedding, ProcessFileResult, SearchDocument
from services.cosmos_service import CosmosService
from services.embedding_service import EmbeddingService
from services.search_service import SearchService


class IngestionPipeline:
    """
    Pipeline for ingesting files:
    1. Save file metadata to Cosmos DB.
    2. Split text into chunks and generate embeddings.
    3. Index chunks in Azure Search.
    """

    def __init__(self):
        self.cosmos = CosmosService()
        self.search = SearchService()
        self.embed = EmbeddingService()

    def _chunk_and_embed_text(self, content: str) -> List[ChunkedEmbedding]:
        """
        Splits text into token-based chunks and generates embeddings.

        Args:
            content (str): The text content to process.

        Returns:
            List[ChunkedEmbedding]: Each dict contains 'chunk_text' and 'vector'.
        """
        try:
            chunks: List[str] = self.embed.chunk_text(content)
            embeddings: List[List[float]] = self.embed.embed_chunks(chunks)
            return [{"chunk_text": c, "vector": v} for c, v in zip(chunks, embeddings)]
        except Exception as e:
            raise FileProcessingError(f"Chunking or embedding failed: {str(e)}")

    def _build_search_documents(
        self, file_id: str, content: str, chunked_data: List[Dict]
    ) -> List[SearchDocument]:
        """
        Build document objects ready to be uploaded to Azure Search.

        Args:
            file_id (str): The Cosmos DB file ID.
            content (str): Original file content.
            chunked_data (list[dict]): List of dicts with 'chunk_text' and 'vector'.

        Returns:
            List[SearchDocument]: Documents formatted for Azure Search indexing.
        """
        docs = []
        char_pointer = 0
        for data in chunked_data:
            chunk = data["chunk_text"]
            vector = data["vector"]

            start = content.find(chunk, char_pointer)
            end = start + len(chunk)
            char_pointer = end

            docs.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "file_id": file_id,
                    "chunk_text": chunk,
                    "start_char": start,
                    "end_char": end,
                    "created_at": datetime.datetime.utcnow().isoformat(),
                    "contentVector": vector,
                }
            )
        return docs

    def process_file(self, filename: str, content: str) -> ProcessFileResult:
        """
        Full processing pipeline for a single file:
        - Save file metadata to Cosmos DB
        - Chunk text and compute embeddings
        - Build document structure for search indexing
        - Upload chunks to Azure Search

        Args:
            filename (str): Name of the file.

        Returns:
            dict: Metadata including file_id and number of chunks indexed.
        """
        if not content:
            raise FileProcessingError("File content is empty")

        try:
            # Save file metadata to Cosmos DB
            file_id: str = self.cosmos.save_file(filename)
            # Split text into chunks and get embeddings
            chunked_data = self._chunk_and_embed_text(content)
            # Build documents for Azure Search
            docs = self._build_search_documents(file_id, content, chunked_data)
            # Upload chunks to Azure Search
            self.search.upload_chunks(docs)

            return {"file_id": file_id, "chunks_indexed": len(docs)}
        except Exception as e:
            raise FileProcessingError(f"Failed to process file {filename}: {str(e)}")
