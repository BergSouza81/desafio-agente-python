"""
Cliente simples para chamar o modelo de linguagem (LLM).

Suporta OpenAI, Ollama ou qualquer provedor compatível com a API OpenAI.
"""

import os
from typing import Optional
from openai import AsyncOpenAI


class LLMClient:
    """
    Cliente simples para interagir com LLMs via API OpenAI-compatível.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
    ):
        """
        Inicializa o cliente LLM.

        Args:
            api_key: Chave da API (padrão: variável de ambiente OPENAI_API_KEY)
            base_url: URL base da API (padrão: OpenAI)
            model: Nome do modelo a usar
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url
        self.model = model
        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.0,
    ) -> str:
        """
        Envia uma mensagem para o LLM e retorna a resposta.

        Args:
            system_prompt: Instruções de sistema
            user_message: Mensagem do usuário
            temperature: Criatividade (0 = determinístico)

        Returns:
            Resposta do LLM
        """
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""


if __name__ == "__main__":
    import asyncio

    async def test():
        # Teste simples (precisa de API key)
        client = LLMClient()
        response = await client.chat(
            system_prompt="Você é um assistente útil.",
            user_message="Olá! Como você está?",
        )
        print(f"Resposta: {response}")

    asyncio.run(test())
