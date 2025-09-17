import datetime
import uuid
from typing import List

from azure.cosmos import CosmosClient
from azure.cosmos import exceptions as cosmos_exceptions
from azure.identity import DefaultAzureCredential

from api.exceptions import DatabaseError, FileNotFoundError
from models.models import FileMetadata
from settings import settings


class CosmosService:
    """
    Service for connecting to Azure Cosmos DB and managing file data.

    Attributes:
        client (CosmosClient): Cosmos DB client instance.
        database: Reference to the Cosmos DB database.
        container: Reference to the Cosmos DB container where files are stored.
    """

    def __init__(self):
        try:
            credential = DefaultAzureCredential()
            self.client = CosmosClient(
                url=settings.cosmos_db_uri, credential=credential
            )
            self.database = self.client.get_database_client(settings.cosmos_db_database)
            self.container = self.database.get_container_client(
                settings.cosmos_db_container
            )
        except Exception as e:
            raise DatabaseError(f"Failed to initialize Cosmos DB client: {str(e)}")

    def save_file(self, filename: str) -> str:
        """
        Save a file's metadata and content to Cosmos DB.

        Args:
            filename (str): Name of the file.

        Returns:
            str: The generated unique file_id for the stored file.
        """
        try:
            file_id: str = str(uuid.uuid4())
            item = {
                "id": file_id,
                "filename": filename,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

            self.container.upsert_item(item)
            return file_id
        except Exception as e:
            raise DatabaseError(f"Failed to save file {filename}: {str(e)}")

    def get_file(self, file_id: str) -> FileMetadata:
        """
        Retrieve a file from Cosmos DB by its unique file_id.

        Args:
            file_id (str): The unique ID of the file to retrieve.

        Returns:
            FileMetadata: The file item including 'id', 'filename' and 'created_at'.
        """
        try:
            return self.container.read_item(item=file_id, partition_key=file_id)
        except cosmos_exceptions.CosmosResourceNotFoundError:
            raise FileNotFoundError(file_id)
        except Exception as e:
            raise DatabaseError(f"Failed to get file {file_id}: {str(e)}")

    def list_files(self) -> List[FileMetadata]:
        """
        Retrieve all files stored in Cosmos DB.

        Returns:
            List[FileMetadata]: A list of file items.
        """
        try:
            fields = f"c.{FileMetadata.ID}, c.{FileMetadata.FILENAME}, c.{FileMetadata.CREATED_AT}"
            query = f"SELECT {fields} FROM c"
            items = list(
                self.container.query_items(
                    query=query, enable_cross_partition_query=True
                )
            )
            return items
        except Exception as e:
            raise DatabaseError(f"Failed to list files: {str(e)}")

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Cosmos DB by its unique file_id.

        Args:
            file_id (str): The unique ID of the file to delete.

        Returns:
            bool: True if deleted, False otherwise.
        """
        try:
            self.container.delete_item(item=file_id, partition_key=file_id)
            return True
        except cosmos_exceptions.CosmosResourceNotFoundError:
            raise FileNotFoundError(file_id)
        except Exception as e:
            raise DatabaseError(f"Failed to delete file {file_id}: {str(e)}")
