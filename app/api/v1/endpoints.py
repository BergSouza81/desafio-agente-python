"""Endpoints da API v1 (Fase 4)."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.messages import (
    MessageRequest,
    MessageResponse,
    SourceMessage,
)
from app.services.orchestrator import OrchestratorService
from app.services.session_store import SessionStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["Messages"])

# Instância singleton do SessionStore (em memória)
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Dependency injection para o armazenamento de sessões."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store


def get_orchestrator() -> OrchestratorService:
    """Dependency injection para o serviço orquestrador."""
    return OrchestratorService()


@router.post("", response_model=MessageResponse)
async def create_message(
    request: MessageRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
    session_store: SessionStore = Depends(get_session_store),
) -> MessageResponse:
    """
    Recebe uma mensagem do usuário, processa via orquestrador RAG
    e retorna a resposta com fontes.

    Se um session_id for enviado, o histórico curto da conversa
    é mantido em memória para fornecer contexto adicional ao LLM.
    """
    try:
        # 1. Recuperar histórico da sessão, se houver session_id
        history: list[dict[str, str]] = []
        if request.session_id:
            history = await session_store.get_history(request.session_id)

        # 2. Processar a mensagem pelo orquestrador
        result = await orchestrator.process(
            message=request.message,
            session_id=request.session_id,
            history=history,
        )

        # 3. Registrar a interação no histórico da sessão
        if request.session_id:
            await session_store.add_message(
                session_id=request.session_id,
                role="user",
                content=request.message,
            )
            await session_store.add_message(
                session_id=request.session_id,
                role="assistant",
                content=result["answer"],
            )

        # 4. Montar resposta no formato contratado
        sources = [SourceMessage(**s) for s in result.get("sources", [])]
        return MessageResponse(
            answer=result["answer"],
            sources=sources,
        )

    except Exception as exc:
        logger.exception("Erro interno ao processar mensagem: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro interno ao processar sua mensagem. "
                   "Por favor, tente novamente mais tarde.",
        ) from exc

