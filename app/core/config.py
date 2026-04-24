from pydantic import SecretStr, HttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    environment: str = Field(default="production", description="Ambiente de execução (development/production)")
    llm_provider: str = Field(default="openai", description="Provedor do LLM")
    llm_model: str = Field(default="gpt-4o-mini", description="Modelo do LLM")
    llm_api_key: SecretStr = Field(description="Chave de API do LLM")
    llm_base_url: HttpUrl = Field(description="URL base da API do LLM")
    kb_url: HttpUrl = Field(description="URL da base de conhecimento")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignora variáveis não mapeadas


settings = Settings()

