"""Fixtures compartilhadas para os testes do projeto."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.llm_client import LLMClient
from app.services.session_store import SessionStore
from app.tools.kb_service import KBService


@pytest.fixture(scope="session")
def event_loop():
    """Fornece um event loop para testes async (pytest-asyncio v0.21+)."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP async para testes de integração da API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_kb_service() -> MagicMock:
    """Mock do KBService para testes unitários do orquestrador."""
    mock = MagicMock(spec=KBService)
    mock.search = AsyncMock(return_value=[])
    mock.get_sections = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Mock do LLMClient para testes unitários do orquestrador."""
    mock = MagicMock(spec=LLMClient)
    mock.chat = AsyncMock(return_value="Resposta mockada.")
    return mock


@pytest.fixture
def session_store() -> SessionStore:
    """Instância limpa de SessionStore."""
    return SessionStore(limit=4)


@pytest.fixture
def sample_kb_sections() -> list[dict[str, str | int]]:
    """Seções de exemplo da KB."""
    return [
        {"section": "Instalação", "content": "Para instalar, execute pip install."},
        {"section": "Configuração", "content": "Edite o arquivo .env com suas credenciais."},
        {"section": "Uso Básico", "content": "Envie uma mensagem para /api/v1/messages."},
    ]

