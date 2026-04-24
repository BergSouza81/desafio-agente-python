import httpx
from app.core.config import settings


class KBSearchTool:
    def search(self, query: str) -> str:
        try:
            response = httpx.get(settings.kb_url, params={"q": query}, timeout=10.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Erro na busca na base de conhecimento: {e}"

