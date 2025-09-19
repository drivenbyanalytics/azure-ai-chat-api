from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Key Vault configuration
    key_vault_url: str 
    
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

    # Auth settings
    username: str = ""
    password: str = ""
    secret_key: str = ""
    auth_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def load_secrets_from_key_vault(self):
        """
        Load sensitive credentials from Azure Key Vault using DefaultAzureCredential.
        """
        try:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=self.key_vault_url, credential=credential)

            self.secret_key = client.get_secret("auth-jwt-secret").value
            self.username = client.get_secret("auth-app-username").value
            self.password = client.get_secret("auth-app-password").value

            # Optional: ensure none of the secrets are empty
            if not all([self.secret_key, self.username, self.password]):
                raise RuntimeError("One or more secrets retrieved from Key Vault are empty")

        except Exception as e:
            raise RuntimeError(f"Failed to load secrets from Azure Key Vault: {e}")


# Global settings instance
settings = Settings()
settings.load_secrets_from_key_vault()
