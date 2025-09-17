from abc import ABC, abstractmethod

import docx
import PyPDF2
from fastapi import UploadFile

from api.exceptions import FileProcessingError


class BaseFileParser(ABC):
    """
    Abstract base class for all file parsers.

    Defines the interface that all concrete file parsers must implement.
    """

    @abstractmethod
    def parse(self, file: UploadFile) -> str:
        """
        Parses the content of the given file and returns it as a string.

        Args:
            file (UploadFile): File uploaded via FastAPI

        Returns:
            str: Text content extracted from the file
        """
        pass


class TxtFileParser(BaseFileParser):
    """Parser for plain text (.txt) files."""

    def parse(self, file: UploadFile) -> str:
        try:
            content = file.file.read().decode("utf-8")
            file.file.seek(0)  # Reset file pointer for potential further use
            return content
        except Exception as e:
            raise FileProcessingError(f"Failed to parse TXT file: {str(e)}")


class DocxFileParser(BaseFileParser):
    """Parser for Microsoft Word (.docx) files."""

    def parse(self, file: UploadFile) -> str:
        try:
            doc = docx.Document(file.file)
            content = "\n".join([p.text for p in doc.paragraphs])
            file.file.seek(0)
            return content
        except Exception as e:
            raise FileProcessingError(f"Failed to parse DOCX file: {str(e)}")


class PdfFileParser(BaseFileParser):
    """Parser for PDF files."""

    def parse(self, file: UploadFile) -> str:
        try:
            reader = PyPDF2.PdfReader(file.file)
            content = "\n".join([page.extract_text() or "" for page in reader.pages])
            file.file.seek(0)
            return content
        except Exception as e:
            raise FileProcessingError(f"Failed to parse PDF file: {str(e)}")
