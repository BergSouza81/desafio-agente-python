"""Testes unitários para o SessionStore."""

import pytest

from app.services.session_store import SessionStore


class TestSessionStore:
    """Suite de testes do armazenamento de sessões em memória."""

    @pytest.fixture
    def store(self) -> SessionStore:
        return SessionStore(limit=4)

    @pytest.mark.asyncio
    async def test_add_and_get_history(self, store: SessionStore) -> None:
        """Deve adicionar mensagens e recuperar o histórico."""
        await store.add_message("sess-1", "user", "Olá")
        await store.add_message("sess-1", "assistant", "Oi!")

        history = await store.get_history("sess-1")

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Olá"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Oi!"

    @pytest.mark.asyncio
    async def test_history_limit(self, store: SessionStore) -> None:
        """Deve manter apenas as últimas N mensagens."""
        for i in range(6):
            await store.add_message("sess-1", "user", f"msg-{i}")

        history = await store.get_history("sess-1")

        assert len(history) == 4
        assert history[0]["content"] == "msg-2"
        assert history[-1]["content"] == "msg-5"

    @pytest.mark.asyncio
    async def test_get_history_with_limit(self, store: SessionStore) -> None:
        """Deve respeitar o parâmetro limit ao recuperar histórico."""
        await store.add_message("sess-1", "user", "a")
        await store.add_message("sess-1", "assistant", "b")
        await store.add_message("sess-1", "user", "c")

        history = await store.get_history("sess-1", limit=2)

        assert len(history) == 2
        assert history[0]["content"] == "b"
        assert history[1]["content"] == "c"

    @pytest.mark.asyncio
    async def test_get_history_empty_session(self, store: SessionStore) -> None:
        """Deve retornar lista vazia para sessão inexistente."""
        history = await store.get_history("sess-inexistente")
        assert history == []

    @pytest.mark.asyncio
    async def test_get_history_none_session(self, store: SessionStore) -> None:
        """Deve retornar lista vazia quando session_id é None."""
        history = await store.get_history(None)
        assert history == []

    @pytest.mark.asyncio
    async def test_add_message_none_session(self, store: SessionStore) -> None:
        """Deve ignorar mensagens com session_id None."""
        await store.add_message(None, "user", "test")
        # Não deve lançar exceção

    @pytest.mark.asyncio
    async def test_clear_session(self, store: SessionStore) -> None:
        """Deve remover o histórico de uma sessão."""
        await store.add_message("sess-1", "user", "Olá")
        await store.clear("sess-1")

        history = await store.get_history("sess-1")
        assert history == []

    @pytest.mark.asyncio
    async def test_isolation_between_sessions(self, store: SessionStore) -> None:
        """Sessões devem ser independentes."""
        await store.add_message("sess-a", "user", "A")
        await store.add_message("sess-b", "user", "B")

        history_a = await store.get_history("sess-a")
        history_b = await store.get_history("sess-b")

        assert len(history_a) == 1
        assert len(history_b) == 1
        assert history_a[0]["content"] == "A"
        assert history_b[0]["content"] == "B"

