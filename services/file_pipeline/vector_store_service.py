from typing import List, Optional, Tuple
from datetime import datetime
import uuid

from azure.identity import DefaultAzureCredential
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document

from api.exceptions import SearchIndexingError
from services.file_pipeline.vector_store_schema import FIELDS
from settings import settings


class VectoreStoreService:
    """
    Service for interacting with Azure Cognitive Search using LangChain integration.
    
    This service provides high-level operations for document indexing, search, and management
    using only LangChain methods for simplified interaction.

    Attributes:
        vector_store (AzureSearch): LangChain vector store for all operations.
        embeddings: Embedding service for generating vectors.
    """

    def __init__(self):
        """
        Initialize the VectoreStoreService with LangChain Azure Search integration.
        
        Uses DefaultAzureCredential for secure authentication following Azure best practices.
        """
        try:
            # Use managed identity for secure authentication
            credential = DefaultAzureCredential()
            
            # Initialize Azure OpenAI embeddings service
            self.embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=settings.azure_openai_endpoint,
                azure_deployment=settings.azure_openai_embedding_deployment,
                api_version=settings.azure_openai_embedding_api_version,
                azure_ad_token_provider=lambda: credential.get_token("https://cognitiveservices.azure.com/.default").token,
            )
            
            # Initialize LangChain AzureSearch vector store
            self.vector_store = AzureSearch(
                azure_search_endpoint=settings.azure_search_endpoint,
                azure_search_key=None,  # Using managed identity instead
                index_name=settings.azure_search_index,
                embedding_function=self.embeddings.embed_query,
                search_type="similarity",
                semantic_configuration_name="default",
                fields=FIELDS
            )
            
        except Exception as e:
            raise SearchIndexingError(f"Failed to initialize Search client: {str(e)}")

    def upload_chunks(self, chunks: List[str], document_id: str) -> List[str]:
        """
        Upload a batch of text chunks to the search index.

        Args:
            chunks (List[str]): A list of text chunks to upload.
            document_id (str): The document ID that these chunks belong to.

        Returns:
            List[str]: List of document IDs that were uploaded.
        
        Raises:
            SearchIndexingError: If the upload operation fails.
        """
        if not chunks:
            return []
        
        if not document_id:
            raise ValueError("document_id cannot be empty")
        
        try:
            # Convert text chunks to LangChain Document objects
            documents = []
            current_timestamp = datetime.now().isoformat()
            
            for i, chunk_text in enumerate(chunks):
                
                # Create metadata as separate fields instead of using the model
                metadata = {
                    "file_id": document_id,
                    "created_at": current_timestamp
                }
                
                document = Document(
                    page_content=chunk_text,
                    metadata=metadata
                )
                documents.append(document)
            
            # Use LangChain's add_documents method
            doc_ids = self.vector_store.add_documents(documents)
            return doc_ids
            
        except Exception as e:
            raise SearchIndexingError(f"Failed to upload chunks: {str(e)}")

    def delete_chunks_by_document_id(self, document_id: str) -> bool:
        """
        Delete all chunks associated with a specific document ID from the search index.

        Args:
            document_id (str): The document ID whose chunks should be deleted.

        Returns:
            bool: True if deletion was successful, False otherwise.
        
        Raises:
            SearchIndexingError: If the deletion operation fails.
            ValueError: If document_id is empty.
        """
        if not document_id:
            raise ValueError("document_id cannot be empty")
        
        try:
            # Get all documents matching the file_id
            results = self.vector_store.client.search(
                search_text="",
                filter=f"file_id eq '{document_id}'"
            )

            # Collect their IDs (primary key in your index schema)
            doc_ids = [{"id": doc["id"]} for doc in results]

            if not doc_ids:
                return  # Nothing to delete

            # Delete documents from the index
            results = self.vector_store.client.delete_documents(doc_ids)
            return all(result.succeeded for result in results)
            
        except Exception as e:
            raise SearchIndexingError(f"Failed to delete chunks for document {document_id}: {str(e)}")

    def similarity_search(
        self, 
        query: str, 
        k: int = 10, 
        score_threshold: Optional[float] = 0.6,
        filter_expression: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search combining vector and keyword search.

        Args:
            query (str): The search query text.
            k (int): Maximum number of results to return. Defaults to 10.
            score_threshold (Optional[float]): Minimum relevance score threshold.
            filter_expression (Optional[str]): OData filter expression for metadata filtering.
            document_id (Optional[str]): If provided, search only within chunks of this document.

        Returns:
            List[Tuple[Document, float]]: List of (document, relevance_score) tuples.
        
        Raises:
            SearchIndexingError: If the search operation fails.
            ValueError: If query is empty.
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        try:
            # Build filter expression
            filters = []
            
            # Add document-specific filter if provided
            if document_id:
                filters.append(f"file_id eq '{document_id}'")
            
            # Add custom filter expression if provided
            if filter_expression:
                filters.append(filter_expression)
            
            # Combine filters with AND operator
            combined_filter = " and ".join(filters) if filters else None
            
            
            search_kwargs = {
                "k": k,
            }
            
            if combined_filter:
                search_kwargs["filter"] = combined_filter
            
            # Use similarity_search_with_score for relevance scores
            results = self.vector_store.similarity_search_with_score(
                query=query,
                **search_kwargs
            )
            
            # Filter by score threshold if provided
            if score_threshold is not None:
                results = [
                    (doc, score) for doc, score in results 
                    if score >= score_threshold
                ]
            
            return results
            
        except Exception as e:
            raise SearchIndexingError(f"Failed to perform similarity search: {str(e)}")