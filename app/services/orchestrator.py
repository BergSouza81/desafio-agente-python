import logging
from typing import Optional

from app.core.config import settings
from app.tools.kb_service import KBService, KBServiceError

logger = logging.getLogger(__name__)


class OrchestratorService:
    """
    Orquestrador do fluxo RAG.

    Responsável por coordenar a busca na base de conhecimento
    e a geração de resposta via LLM.
    """

    def __init__(self, kb_service: Optional[KBService] = None) -> None:
        self._kb_service = kb_service or KBService()

    async def process(self, question: str) -> str:
        """
        Processa uma pergunta através do pipeline RAG.

        Args:
            question: Pergunta do usuário.

        Returns:
            Resposta gerada pelo sistema.
        """
        logger.info("Processando pergunta: %s", question)

        try:
            sections = await self._kb_service.get_sections()
        except KBServiceError:
            logger.exception("Falha ao recuperar contexto da KB")
            return "Não foi possível recuperar contexto da base de conhecimento."

        if not sections:
            return "Base de conhecimento está vazia ou sem seções identificáveis."

        # TODO: Integrar com LLM usando settings.llm_provider, settings.llm_model, etc.
        # A chave de API deve ser acessada via: settings.llm_api_key.get_secret_value()
        context = "\n\n".join(
            f"### {s['section']}\n{s['content']}" for s in sections
        )
        return f"Resposta baseada no contexto:\n{context}"

