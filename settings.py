from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_deployment: str
    azure_openai_model: str
    azure_openai_api_version: str

    # Cosmos DB
    cosmos_db_uri: str
    cosmos_db_database: str
    cosmos_db_container: str

    # Azure Search
    azure_search_endpoint: str
    azure_search_index: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Global settings instance
settings = Settings()
