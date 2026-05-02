"""
API FastAPI simples - O cérebro principal do desafio.

Este é o entrypoint da aplicação:
- Endpoint POST /messages que recebe a pergunta
- Chama o orchestrado
- Retorna a resposta em JSON
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from src.orchestrator import Orchestrator

# Cria a aplicação FastAPI
app = FastAPI(
    title="Python Agent Challenge",
    description="API simples de orquestração RAG para responder perguntas.",
    version="1.0.0",
)

# Endpoint GET para health check
@app.get("/health")
def health_check():
    """Verificação de saúde da API."""
    return {"status": "ok"}


# Schema de entrada (valida o JSON)
class MessageRequest(BaseModel):
    """Payload da requisição."""
    message: str = Field(..., description="Pergunta do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão (opcional)")


# Schema de saída
class SourceMessage(BaseModel):
    """Fonte citada na resposta."""
    section: str = Field(..., description="Nome da seção")


class MessageResponse(BaseModel):
    """Payload da resposta."""
    answer: str = Field(..., description="Resposta gerada")
    sources: list[SourceMessage] = Field(default_factory=list, description="Fontes utilizadas")
    session_id: Optional[str] = Field(None, description="ID da sessão")


# Instância global do orquestrador
orchestrator = Orchestrator()


@app.post("/messages", response_model=MessageResponse)
async def create_message(request: MessageRequest):
    """
    Recebe uma pergunta, processa via orquestrador e retorna a resposta.
    """
    try:
        # Repasse o session_id também!
        result = await orchestrator.process(
            message=request.message,
            session_id=request.session_id
        )

        # Converte fontes para o schema de saída
        sources = [SourceMessage(**s) for s in result.get("sources", [])]

        return MessageResponse(
            answer=result["answer"],
            sources=sources,
            session_id=result.get("session_id"),
        )

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro ao processar sua mensagem. Tente novamente.",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
