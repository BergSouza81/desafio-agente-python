import logging
from typing import Optional

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class KBSearchTool:
    """Ferramenta de busca na base de conhecimento (Knowledge Base)."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def search(self, query: str) -> Optional[str]:
        """
        Executa uma busca na KB e retorna o texto da resposta.

        Args:
            query: Termo de busca.

        Returns:
            Texto da resposta em caso de sucesso, None em caso de erro.
        """
        try:
            response = httpx.get(
                str(settings.kb_url),
                params={"q": query},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as exc:
            logger.error("Erro HTTP na KB: %s - %s", exc.response.status_code, exc.response.text)
            return None
        except httpx.RequestError as exc:
            logger.error("Erro de conexão com a KB: %s", exc)
            return None

