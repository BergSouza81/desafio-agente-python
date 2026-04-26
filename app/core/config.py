from pydantic import SecretStr, HttpUrl, Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignora variáveis não mapeadas
    )

    environment: str = Field(default="development", description="Ambiente de execução (development/production)")
    llm_provider: str = Field(default="openai", description="Provedor do LLM")
    llm_model: str = Field(default="gpt-4o-mini", description="Modelo do LLM")
    llm_api_key: SecretStr = Field(default="", description="Chave de API do LLM")
    llm_base_url: HttpUrl = Field(default="https://api.openai.com/v1", description="URL base da API do LLM")
    kb_url: HttpUrl = Field(default="https://raw.githubusercontent.com/igortce/python-agent-challenge/refs/heads/main/python_agent_knowledge_base.md", description="URL da base de conhecimento")
    kb_ttl_seconds: int = Field(default=300, description="Cache TTL da KB em segundos")
    kb_allow_private_ips: bool = Field(default=True, description="Permite IPs privados na KB")
    session_max_messages: int = Field(default=20, description="Máximo de mensagens por sessão")
    session_ttl_hours: int = Field(default=1, description="Tempo de vida da sessão em horas")
    llm_timeout_seconds: float = Field(default=30.0, description="Timeout do LLM em segundos")


settings = Settings()

