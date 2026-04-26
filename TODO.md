# TODO - Correções para o Desafio Técnico

## Status: ✅ CONCLUÍDO

## Passos
- [x] 1. Analisar gaps vs requisitos do desafio
- [x] 2. Atualizar requirements.txt (pytest, pytest-asyncio)
- [x] 3. Atualizar app/core/config.py (defaults, KB_URL oficial)
- [x] 4. Atualizar app/schemas/messages.py (adicionar session_id ao MessageResponse)
- [x] 5. Atualizar app/api/v1/endpoints.py (retornar session_id na resposta)
- [x] 6. Atualizar app/main.py (expor POST /messages sem prefixo)
- [x] 7. Atualizar app/services/session_store.py (TTL/expire)
- [x] 8. Criar .env.example
- [x] 9. Criar Makefile
- [x] 10. Criar DECISION_RULES.md
- [x] 11. Atualizar tests/test_api.py (paths /messages)
- [x] 12. Instalar dependências de teste
- [x] 13. Rodar testes
- [x] 14. Testar no localhost

## Resultados
- **47/47 testes passando** ✅
- **Endpoint `/messages` exposto sem prefixo** `/api/v1` ✅
- **Session ID gerado automaticamente** (UUID v4) ✅
- **TTL implementado no SessionStore** ✅
- **Configurações com defaults** ✅
- **Documentação criada** (.env.example, Makefile, DECISION_RULES.md) ✅

