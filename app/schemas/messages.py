"""Schemas Pydantic para o endpoint de mensagens (Fase 4)."""

from typing import Optional

from pydantic import BaseModel, Field


class SourceMessage(BaseModel):
    """Representa uma fonte citada na resposta."""

    section: str = Field(..., description="Nome da seção da base de conhecimento")


class MessageRequest(BaseModel):
    """Payload de entrada para o endpoint /messages."""

    message: str = Field(..., description="Mensagem ou pergunta do usuário")
    session_id: Optional[str] = Field(
        default=None, description="Identificador opcional da sessão de conversa"
    )


class MessageResponse(BaseModel):
    """Payload de saída do endpoint /messages."""

    answer: str = Field(..., description="Resposta gerada pelo orquestrador")
    sources: list[SourceMessage] = Field(
        default_factory=list,
        description="Lista de fontes utilizadas na resposta",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Identificador da sessão de conversa",
    )

