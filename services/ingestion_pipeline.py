from services.cosmos_service import CosmosService


class IngestionPipeline:
    """
    Pipeline for ingesting files:
    1. Save file metadata to Cosmos DB.
    """
    
    def __init__(self):
        self.cosmos = CosmosService()

    def process_file(self, filename: str, content: str):
        """
        Full processing pipeline for a single file:
        - Save file metadata to Cosmos DB

        Args:
            filename (str): Name of the file.

        Returns:
            dict: Metadata including file_id.
        """
        # Save file metadata to Cosmos DB
        file_id = self.cosmos.save_file(filename)

        return {"file_id": file_id}
