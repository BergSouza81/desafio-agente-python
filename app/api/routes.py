from fastapi import APIRouter
from app.schemas.models import QueryRequest, QueryResponse
from app.services.orchestrator import OrchestratorService

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    orchestrator = OrchestratorService()
    answer = orchestrator.process(request.question)
    return QueryResponse(answer=answer)

