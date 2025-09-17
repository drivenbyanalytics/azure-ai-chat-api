from typing import List

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import IndexingResult

from api.exceptions import SearchIndexingError
from models.models import SearchDocument
from settings import settings


class SearchService:
    """
    Service for interacting with Azure Cognitive Search.

    Attributes:
        client (SearchClient): Client for interacting with the Azure Search index.
    """

    def __init__(self):
        try:
            credential = DefaultAzureCredential()
            self.client = SearchClient(
                endpoint=settings.azure_search_endpoint,
                index_name=settings.azure_search_index,
                credential=credential,
            )
        except Exception as e:
            raise SearchIndexingError(f"Failed to initialize Search client: {str(e)}")

    def upload_chunks(self, docs: List[SearchDocument]) -> List[IndexingResult]:
        """
        Upload a batch of documents (e.g., text chunks with embeddings) to the search index.

        Args:
            docs (List[SearchDocument]): A list of SearchDocument representing documents to upload.
                               Each document should match the index schema.

        Returns:
            List[IndexingResult]: The result of the upload operation for each document.
        """
        try:
            result = self.client.upload_documents(documents=docs)
            return result
        except HttpResponseError as e:
            raise SearchIndexingError(f"Azure Search HTTP error: {e.message}")
        except Exception as e:
            raise SearchIndexingError(f"Failed to upload chunks: {str(e)}")
