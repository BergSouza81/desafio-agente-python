"""Armazenamento em memória do histórico de sessões (Fase 4)."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_HISTORY_LIMIT = 6  # 3 turnos (pergunta + resposta)


class SessionStore:
    """
    Armazena o histórico curto de mensagens por session_id em memória.

    Thread-safe via asyncio.Lock. Não persiste entre reinicializações.
    """

    def __init__(self, limit: int = DEFAULT_HISTORY_LIMIT) -> None:
        self._sessions: dict[str, list[dict[str, str]]] = {}
        self._limit = limit
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
            history = self._sessions.get(session_id, [])
            if limit:
                return history[-limit:]
            return history.copy()

    async def clear(self, session_id: str) -> None:
        """Remove o histórico de uma sessão específica."""
        async with self._lock:
            self._sessions.pop(session_id, None)

