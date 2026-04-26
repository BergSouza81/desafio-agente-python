"""Armazenamento em memória do histórico de sessões (Fase 4)."""

import asyncio
import logging
import time
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_HISTORY_LIMIT = 6  # 3 turnos (pergunta + resposta)
DEFAULT_TTL_SECONDS = 3600  # 1 hora


class SessionStore:
    """
    Armazena o histórico curto de mensagens por session_id em memória.

    Thread-safe via asyncio.Lock. Não persiste entre reinicializações.
    Implementa TTL (time-to-live) para expiração automática de sessões inativas.
    """

    def __init__(
        self,
        limit: int = DEFAULT_HISTORY_LIMIT,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        self._sessions: dict[str, list[dict[str, str]]] = {}
        self._last_access: dict[str, float] = {}
        self._limit = limit
        self._ttl_seconds = ttl_seconds or settings.session_ttl_hours * 3600 or DEFAULT_TTL_SECONDS
        self._lock = asyncio.Lock()

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """Adiciona uma mensagem ao histórico da sessão."""
        if not session_id:
            return

        async with self._lock:
            # Limpar sessões expiradas antes de adicionar
            await self._cleanup_expired()

            if session_id not in self._sessions:
                self._sessions[session_id] = []

            self._sessions[session_id].append(
                {"role": role, "content": content}
            )

            # Manter apenas as últimas N mensagens
            if len(self._sessions[session_id]) > self._limit:
                self._sessions[session_id] = self._sessions[session_id][
                    -self._limit :
                ]

            # Atualizar timestamp de acesso
            self._last_access[session_id] = time.monotonic()

            logger.debug(
                "Mensagem adicionada à sessão %s (total: %d)",
                session_id,
                len(self._sessions[session_id]),
            )

    async def get_history(
        self,
        session_id: Optional[str],
        limit: Optional[int] = None,
    ) -> list[dict[str, str]]:
        """Retorna o histórico de mensagens da sessão."""
        if not session_id:
            return []

        async with self._lock:
            # Limpar sessões expiradas antes de retornar
            await self._cleanup_expired()

            history = self._sessions.get(session_id, [])
            if limit:
                return history[-limit:]

            # Atualizar timestamp de acesso
            if session_id in self._sessions:
                self._last_access[session_id] = time.monotonic()

            return history.copy()

    async def clear(self, session_id: str) -> None:
        """Remove o histórico de uma sessão específica."""
        async with self._lock:
            self._sessions.pop(session_id, None)
            self._last_access.pop(session_id, None)

    async def _cleanup_expired(self) -> None:
        """Remove sessões que excederam o TTL."""
        now = time.monotonic()
        expired = [
            sid
            for sid, last_access in self._last_access.items()
            if (now - last_access) > self._ttl_seconds
        ]
        for sid in expired:
            self._sessions.pop(sid, None)
            self._last_access.pop(sid, None)
            logger.debug("Sessão %s expirada e removida", sid)

    async def get_session_ids(self) -> list[str]:
        """Retorna lista de session_ids ativos (não expirados)."""
        async with self._lock:
            await self._cleanup_expired()
            return list(self._sessions.keys())

