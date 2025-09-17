import uuid
import datetime
from typing import List
from settings import settings
from services.exceptions import FileNotFoundError
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential


class CosmosService:
    """
    Service for connecting to Azure Cosmos DB and managing file data.

    Attributes:
        client (CosmosClient): Cosmos DB client instance.
        database: Reference to the Cosmos DB database.
        container: Reference to the Cosmos DB container where files are stored.
    """

    def __init__(self):
        credential = DefaultAzureCredential()

        self.client = CosmosClient(
            url=settings.cosmos_db_uri,
            credential=credential
        )
        self.database = self.client.get_database_client(settings.cosmos_db_database)
        self.container = self.database.get_container_client(settings.cosmos_db_container)

    def save_file(self, filename: str) -> str:
        """
        Save a file's metadata and content to Cosmos DB.

        Args:
            filename (str): Name of the file.

        Returns:
            str: The generated unique file_id for the stored file.
        """
        file_id = str(uuid.uuid4())
        item = {
            "id": file_id,
            "filename": filename,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        self.container.upsert_item(item)
        return file_id

    def get_file(self, file_id: str):
        """
        Retrieve a file from Cosmos DB by its unique file_id.

        Args:
            file_id (str): The unique ID of the file to retrieve.

        Returns:
            dict: The file item including 'id', 'filename', 'content', and 'created_at'.
        """
        return self.container.read_item(item=file_id, partition_key=file_id)


    def list_files(self) -> List[dict]:
        """
        Retrieve all files stored in Cosmos DB.

        Returns:
            List[dict]: A list of file items.
        """
        query = "SELECT c.id, c.filename, c.created_at FROM c"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        return items

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
        except Exception as e:
            raise FileNotFoundError(file_id)
