class FileNotFoundError(Exception):
    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"File with id {file_id} not found")