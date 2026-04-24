import logging

from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Exceção customizada para erros no cliente LLM."""

    pass


class LLMClient:
    """Cliente assíncrono compatível com OpenAI para integração com LLMs."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key.get_secret_value(),
            base_url=str(settings.llm_base_url),
        )
        self._model = settings.llm_model

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.0,
    ) -> str:
        """
        Envia uma conversa para o LLM e retorna a resposta textual.

        Args:
            system_prompt: Instruções de sistema para o LLM.
            user_message: Mensagem do usuário.
            temperature: Criatividade da resposta (0.0 = determinístico).

        Returns:
            Conteúdo textual da resposta do LLM.

        Raises:
            LLMClientError: Em caso de falha na comunicação com o LLM.
        """
        logger.debug(
            "Chamando LLM (model=%s, temp=%s)", self._model, temperature
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
            )
        except AuthenticationError as exc:
            logger.error("Falha de autenticação no LLM: %s", exc)
            raise LLMClientError(
                "Autenticação falhou com o provedor LLM"
            ) from exc
        except RateLimitError as exc:
            logger.error("Rate limit atingido no LLM: %s", exc)
            raise LLMClientError(
                "Rate limit atingido no provedor LLM"
            ) from exc
        except APIError as exc:
            logger.error("Erro da API do LLM: %s", exc)
            raise LLMClientError(f"Erro na API do LLM: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            logger.warning("LLM retornou resposta vazia")
            raise LLMClientError("Resposta vazia do LLM")

        logger.debug("Resposta recebida do LLM (%d chars)", len(content))
        return content

