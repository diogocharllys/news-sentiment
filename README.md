# news-sentiment

Agregador de notícias econômicas brasileiras com análise de sentimento, NER e correlação com ativos financeiros.

## Status

Em desenvolvimento — Fase 1 (Fundação).

## Visão geral

Sistema que coleta notícias de portais econômicos, classifica sentimento (PT-BR) via modelo Transformer, extrai entidades (empresas, ativos) com spaCy, armazena com embeddings e expõe API REST para:

- Busca de artigos com filtros (texto, fonte, data, sentimento, entidade)
- Séries temporais de sentimento por entidade
- Correlação entre sentimento agregado e retorno de ativos
- Alertas sob condições configuráveis

## Stack

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Dados:** PostgreSQL 16 (pgvector, pg_trgm), Redis
- **Workers:** Celery + Celery Beat
- **NLP:** Hugging Face Transformers, spaCy, sentence-transformers
- **Financeiro:** yfinance, pandas, statsmodels
- **Infra:** Docker, GitHub Actions, Fly.io

## Documentos relacionados

- [DECISIONS.md](./DECISIONS.md) — registro de decisões arquiteturais
- [LEARNING.md](./LEARNING.md) — anotações de aprendizado

## Setup

_A ser preenchido após configuração do `pyproject.toml` e do ambiente de desenvolvimento._
