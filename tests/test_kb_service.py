"""Testes unitários para o KBService."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.tools.kb_service import (
    KBService,
    KBServiceError,
    KBTimeoutError,
    KBUnavailableError,
    KBNotFoundError,
    Section,
)


class TestSection:
    """Testes do dataclass Section."""

    def test_to_dict(self) -> None:
        section = Section(heading_level=2, title="Título", content="Conteúdo")
        result = section.to_dict()
        assert result == {"section": "Título", "content": "Conteúdo"}


class TestKBServiceParsing:
    """Testes de parsing do Markdown."""

    def test_parse_sections_simple(self) -> None:
        markdown = "# Intro\nTexto intro.\n\n# Instalação\nExecute pip."
        sections = KBService._parse_sections(markdown)
        assert len(sections) == 2
        assert sections[0].title == "Intro"
        assert "Texto intro" in sections[0].content
        assert sections[1].title == "Instalação"

    def test_parse_sections_no_headings(self) -> None:
        markdown = "Apenas texto sem títulos."
        sections = KBService._parse_sections(markdown)
        assert sections == []

    def test_parse_sections_nested_levels(self) -> None:
        markdown = "# H1\nTexto 1\n## H2\nTexto 2\n### H3\nTexto 3"
        sections = KBService._parse_sections(markdown)
        assert len(sections) == 3
        assert sections[0].heading_level == 1
        assert sections[1].heading_level == 2
        assert sections[2].heading_level == 3


class TestKBServiceCache:
    """Testes do mecanismo de cache."""

    def test_cache_valid(self) -> None:
        service = KBService(ttl_seconds=10)
        service._cache_content = "# Test\nConteúdo"
        service._cache_timestamp = time.monotonic()
        assert service._is_cache_valid() is True

    def test_cache_expired(self) -> None:
        service = KBService(ttl_seconds=0)
        service._cache_content = "# Test\nConteúdo"
        service._cache_timestamp = time.monotonic() - 1
        assert service._is_cache_valid() is False


class TestKBServiceSearch:
    """Testes da busca por keywords."""

    @pytest.fixture
    def sample_sections(self) -> list[dict[str, str | int]]:
        return [
            {"section": "Instalação", "content": "Use pip install para instalar."},
            {"section": "API", "content": "Endpoints RESTful documentados."},
            {"section": "Docker", "content": "Construa a imagem com docker build."},
        ]

    @pytest.mark.asyncio
    async def test_search_exact_match(self, sample_sections: list[dict[str, str | int]]) -> None:
        service = KBService()
        with patch.object(service, "get_sections", new=AsyncMock(return_value=sample_sections)):
            result = await service.search("pip install")
            assert len(result) >= 1
            assert result[0]["section"] == "Instalação"

    @pytest.mark.asyncio
    async def test_search_no_results(self, sample_sections: list[dict[str, str | int]]) -> None:
        service = KBService()
        with patch.object(service, "get_sections", new=AsyncMock(return_value=sample_sections)):
            result = await service.search("xyz123nada")
            assert result == []

    @pytest.mark.asyncio
    async def test_search_top_k(self, sample_sections: list[dict[str, str | int]]) -> None:
        service = KBService()
        with patch.object(service, "get_sections", new=AsyncMock(return_value=sample_sections)):
            result = await service.search("docker pip", top_k=1)
            assert len(result) == 1


class TestKBServiceFetch:
    """Testes do fetch HTTP com mocks."""

    @pytest.mark.asyncio
    async def test_fetch_404_raises_not_found(self) -> None:
        service = KBService()
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404",
            request=mock_request,
            response=mock_response,
        )

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(KBNotFoundError):
                await service._fetch_markdown()

    @pytest.mark.asyncio
    async def test_fetch_502_raises_unavailable(self) -> None:
        service = KBService()
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.text = "Bad Gateway"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "502",
            request=mock_request,
            response=mock_response,
        )

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(KBUnavailableError):
                await service._fetch_markdown()

    @pytest.mark.asyncio
    async def test_fetch_timeout_raises_timeout(self) -> None:
        service = KBService()
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(KBTimeoutError):
                await service._fetch_markdown()

    @pytest.mark.asyncio
    async def test_fetch_success(self) -> None:
        service = KBService()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "# Test\nConteúdo"

        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await service._fetch_markdown()
            assert result == "# Test\nConteúdo"

