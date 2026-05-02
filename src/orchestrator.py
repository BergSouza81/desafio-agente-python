"""
Orquestrador simples do fluxo RAG.

Este é o cérebro do sistema:
1. Recebe a mensagem do usuário
2. Busca o contexto na Knowledge Base (Markdown)
3. Formata o prompt para o LLM
4. Envia para o LLM e retorna a resposta
"""

import re
import uuid
from typing import Optional

from src.tool import fetch_markdown
from src.llm import LLMClient

# URL base de conhecimento (pode vir de variável de ambiente)
DEFAULT_KB_URL = "https://raw.githubusercontent.com/igortce/python-agent-challenge/refs/heads/main/python_agent_knowledge_base.md"


class Orchestrator:
    """
    Orquestrador simples que coordena a busca na KB e a geração de resposta via LLM.
    """

    def __init__(
        self,
        kb_url: str = DEFAULT_KB_URL,
        llm_client: Optional[LLMClient] = None,
    ):
        self.kb_url = kb_url
        self.llm_client = llm_client or LLMClient()
        self._kb_content: Optional[str] = None

    def _get_kb_content(self) -> str:
        """Busca o conteúdo da KB (com cache simples em memória)."""
        if self._kb_content is None:
            self._kb_content = fetch_markdown(self.kb_url) or ""
        return self._kb_content

    def _parse_sections(self, markdown: str) -> list[dict]:
        """Faz o parsing do Markdown extraindo seções por títulos (#)."""
        sections = []
        pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        matches = list(pattern.finditer(markdown))

        for i, match in enumerate(matches):
            title = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            content = markdown[start:end].strip()
            sections.append({"section": title, "content": content})

        return sections

    def _find_relevant_sections(self, query: str, sections: list[dict]) -> list[dict]:
        """Encontra as seções mais relevantes para a query usando keyword matching."""
        query_terms = set(re.findall(r"\b\w+\b", query.lower()))
        if not query_terms:
            return sections[:5]

        scored = []
        for section in sections:
            text = f"{section['section']} {section['content']}".lower()
            section_terms = set(re.findall(r"\b\w+\b", text))
            overlap = len(query_terms & section_terms)
            if overlap > 0:
                scored.append((overlap, section))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:5]]

    def _build_context(self, sections: list[dict]) -> str:
        """Monta o bloco de contexto a partir das seções relevantes."""
        parts = []
        for s in sections:
            title = s.get("section", "(sem título)")
            content = s.get("content", "") or "(sem conteúdo)"
            parts.append(f"## {title}\n{content}")
        return "\n\n".join(parts)

    def _build_prompt(self, context: str, user_message: str) -> str:
        """Constrói o prompt para o LLM."""
        return f"""Você é um assistente que responde ESTRITAMENTE com base no contexto fornecido abaixo.

REGRAS:
1. NÃO use conhecimento externo ou informações que não estejam no contexto.
2. Responda de forma clara e objetiva.
3. Ao final da resposta, indique a fonte no formato: [Fonte: Nome da Seção]
4. Se a resposta não estiver no contexto, diga que não encontrou.

CONTEXTO:
{context}

Pergunta: {user_message}

Resposta:"""

    async def process(self, message: str, session_id: Optional[str] = None) -> dict:
        """
        Processa a mensagem do usuário através do fluxo RAG.

        Args:
            message: Mensagem ou pergunta do usuário
            session_id: ID da sessão (opcional, gera novo se None)

        Returns:
            Dicionário com 'answer', 'sources' e 'session_id'
        """
        # Gera session_id se não fornecido
        if not session_id:
            session_id = str(uuid.uuid4())

        # 1. Busca conteúdo da KB
        kb_content = self._get_kb_content()
        if not kb_content:
            return {
                "answer": "Não foi possível acessar a base de conhecimento.",
                "sources": [],
                "session_id": session_id,
            }

        # 2. Parse e encontra seções relevantes
        sections = self._parse_sections(kb_content)
        relevant = self._find_relevant_sections(message, sections)

        if not relevant:
            return {
                "answer": "Não encontrei informação suficiente na base para responder essa pergunta.",
                "sources": [],
                "session_id": session_id,
            }

        # 3. Constrói contexto e prompt
        context = self._build_context(relevant)
        prompt = self._build_prompt(context, message)

        # 4. Chama LLM
        try:
            raw_answer = await self.llm_client.chat(
                system_prompt="Você é um assistente útil.",
                user_message=prompt,
                temperature=0.0,
            )
        except Exception as e:
            print(f"Erro ao chamar LLM: {e}")
            return {
                "answer": "Ocorreu um erro ao processar sua pergunta. Tente novamente.",
                "sources": [],
                "session_id": session_id,
            }

        # 5. Extrai fonte da resposta
        answer, sources = self._extract_sources(raw_answer, relevant)

        return {
            "answer": answer,
            "sources": sources,
            "session_id": session_id,
        }

    def _extract_sources(
        self,
        answer: str,
        sections: list[dict],
    ) -> tuple[str, list[dict]]:
        """Extrai a fonte citada na resposta."""
        patterns = [
            re.compile(r"\[Fonte:\s*(.*?)\]", re.IGNORECASE),
            re.compile(r"Fonte:\s*(.+?)(?:\n|$)", re.IGNORECASE),
        ]

        source_name = None
        for pattern in patterns:
            match = pattern.search(answer)
            if match:
                source_name = match.group(1).strip()
                answer = pattern.sub("", answer).strip()
                break

        if source_name:
            return answer, [{"section": source_name}]

        # Fallback: usa a primeira seção relevante
        if sections:
            return answer, [{"section": sections[0]["section"]}]

        return answer, []


if __name__ == "__main__":
    import asyncio

    async def test():
        orch = Orchestrator()
        result = await orch.process("O que é composição?")
        print("Answer:", result["answer"])
        print("Sources:", result["sources"])

    asyncio.run(test())
