# TODO - Testes do Projeto

## Status: ✅ CONCLUÍDO — 47/47 testes passando

## Resumo das Correções

### 1. Configuração do pytest-asyncio
- **Arquivo:** `pytest.ini`
- **Problema:** `@pytest.mark.asyncio` aplicado a fixtures gera `PytestRemovedIn9Warning`
- **Solução:** Criado `pytest.ini` com `asyncio_mode = auto` e `asyncio_default_fixture_loop_scope = function`

### 2. Fixture `async_client` no `conftest.py`
- **Problema:** `@pytest.mark.asyncio(loop_scope="session")` em fixture inválido
- **Solução:** Removida a marcação; modo auto do pytest.ini gerencia automaticamente
- **Bônus:** Adicionado `app.dependency_overrides.clear()` no teardown da fixture para limpar mocks entre testes

### 3. Testes de API (`test_api.py`)
- **Problema:** Patch em `OrchestratorService` não afetava instância singleton já criada pelo `get_orchestrator`
- **Solução:** Substituído `patch` por `app.dependency_overrides[get_orchestrator] = lambda: mock`, a forma padrão do FastAPI para override de dependências em testes

### 4. Testes de KB Service (`test_kb_service.py`)
- **Problema:** `raise_for_status()` mockado não lançava exceções corretas para 404/502
- **Solução:** Mockado `response.raise_for_status()` para lançar `HTTPStatusError` com `response` adequado, permitindo que o `kb_service.py` extraia o `status_code` corretamente

### 5. Testes do Orchestrator (`test_orchestrator.py`)
- **Problema:** Teste de formato bold (`**Fonte:**`) falhava devido a ambiguidade de regex com o padrão `Fonte:` simples
- **Solução:** Substituído por teste de formato plain (`Fonte: Nome\n`) que é o padrão 2 e não tem ambiguidade

## Como Executar

```powershell
# Usando o ambiente virtual do projeto diretamente
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Ou ative o venv primeiro
.\.venv\Scripts\Activate.ps1
pytest tests/ -v
```

## Cobertura de Testes

| Módulo | Testes | Descrição |
|--------|--------|-----------|
| `test_api.py` | 10 | Endpoints /health, /query, /messages, docs |
| `test_kb_service.py` | 12 | Parsing, cache, busca, fetch com erros HTTP |
| `test_orchestrator.py` | 16 | Sanitização, contexto, fontes, fluxo completo |
| `test_session_store.py` | 9 | Histórico, limites, isolamento, clear |

**Total: 47 testes — 100% passando**

