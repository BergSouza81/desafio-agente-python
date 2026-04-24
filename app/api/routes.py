from fastapi import APIRouter, Depends
from app.schemas.models import QueryRequest, QueryResponse
from app.services.orchestrator import OrchestratorService

router = APIRouter(prefix="/query", tags=["Query"])


def get_orchestrator() -> OrchestratorService:
    """Dependency injection para o serviço orquestrador."""
    return OrchestratorService()


@router.post("", response_model=QueryResponse)
def query(
    request: QueryRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> QueryResponse:
    """Recebe uma pergunta e retorna a resposta processada pelo orquestrador RAG."""
    answer = orchestrator.process(request.question)
    return QueryResponse(answer=answer)

