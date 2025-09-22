from typing import List

from langchain.text_splitter import TokenTextSplitter

from api.exceptions import FileProcessingError

class TextChunker:
    """
    A service class for chunking text using LangChain's TokenTextSplitter.
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize the TextChunker with TokenTextSplitter configuration.
        
        Args:
            chunk_size (int): Maximum number of tokens per chunk. Default is 1000.
            chunk_overlap (int): Number of tokens to overlap between chunks. Default is 100.
            encoding_name (str): The encoding to use for tokenization. Default is "cl100k_base".
        """
        # Initialize the TokenTextSplitter
        try:
            self.splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            encoding_name=encoding_name
        )
        except Exception as e:
            raise FileProcessingError(
                f"Failed to initialize TokenTextSplitter: {str(e)}"
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
