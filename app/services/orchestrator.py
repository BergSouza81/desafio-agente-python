import logging

from app.core.config import settings
from app.tools.search import KBSearchTool

logger = logging.getLogger(__name__)


class OrchestratorService:
    """
    Orquestrador do fluxo RAG.

    Responsável por coordenar a busca na base de conhecimento
    e a geração de resposta via LLM.
    """

    def __init__(self, search_tool: KBSearchTool | None = None) -> None:
        self.search_tool = search_tool or KBSearchTool()

    def process(self, question: str) -> str:
        """
        Processa uma pergunta através do pipeline RAG.

        Args:
            question: Pergunta do usuário.

        Returns:
            Resposta gerada pelo sistema.
        """
        logger.info("Processando pergunta: %s", question)

        context = self.search_tool.search(question)

        if context is None:
            return "Não foi possível recuperar contexto da base de conhecimento."

        # TODO: Integrar com LLM usando settings.llm_provider, settings.llm_model, etc.
        # A chave de API deve ser acessada via: settings.llm_api_key.get_secret_value()
        return f"Resposta baseada no contexto: {context}"

