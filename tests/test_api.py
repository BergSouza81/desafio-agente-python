"""Testes de integração para os endpoints da API."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.main import app
from app.api.v1.endpoints import get_orchestrator


def _mock_orchestrator(return_value=None, side_effect=None):
    """Helper para criar um mock de OrchestratorService."""
    instance = MagicMock()
    if side_effect is not None:
        instance.process = AsyncMock(side_effect=side_effect)
    else:
        instance.process = AsyncMock(return_value=return_value)
    return instance


class TestHealthEndpoint:
    """Testes do endpoint /health."""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestQueryEndpoint:
    """Testes do endpoint /api/v1/query (legado)."""

    @pytest.mark.asyncio
    async def test_query_success(self, async_client: AsyncClient) -> None:
        with patch("app.api.routes.OrchestratorService") as MockOrch:
            instance = MagicMock()
            instance.process = AsyncMock(
                return_value={"answer": "Resposta.", "sources": [{"section": "Doc"}]}
            )
            MockOrch.return_value = instance

            response = await async_client.post(
                "/api/v1/query", json={"question": "Como usar?"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "Resposta."
            assert len(data["sources"]) == 1
            assert data["sources"][0]["section"] == "Doc"

    @pytest.mark.asyncio
    async def test_query_with_session(self, async_client: AsyncClient) -> None:
        with patch("app.api.routes.OrchestratorService") as MockOrch:
            instance = MagicMock()
            instance.process = AsyncMock(
                return_value={"answer": "OK", "sources": []}
            )
            MockOrch.return_value = instance

            response = await async_client.post(
                "/api/v1/query",
                json={"question": "Q", "session_id": "sess-abc"},
            )

            assert response.status_code == 200
            instance.process.assert_awaited_once_with(
                message="Q", session_id="sess-abc"
            )


class TestMessagesEndpoint:
    """Testes do endpoint /api/v1/messages (Fase 4)."""

    @pytest.mark.asyncio
    async def test_create_message_success(self, async_client: AsyncClient) -> None:
        mock = _mock_orchestrator(
            return_value={
                "answer": "Resposta do assistente.",
                "sources": [{"section": "API Docs"}],
            }
        )
        app.dependency_overrides[get_orchestrator] = lambda: mock
        response = await async_client.post(
            "/api/v1/messages",
            json={"message": "Como funciona?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Resposta do assistente."
        assert len(data["sources"]) == 1
        assert data["sources"][0]["section"] == "API Docs"

    @pytest.mark.asyncio
    async def test_create_message_with_session(self, async_client: AsyncClient) -> None:
        mock = _mock_orchestrator(return_value={"answer": "OK", "sources": []})
        app.dependency_overrides[get_orchestrator] = lambda: mock
        response = await async_client.post(
            "/api/v1/messages",
            json={"message": "Olá", "session_id": "sess-123"},
        )

        assert response.status_code == 200
        mock.process.assert_awaited_once_with(
            message="Olá", session_id="sess-123"
        )

    @pytest.mark.asyncio
    async def test_create_message_empty_body(self, async_client: AsyncClient) -> None:
        response = await async_client.post("/api/v1/messages", json={})
        assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    async def test_create_message_validation_error(self, async_client: AsyncClient) -> None:
        response = await async_client.post(
            "/api/v1/messages",
            json={"message": 123},  # message deve ser string
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_message_internal_error(self, async_client: AsyncClient) -> None:
        mock = _mock_orchestrator(side_effect=RuntimeError("Boom"))
        app.dependency_overrides[get_orchestrator] = lambda: mock
        response = await async_client.post(
            "/api/v1/messages",
            json={"message": "Teste"},
        )

        assert response.status_code == 500
        assert "erro interno" in response.json()["detail"].lower()


class TestAPIDocs:
    """Testes de disponibilidade da documentação OpenAPI."""

    @pytest.mark.asyncio
    async def test_openapi_docs_available(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_redoc_available(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/redoc")
        assert response.status_code == 200

