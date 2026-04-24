import logging
import re
from typing import Optional

from app.tools.kb_service import KBService, KBServiceError
from app.services.llm_client import LLMClient, LLMClientError

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = (
    "Não encontrei informação suficiente na base para responder essa pergunta."
)
_SOURCE_TAG_PATTERN = re.compile(r"\[Fonte:\s*(.*?)\]", re.IGNORECASE)


class OrchestratorService:
    """
    Orquestrador do fluxo RAG (Retrieval-Augmented Generation).

    Coordena a busca na base de conhecimento e a geração de respostas
    via LLM, garantindo que apenas o contexto recuperado seja utilizado.
    """

    def __init__(
        self,
        kb_service: Optional[KBService] = None,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self._kb_service = kb_service or KBService()
        self._llm_client = llm_client or LLMClient()

    async def process(
        self, message: str, session_id: Optional[str] = None
    ) -> dict[str, str | list[dict[str, str]]]:
        """
        Processa uma mensagem através do pipeline RAG completo.

        Args:
            message: Pergunta ou mensagem do usuário.
            session_id: Identificador opcional da sessão.

        Returns:
            Dicionário contendo 'answer' e 'sources'.
        """
        logger.info(
            "Processando mensagem (session_id=%s): %s", session_id, message
        )

        # 1. Recuperar contexto da KB
        try:
            sections = await self._kb_service.get_sections()
        except KBServiceError:
            logger.exception("Falha ao recuperar contexto da KB")
            return {"answer": FALLBACK_MESSAGE, "sources": []}

        if not sections:
            logger.warning("Acionando Fallback: KB vazia ou sem seções")
            return {"answer": FALLBACK_MESSAGE, "sources": []}

        logger.info("Contexto encontrado: %d seções", len(sections))

        # 2. Montar prompt e chamar LLM
        context = self._build_context(sections)
        system_prompt = self._build_system_prompt(context)

        try:
            raw_answer = await self._llm_client.chat(
                system_prompt=system_prompt,
                user_message=message,
                temperature=0.0,
            )
        except LLMClientError:
            logger.exception("Erro ao chamar LLM")
            return {"answer": FALLBACK_MESSAGE, "sources": []}

        # 3. Extrair fontes e limpar resposta
        answer, sources = self._extract_sources(raw_answer, sections)

        return {"answer": answer, "sources": sources}

    @staticmethod
    def _build_context(sections: list[dict[str, str | int]]) -> str:
        """Monta o bloco de contexto a partir das seções."""
        return "\n\n".join(
            f"## {s['section']}\n{s['content']}" for s in sections
        )

    @staticmethod
    def _build_system_prompt(context: str) -> str:
        """Constrói o system prompt rigoroso para o LLM."""
        return (
            "Você é um assistente especializado que responde "
            "ESTRITAMENTE com base no contexto fornecido abaixo.\n\n"
            "REGRAS:\n"
            "1. NÃO use conhecimento externo ou informações que não "
            "estejam no contexto.\n"
            "2. Responda de forma clara, objetiva e concisa.\n"
            "3. Ao final da sua resposta, adicione uma linha exatamente "
            "neste formato: [Fonte: Nome da Seção]\n"
            "4. Se a resposta não estiver no contexto, diga: "
            "'Não encontrei essa informação na base de conhecimento.'\n\n"
            f"CONTEXTO:\n{context}"
        )

    @classmethod
    def _extract_sources(
        cls,
        answer: str,
        available_sections: list[dict[str, str | int]],
    ) -> tuple[str, list[dict[str, str]]]:
        """
        Extrai a fonte identificada pelo LLM e valida contra as seções disponíveis.
        """
        match = _SOURCE_TAG_PATTERN.search(answer)
        if not match:
            logger.warning("LLM não identificou fonte na resposta")
            return answer.strip(), []

        source_name = match.group(1).strip()
        clean_answer = _SOURCE_TAG_PATTERN.sub("", answer).strip()

        # Validar se a fonte existe nas seções disponíveis
        valid = any(
            s["section"].lower() == source_name.lower()
            for s in available_sections
        )

        if not valid:
            logger.warning(
                "Fonte '%s' não encontrada nas seções disponíveis", source_name
            )
            return clean_answer, []

        logger.info("Fonte identificada: %s", source_name)
        return clean_answer, [{"section": source_name}]

