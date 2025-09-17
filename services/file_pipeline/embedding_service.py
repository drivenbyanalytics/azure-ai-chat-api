from typing import List

from azure.identity import DefaultAzureCredential
from langchain.text_splitter import TokenTextSplitter
from langchain_openai import AzureOpenAIEmbeddings

from api.exceptions import FileProcessingError
from settings import settings


class EmbeddingService:
    """
    Service for token-based chunking and embedding using Azure OpenAI.

    Attributes:
        splitter (TokenTextSplitter): Splits text into token-based chunks for embeddings.
        embedder (AzureOpenAIEmbeddings): Generates embeddings for text chunks using Azure OpenAI.
    """

    def __init__(self):
        try:
            self.splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)
        except Exception as e:
            raise FileProcessingError(
                f"Failed to initialize TokenTextSplitter: {str(e)}"
            )

        try:
            credential = DefaultAzureCredential()
            self.embedder = AzureOpenAIEmbeddings(
                deployment=settings.azure_openai_deployment,
                model=settings.azure_openai_model,
                azure_endpoint=settings.azure_openai_endpoint,
                openai_api_version=settings.azure_openai_api_version,
                azure_ad_token_provider=lambda: credential.get_token(
                    "https://cognitiveservices.azure.com/.default"
                ).token,
            )
        except Exception as e:
            raise FileProcessingError(
                f"Failed to initialize embedding service: {str(e)}"
            )

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits a given text into smaller token-based chunks.

        Args:
            text (str): The input text to be split into chunks.

        Returns:
            List[str]: A list of text chunks, each with a maximum number of tokens
                       defined by the TokenTextSplitter configuration.
        """
        try:
            return self.splitter.split_text(text)
        except Exception as e:
            raise FileProcessingError(f"Failed to chunk text: {str(e)}")

    def embed_chunks(self, chunks: list[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of text chunks using Azure OpenAI.

        Args:
            chunks (list[str]): A list of text chunks to be converted into embeddings.

        Returns:
            list[list[float]]: A list of embedding vectors, one per input chunk.
        """
        try:
            return self.embedder.embed_documents(chunks)
        except Exception as e:
            raise FileProcessingError(f"Failed to embed chunks: {str(e)}")
