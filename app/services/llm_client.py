import asyncio
import logging
from typing import Optional

from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError, APITimeoutError

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Exceção base para erros no cliente LLM."""

    pass


class LLMTimeoutError(LLMClientError):
    """Timeout na comunicação com o LLM."""

    pass


class LLMRateLimitError(LLMClientError):
    """Rate limit atingido no provedor LLM."""

    pass


class LLMClient:
    """Cliente assíncrono compatível com OpenAI para integração com LLMs."""

    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key.get_secret_value(),
            base_url=str(settings.llm_base_url),
        )
        self._model = settings.llm_model
        self._timeout = timeout
        self._max_retries = max_retries

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
            LLMTimeoutError: Em caso de timeout.
            LLMRateLimitError: Em caso de rate limit.
            LLMClientError: Em caso de falha na comunicação com o LLM.
        """
        logger.debug(
            "Chamando LLM (model=%s, temp=%s)", self._model, temperature
        )

        last_exception: Optional[Exception] = None
        for attempt in range(1, self._max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(
                        model=self._model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        temperature=temperature,
                    ),
                    timeout=self._timeout,
                )
            except asyncio.TimeoutError as exc:
                logger.warning("Timeout na chamada LLM (tentativa %d/%d)", attempt, self._max_retries)
                last_exception = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(2 ** attempt)  # backoff exponencial
                    continue
                raise LLMTimeoutError("O serviço está lento. Tente novamente.") from exc
            except RateLimitError as exc:
                logger.error("Rate limit atingido no LLM: %s", exc)
                raise LLMRateLimitError("Muitas requisições. Aguarde um momento.") from exc
            except AuthenticationError as exc:
                logger.error("Falha de autenticação no LLM: %s", exc)
                raise LLMClientError("Autenticação falhou com o provedor LLM") from exc
            except APITimeoutError as exc:
                logger.warning("APITimeoutError na chamada LLM (tentativa %d/%d): %s", attempt, self._max_retries, exc)
                last_exception = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise LLMTimeoutError("O serviço está lento. Tente novamente.") from exc
            except APIError as exc:
                logger.error("Erro da API do LLM: %s", exc)
                # Se for erro transitório (5xx), tenta novamente
                if attempt < self._max_retries and getattr(exc, 'status_code', None) and 500 <= exc.status_code < 600:
                    logger.warning("Erro transitório no LLM (tentativa %d/%d)", attempt, self._max_retries)
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise LLMClientError(f"Erro na API do LLM: {exc}") from exc
            else:
                break

        content = response.choices[0].message.content
        if not content:
            logger.warning("LLM retornou resposta vazia")
            raise LLMClientError("Resposta vazia do LLM")

        logger.debug("Resposta recebida do LLM (%d chars)", len(content))
        return content

