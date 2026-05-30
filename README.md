<h1 align="center">News Sentiment</h1>

<p align="center">
  Agregador de notícias econômicas brasileiras com análise de sentimento, NER e correlação com ativos financeiros.
</p>

<p align="center">
  <a href="https://github.com/diogocharllys/news-sentiment/actions/workflows/ci.yml"><img src="https://github.com/diogocharllys/news-sentiment/actions/workflows/ci.yml/badge.svg" alt="CI"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-CA4136?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/pgvector-0064A5?logo=postgresql&logoColor=white" alt="pgvector"/>
  <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white" alt="Celery"/>
  <img src="https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black" alt="Hugging Face"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License"/>
</p>

> 🚧 **Status:** em desenvolvimento — **Fase 2: Coleta de notícias** (scraping idempotente).
> Veja o [Roadmap](#-roadmap) para o estado de cada fase.

---

## 📑 Índice

- [Sobre](#-sobre)
- [Objetivos](#-objetivos)
- [Princípios](#-princípios)
- [Stack](#-stack)
- [Arquitetura](#-arquitetura)
- [Modelo de dados](#-modelo-de-dados)
- [Roadmap](#-roadmap)
- [Como rodar](#-como-rodar)
- [Testes](#-testes)
- [Documentos](#-documentos)
- [O que estou aprendendo](#-o-que-estou-aprendendo)
- [Melhorias futuras](#-melhorias-futuras)

---

## 📋 Sobre

`news-sentiment` é um backend que coleta notícias de portais econômicos brasileiros, classifica o **sentimento** (PT-BR) com um modelo Transformer, extrai **entidades** (empresas, ativos, pessoas) com spaCy, armazena tudo com embeddings em PostgreSQL + `pgvector` e expõe uma **API REST** para análise — incluindo correlação entre sentimento agregado e retorno de ativos financeiros.

O projeto foi desenhado como estudo aprofundado de **arquitetura em camadas**, **processamento assíncrono com Celery**, **NLP em produção** e **engenharia de dados financeiros**. Cada decisão técnica está registrada no [DECISIONS.md](./DECISIONS.md) e o que vou aprendendo no [LEARNING.md](./LEARNING.md).

---

## 🎯 Objetivos

- 📰 Coletar notícias de portais econômicos respeitando `robots.txt` e rate limits
- 🧠 Classificar sentimento em PT-BR com modelo Transformer versionado
- 🏷️ Extrair entidades nomeadas (empresas, ativos, pessoas) com spaCy
- 🔎 Indexar artigos para busca **textual** (`pg_trgm`) e **semântica** (`pgvector`)
- 📈 Buscar cotações via `yfinance` e correlacionar sentimento agregado com retorno
- 🚨 Disparar alertas sob condições configuráveis (sentimento + janela temporal)
- 🛡️ Expor API REST com autenticação JWT e documentação OpenAPI

---

## 🔒 Princípios

Restrições não-negociáveis do projeto, registradas como guarda-corpos contra atalhos:

- **Idempotência no scraping** — rodar duas vezes não duplica nem corrompe
- **Versionamento do modelo NLP** — campo `model_version` em cada classificação
- **Timezone UTC** em todo o banco; conversão só na borda (API/CLI)
- **Migrations Alembic reversíveis** — `downgrade` sempre implementado
- **Secrets via `pydantic-settings` + env vars** — nunca no código
- **Respeito a `robots.txt`** + rate limit polido nos scrapers
- **Não republicar conteúdo integral** — a API só expõe título, resumo curto e link

---

## 🛠️ Stack

| Camada | Tecnologias |
|--------|-------------|
| Runtime / Linguagem | Python 3.12+ |
| Web | FastAPI, Pydantic v2 |
| ORM / Migrations | SQLAlchemy 2.0 (`Mapped`/`mapped_column`), Alembic |
| Banco de dados | PostgreSQL 16 com `pgvector` (similaridade) + `pg_trgm` (busca textual) |
| Cache / Broker | Redis 7 |
| Workers | Celery + Celery Beat |
| NLP | Hugging Face Transformers, spaCy, sentence-transformers |
| Financeiro | yfinance, pandas, statsmodels |
| Scraping | feedparser, httpx, BeautifulSoup |
| Auth | JWT + `passlib` (planejado) |
| Tooling | `uv`, ruff, mypy (strict), pytest, pre-commit |
| Infra | Docker / Docker Compose, GitHub Actions, Fly.io (planejado) |

---

## 🏗️ Arquitetura

Organização em **camadas** (ADR-002), com dependências sempre apontando para dentro: o domínio não conhece nem framework, nem banco, nem HTTP.

```
src/news_sentiment/
├── api/                       # FastAPI: rotas, schemas, dependências (Fase 6)
├── domain/                    # Entidades e regras de negócio puras
├── infrastructure/
│   ├── db/
│   │   ├── base.py            # Declarative Base + naming convention
│   │   ├── mixins.py          # TimestampMixin (created_at/updated_at UTC)
│   │   ├── models/            # Source, Article (SQLAlchemy 2.0)
│   │   ├── repositories/      # Acesso a dados por agregado
│   │   └── session.py         # Engine + session_scope()
│   ├── scrapers/              # Coletores de notícias (Agência Brasil, ...)
│   ├── nlp/                   # Pipeline de sentimento + NER (Fase 4)
│   └── finance/               # Cotações e correlação (Fase 5)
├── workers/                   # Tasks Celery + Beat (Fase 3)
├── cli/                       # Comandos administrativos (typer)
└── core/
    └── config.py              # Settings via pydantic-settings
```

A regra de ouro: **`domain/` não importa nada de `infrastructure/`, `api/` ou `workers/`** — as camadas externas dependem do domínio, nunca o contrário. Detalhes e alternativas em [ADR-002](./DECISIONS.md).

---

## 🗃️ Modelo de dados

Estado atual (Fase 2):

`Source` · `Article`

- **`Source`** — veículo de notícia (ex.: Agência Brasil), identificado por `slug` único.
- **`Article`** — notícia coletada, deduplicada por `url` única. Guarda `raw_text` (texto bruto, **uso interno apenas**) e `summary` (resumo curto, exposto na API).

Decisões: PK inteira surrogate, FK `articles.source_id → sources.id` com `ON DELETE RESTRICT`, timestamps em `TIMESTAMP WITH TIME ZONE`. Justificativas em [ADR-005](./DECISIONS.md).

Entidades futuras: `SentimentAnalysis`, `Entity`, `ArticleEmbedding`, `Asset`, `PriceQuote`, `Alert`.

---

## 🗺️ Roadmap

Desenvolvimento em fatias verticais — cada fase entrega valor mensurável:

| Fase | Tema | Status |
|------|------|:------:|
| 1 | Fundação: pyproject, docker-compose, modelo de dados inicial, CI | ✅ |
| 2 | Coleta de notícias: scraper RSS + persistência idempotente | 🚧 |
| 3 | Workers: Celery + Beat + agendamento e rate limit | ⏳ |
| 4 | NLP: pipeline de sentimento (PT-BR) + NER versionado | ⏳ |
| 5 | Financeiro: cotações via `yfinance` + agregação de sentimento | ⏳ |
| 6 | API REST: endpoints de busca, séries temporais, correlação | ⏳ |
| 7 | Embeddings + busca semântica (`pgvector`) | ⏳ |
| 8 | Auth JWT + rate limit por usuário | ⏳ |
| 9 | Alertas configuráveis e notificações | ⏳ |
| 10 | Observabilidade, deploy (Fly.io) e hardening | ⏳ |

---

## 🚀 Como rodar

### Pré-requisitos
- Python **3.12+**
- [`uv`](https://docs.astral.sh/uv/) (gerenciador de pacotes)
- Docker + Docker Compose

### Passos

1. **Clonar e instalar dependências**
   ```bash
   git clone https://github.com/diogocharllys/news-sentiment.git
   cd news-sentiment
   uv sync
   ```

2. **Configurar variáveis de ambiente**
   ```bash
   cp .env.example .env
   ```
   Os defaults já funcionam para desenvolvimento local.

3. **Subir Postgres + Redis**
   ```bash
   docker compose up -d
   ```

4. **Aplicar migrations**
   ```bash
   uv run alembic upgrade head
   ```

5. **Rodar o scraper (Fase 2)**
   ```bash
   uv run python -m news_sentiment.infrastructure.scrapers.agencia_brasil
   ```

---

## 🧪 Testes

```bash
uv run pytest                # suíte completa
uv run pytest -m "not integration"   # só unitários
uv run ruff check            # lint
uv run ruff format --check   # formatação
uv run mypy                  # type checking (strict)
```

O `pre-commit` (`uv run pre-commit install`) roda lint, format e mypy em cada commit.

---

## 📚 Documentos

- [DECISIONS.md](./DECISIONS.md) — Architectural Decision Records (ADRs)
- [LEARNING.md](./LEARNING.md) — anotações de aprendizado por fase

---

## 💡 O que estou aprendendo

Projeto construído explicitamente para aprofundar:

- **Arquitetura em camadas** com dependências apontando para o domínio
- **SQLAlchemy 2.0** estilo declarativo moderno (`Mapped`/`mapped_column`)
- **Idempotência** via `INSERT ... ON CONFLICT` e chaves naturais
- **Migrations reversíveis** com Alembic
- **NLP em produção:** versionamento de modelo, pipeline reproduzível
- **Processamento assíncrono** com Celery + Beat (não polling)
- **Busca híbrida** (textual + vetorial) num único banco
- **Engenharia de dados financeiros:** janela móvel, correlação, séries temporais
- **Type checking estrito** em Python (mypy strict + plugins)

---

## 🚧 Melhorias futuras

- Suporte a múltiplas fontes (Valor Econômico, InfoMoney, Brazil Journal)
- Cache de cotações e tratamento de feriados de bolsa
- Detecção de eventos (M&A, earnings) por padrões + NER
- Modelo de sentimento específico para finanças (FinBERT em PT)
- Deploy completo (API + worker + Beat) no Fly.io com observabilidade
- Dashboard de visualização (próximo projeto, frontend separado)
