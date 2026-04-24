from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str
    session_id: str | None = Field(
        default=None, description="Identificador opcional da sessão"
    )


class Source(BaseModel):
    section: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)

