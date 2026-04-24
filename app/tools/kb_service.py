import logging
import re
import time
from dataclasses import dataclass
from typing import Optional

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class KBServiceError(Exception):
    """Exceção customizada para erros no serviço de Knowledge Base."""

    pass


@dataclass(frozen=True)
class Section:
    """Representa uma seção do Markdown."""

    heading_level: int
    title: str
    content: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "section": self.title,
            "content": self.content.strip(),
        }


class KBService:
    """
    Serviço de busca e parsing da Knowledge Base em Markdown.

    Implementa cache em memória com TTL para evitar requisições
    desnecessárias e proteger contra rate limits.
    """

    def __init__(
        self,
        ttl_seconds: float = 300.0,
        request_timeout: float = 30.0,
    ) -> None:
        self._ttl = ttl_seconds
        self._request_timeout = request_timeout
        self._cache_content: Optional[str] = None
        self._cache_timestamp: float = 0.0

    def _is_cache_valid(self) -> bool:
        """Verifica se o cache em memória ainda é válido."""
        if self._cache_content is None:
            return False
        return (time.monotonic() - self._cache_timestamp) < self._ttl

    async def _fetch_markdown(self) -> str:
        """
        Busca o conteúdo Markdown da KB_URL.

        Returns:
            Texto Markdown cru da Knowledge Base.

        Raises:
            KBServiceError: Em caso de falha de conexão ou HTTP.
        """
        if self._is_cache_valid():
            logger.debug("Retornando conteúdo da KB do cache em memória")
            return self._cache_content

        kb_url = str(settings.kb_url)
        logger.info("Buscando conteúdo da KB em %s", kb_url)

        try:
            async with httpx.AsyncClient(timeout=self._request_timeout) as client:
                response = await client.get(kb_url)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Erro HTTP %s ao buscar KB: %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise KBServiceError(
                f"Erro HTTP {exc.response.status_code} ao buscar KB"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Erro de conexão ao buscar KB: %s", exc)
            raise KBServiceError(f"Erro de conexão ao buscar KB: {exc}") from exc

        self._cache_content = response.text
        self._cache_timestamp = time.monotonic()
        return self._cache_content

    @staticmethod
    def _parse_sections(markdown: str) -> list[Section]:
        """
        Faz o parsing do Markdown extraindo seções por títulos.

        Args:
            markdown: Texto Markdown completo.

        Returns:
            Lista de seções identificadas.
        """
        sections: list[Section] = []
        matches = list(_HEADING_PATTERN.finditer(markdown))

        if not matches:
            logger.warning("Nenhum título encontrado no Markdown")
            return sections

        for index, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
            content = markdown[start:end]
            sections.append(Section(level, title, content))

        return sections

    async def get_sections(self) -> list[dict[str, str | int]]:
        """
        Retorna todas as seções da KB como dicionários.

        Returns:
            Lista de dicionários no formato {"section": str, "content": str}.
        """
        markdown = await self._fetch_markdown()
        sections = self._parse_sections(markdown)
        return [section.to_dict() for section in sections]

    async def find_section(self, section_name: str) -> Optional[dict[str, str | int]]:
        """
        Busca uma seção específica pelo nome (case-insensitive).

        Args:
            section_name: Nome da seção a ser localizada.

        Returns:
            Dicionário da seção se encontrada, None caso contrário.
        """
        sections = await self.get_sections()
        target = section_name.strip().lower()

        for section in sections:
            if section["section"].lower() == target:
                return section

        logger.warning("Seção '%s' não encontrada na KB", section_name)
        return None

