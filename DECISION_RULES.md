# Regras de Decisão Arquitetural

Este documento registra as decisões técnicas fundamentais do projeto Python Agent Challenge, com justificativas e trade-offs.

## 1. RAG com Busca por Relevância (não KB inteira)

**Decisão:** Buscar apenas as top-k seções relevantes da KB em vez de enviar todo o conteúdo no prompt.

**Justificativa:**
- Reduz custo de tokens em 95%+
- Melhora precisão (menos ruído no contexto)
- Respeita janela de contexto do LLM
- Escalabilidade: funciona com KBs de qualquer tamanho

**Trade-off:** Busca por palavras-chave é menos precisa que embeddings semânticos, mas elimina dependências externas.

## 2. Session Store em Memória (sem Redis externo)

**Decisão:** Armazenar histórico de conversas em memória com TTL automático.

**Justificativa:**
- Simplicidade para desafio técnico
- Zero dependências de infraestrutura
- Interface async permite troca futura por Redis/banco

**Trade-off:** Dados perdidos entre reinicializações. Em produção, migrar para Redis.

## 3. Sanitização contra Prompt Injection

**Decisão:** Implementar 8 padrões de regex para detectar e remover tentativas de prompt injection.

**Justificativa:**
- Proteção básica sem custo de LLM adicional
- Wrap de segurança no system prompt como segunda camada

**Trade-off:** Não é infalível. Em produção, adicionar classificador dedicado (Rebuff, LLM Guardrails).

## 4. Cache da KB com TTL

**Decisão:** Cachear conteúdo da KB em memória com TTL configurável.

**Justificativa:**
- Evita re-download a cada requisição
- time.monotonic() imune a ajustes de relógio (NTP)

**Trade-off:** Memória consumida proporcional ao tamanho da KB.

## 5. Timeouts Separados (connect vs read)

**Decisão:** Timeouts distintos para conexão (5s) e leitura (25s).

**Justificativa:**
- Evita que servidor lento consuma conexões indefinidamente
- Diferencia problemas de rede vs processamento lento

## 6. Extração de Fontes com Fallback

**Decisão:** Múltiplos padrões de regex + fallback por overlap semântico (50%+).

**Justificativa:**
- LLMs não seguem instruções de formato 100% do tempo
- Fallback garante rastreabilidade mesmo com formato inesperado

## 7. Temperature = 0.0

**Decisão:** Respostas determinísticas para RAG factual.

**Justificativa:**
- RAG exige precisão, não criatividade
- Reduz alucinações e variações entre chamadas

## 8. Estrutura de Pastas por Domínio

**Decisão:** Organização em camadas: api/, services/, tools/, core/, schemas/.

**Justificativa:**
- Separação de responsabilidades clara
- Facilita testes unitários por camada
- Alinhado com padrões FastAPI

## Próximos Passos (Produção)

| Melhoria | Justificativa | Complexidade |
|----------|---------------|--------------|
| Embeddings semânticos | Busca mais precisa que palavras-chave | Média |
| Redis para sessões | Persistência entre reinícios | Baixa |
| Rate limiting por IP | Evita abuso | Baixa |
| Classificador de prompt injection | Proteção robusta | Média |
| Observabilidade (OpenTelemetry) | Tracing distribuído | Alta |
| Streaming de respostas | UX melhor para LLMs lentos | Média |

