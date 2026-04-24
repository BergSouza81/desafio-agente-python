from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.v1.endpoints import router as messages_router

app = FastAPI(
    title="Python Agent Challenge",
    description="API de orquestração de IA com fluxo RAG simples.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Endpoint de verificação de saúde da API."""
    return {"status": "ok"}

