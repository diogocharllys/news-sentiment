# Architectural Decision Records

Registro de decisões arquiteturais relevantes. Cada decisão segue o formato ADR (Architectural Decision Record).

## Formato

```
## ADR-NNN — Título curto

**Data:** YYYY-MM-DD
**Status:** Proposta | Aceita | Substituída por ADR-XXX | Deprecada

### Contexto
O problema que motivou a decisão.

### Decisão
O que foi decidido, em uma frase.

### Alternativas consideradas
- Alternativa A — prós/contras
- Alternativa B — prós/contras

### Consequências
- Positivas
- Negativas / trade-offs aceitos
```
---

## ADR-001 — Layout src/ em vez de flat
**Data:** 2026-05-18
**Status:** Aceita

### Contexto
Ao iniciar o projeto, era necessário escolher entre layout `src/` e flat para estrutura de pacote Python.

### Decisão
O layout escolhido foi `src/news_sentiment`.

### Alternativas consideradas
- Layout flat (rejeitada): Pró — setup mais simples (sem `pip install -e .`). Contra — testes podem importar do CWD por engano; problemas de packaging só aparecem ao buildar o Docker.

### Consequências
- Positivas: imports de teste não pegam o pacote do CWD por engano; problemas de empacotamento aparecem em dev, não em produção; alinhado com `pyproject.toml` moderno.
- Negativas: setup precisa de `pip install -e .`.

---

<!-- Decisões a registrar (preencher conforme tomadas):

- ADR-002: Separação de camadas (api / domain / infrastructure / workers / cli / core)
- ADR-003: `domain/` plano por enquanto, particionar por agregado quando crescer
- ADR-004: Stack principal (FastAPI + SQLAlchemy 2.0 + Celery + PostgreSQL + Redis)

-->
