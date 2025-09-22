from api.exceptions import FileProcessingError
from models.models import ProcessFileResult
from services.file_pipeline.cosmos_service import CosmosService
from services.file_pipeline.text_chuncker import TextChunker
from services.file_pipeline.vector_store_service import VectoreStoreService


class FileService:
    """
    Pipeline for ingesting files:
    1. Save file metadata to Cosmos DB.
    2. Split text into chunks and generate embeddings.
    3. Index chunks in Azure Search.
    """

    def __init__(self):
        self.cosmos = CosmosService()
        self.vector = VectoreStoreService()
        self.chunk = TextChunker()

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
            # Split text into chunks
            chunked_data = self.chunk.chunk_text(content)
            # Upload chunks to Azure Search
            self.vector.upload_chunks(chunked_data, file_id)

            return {"file_id": file_id, "chunks_indexed": len(chunked_data)}
        except Exception as e:
            raise FileProcessingError(f"Failed to process file {filename}: {str(e)}")
        
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file and its associated chunks from both Cosmos DB and Azure Search.

        Args:
            file_id (str): The ID of the file to delete.
        Returns:
            bool: True if deletion was successful, False otherwise. 
        """
        if not file_id:
            raise FileProcessingError("file_id cannot be empty")

        try:
            # Delete chunks from Azure Search
            self.vector.delete_chunks_by_document_id(file_id)
            # Delete file metadata from Cosmos DB
            self.cosmos.delete_file(file_id)
            return True
        except Exception as e:
            raise FileProcessingError(f"Failed to delete file {file_id}: {str(e)}")
