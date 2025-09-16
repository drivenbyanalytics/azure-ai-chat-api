from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Cosmos DB
    cosmos_db_uri: str
    cosmos_db_database: str
    cosmos_db_container: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Global settings instance
settings = Settings()
