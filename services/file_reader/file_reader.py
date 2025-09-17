from fastapi import UploadFile

from api.exceptions import FileProcessingError

from .factory import FileParserFactory


class FileReader:
    """
    Reads file content using the appropriate parser provided by FileParserFactory.

    This class abstracts away the logic of selecting a parser based on the file
    extension, and ensures consistent error handling.
    """

    def read_file(self, file: UploadFile) -> str:
        """
        Determines the appropriate parser based on file extension and returns
        the extracted text content.

        Args:
            file (UploadFile): File uploaded via FastAPI

        Returns:
            str: Extracted textual content from the file

        Raises:
            FileProcessingError: If the file type is unsupported or parsing fails
        """
        try:
            parser = FileParserFactory.get_parser(file.filename)
            return parser.parse(file)
        except FileProcessingError:
            # Re-raise parsing errors directly
            raise
        except Exception as e:
            # Wrap unexpected errors in a consistent project-specific exception
            raise FileProcessingError(f"Failed to read file {file.filename}: {str(e)}")
