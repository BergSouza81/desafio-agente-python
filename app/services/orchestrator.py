from app.core.config import settings
from app.tools.search import KBSearchTool


class OrchestratorService:
    def __init__(self):
        self.search_tool = KBSearchTool()

    def process(self, question: str) -> str:
        context = self.search_tool.search(question)
        # TODO: Integrar com LLM usando settings.llm_provider, settings.llm_model, etc.
        return f"Resposta baseada no contexto: {context}"

