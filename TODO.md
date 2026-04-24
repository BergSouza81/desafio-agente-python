# TODO Refatoração Orchestrator

- [x] 1. Atualizar `app/core/config.py` (adicionar `environment`)
- [x] 2. Refatorar `app/tools/kb_service.py` (exceções granulares + método `search`)
- [x] 3. Refatorar `app/services/llm_client.py` (timeout, retry, exceções específicas)
- [x] 4. Ajustar `app/services/session_store.py` (renomear `clear_session` → `clear`)
- [x] 5. Refatorar `app/services/orchestrator.py` (RAG real, sanitização, session store, fontes robustas, erros granulares)
- [x] 6. Atualizar `app/api/v1/endpoints.py` (injeção de dependências, delegar ao orquestrador)
- [x] 7. Verificar imports e tipagem
- [x] 8. Ajustes pós-feedback: LoggerAdapter, _build_context robusto, consolidação de excepts Timeout, comentários de escalabilidade e design async

