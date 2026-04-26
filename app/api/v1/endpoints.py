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

router = APIRouter(tags=["Messages"])

# Instâncias singleton (em memória)
_session_store: Optional[SessionStore] = None
_orchestrator: Optional[OrchestratorService] = None


def get_session_store() -> SessionStore:
    """Dependency injection para o armazenamento de sessões."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store


def get_orchestrator(
    session_store: SessionStore = Depends(get_session_store),
) -> OrchestratorService:
    """Dependency injection para o serviço orquestrador."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorService(session_store=session_store)
    return _orchestrator


@router.post("/messages", response_model=MessageResponse)
async def create_message(
    request: MessageRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> MessageResponse:
    """
    Recebe uma mensagem do usuário, processa via orquestrador RAG
    e retorna a resposta com fontes.

    O histórico da conversa é mantido automaticamente pelo orquestrador
    quando um session_id é fornecido (ou gerado).
    """
    try:
        result = await orchestrator.process(
            message=request.message,
            session_id=request.session_id,
        )

        sources = [SourceMessage(**s) for s in result.get("sources", [])]
        return MessageResponse(
            answer=result["answer"],
            sources=sources,
            session_id=result.get("session_id"),
        )

    except Exception as exc:
        logger.exception("Erro interno ao processar mensagem: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro interno ao processar sua mensagem. "
                   "Por favor, tente novamente mais tarde.",
        ) from exc

