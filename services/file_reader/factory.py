from api.exceptions import FileProcessingError

from .parsers import BaseFileParser, DocxFileParser, PdfFileParser, TxtFileParser


class FileParserFactory:
    """
    Factory class to select the appropriate parser based on file extension.
    """

    parser_map = {
        ".txt": TxtFileParser,
        ".docx": DocxFileParser,
        ".pdf": PdfFileParser,
    }

    @classmethod
    def get_parser(cls, filename: str) -> BaseFileParser:
        """
        Return an instance of the parser matching the file's extension.

        Args:
            filename (str): Name of the uploaded file

        Returns:
            BaseFileParser: Concrete parser instance
        """
        filename = filename.lower()
        for ext, parser_cls in cls.parser_map.items():
            if filename.endswith(ext):
                return parser_cls()
        raise FileProcessingError(f"Unsupported file type: {filename}")
