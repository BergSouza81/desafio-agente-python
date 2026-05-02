# Python Agent Challenge - RAG Orchestrator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)

API em Python que implementa um pipeline RAG (Retrieval-Augmented Generation) para responder perguntas com base em documentação em Markdown. O foco é escalabilidade, segurança e decisões técnicas conscientes.

---

## 🚀 Visão Geral

Este sistema implementa um agente conversacional otimizado para cenários de suporte técnico ou base de conhecimento, com:
- **RAG Verdadeiro:** Busca por relevância (Top-K) em vez de enviar a KB inteira.
- **Histórico:** Suporte a sessões (memória de curto prazo).
- **Rastreabilidade:** Extração de fontes citadas.
- **Segurança:** Proteção contra SSRF e sanitização de prompts.

## 🏗️ Arquitetura

```mermaid
graph TD
    User((Cliente/API)) --> Orchestrator[Orchestrator Service]
    Orchestrator --> SessionStore[(Session Store)]
    Orchestrator --> KBService[KB Service]
    
    subgraph "Pipeline RAG"
    KBService --> Parser[Markdown Parser]
    KBService --> Search[Busca por Relevância]
    end
    
    Orchestrator --> LLMClient[LLM Client]
    LLMClient --> RateLimiter[Rate Limiter]
