from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str
    llm_model: str
    llm_api_key: str
    llm_base_url: str
    kb_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

