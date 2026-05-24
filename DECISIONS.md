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

## ADR-002 — Separação em camadas (api / domain / infrastructure / workers / cli / core)
**Data:** 2026-05-18
**Status:** Aceita

### Contexto
O projeto cresce em três frentes que mudam por motivos diferentes: a API HTTP, a
ingestão/processamento assíncrono e as regras de negócio (sentimento, entidades,
correlação). Sem uma fronteira explícita, regra de negócio vaza para dentro de rota
FastAPI e de task Celery, e qualquer troca de framework ou de banco vira reescrita.

### Decisão
Organizar o código em camadas com dependências apontando para dentro:
- `api/` — rotas, schemas Pydantic, dependências de request
- `domain/` — entidades, regras de negócio e interfaces (puro, sem framework)
- `infrastructure/` — repositórios SQLAlchemy, clientes HTTP, NLP, finanças
- `workers/` — tasks Celery
- `cli/` — comandos administrativos (typer)
- `core/` — configuração, logging e utilidades transversais

`domain/` não importa de `api/`, `infrastructure/` nem `workers/`; as camadas de
fora dependem do domínio, nunca o contrário.

### Alternativas consideradas
- Estrutura plana / por tipo técnico (`models/`, `routes/`, `services/`) — Pró: menos
  arquivos no começo, padrão comum em tutorial. Contra: regra de negócio se espalha,
  acoplamento ao framework, difícil testar domínio isolado.
- Pacote único sem fronteiras — Pró: zero cerimônia. Contra: não escala com três
  processos (API, workers, beat) e múltiplas fases do roadmap.

### Consequências
- Positivas: domínio testável sem subir banco nem HTTP; trocar detalhe de
  infraestrutura (driver, cliente NLP) não toca regra de negócio; fronteira clara
  entre os três processos.
- Negativas / trade-offs aceitos: mais arquivos e indireção desde cedo; exige
  disciplina para não importar "para o lado errado" (a ser reforçado por revisão,
  e futuramente por checagem automática de imports).

---

## ADR-003 — `domain/` plano por enquanto
**Data:** 2026-05-18
**Status:** Aceita

### Contexto
Dentro de `domain/` é possível agrupar por agregado (`domain/article/`,
`domain/sentiment/`, …) desde o início ou manter os módulos lado a lado. Particionar
cedo, com o domínio ainda pequeno e instável, cria pastas com um arquivo só e força
decisões de fronteira antes de haver informação para tomá-las.

### Decisão
Manter `domain/` plano (módulos no mesmo nível) enquanto o número de entidades for
pequeno. Particionar por agregado apenas quando o crescimento justificar.

### Alternativas consideradas
- Particionar por agregado já no início — Pró: estrutura "pronta para escalar".
  Contra: over-engineering prematuro; refatorar fronteira errada custa mais do que
  começar plano.

### Consequências
- Positivas: menos cerimônia agora; a fronteira entre agregados emerge do uso real.
- Negativas / trade-offs aceitos: haverá uma refatoração de reorganização quando o
  domínio crescer — aceita por ser barata e informada.

---

## ADR-004 — Stack principal (FastAPI + SQLAlchemy 2.0 + Celery + PostgreSQL + Redis)
**Data:** 2026-05-18
**Status:** Aceita

### Contexto
O projeto precisa de: API REST de leitura, ORM com migrations, processamento
assíncrono agendado (scraping a cada 30min, NLP, agregações), banco relacional capaz
de busca textual e similaridade vetorial, e cache/broker. As escolhas precisam ser
maduras, bem documentadas e adequadas a aprendizado.

### Decisão
- **FastAPI** para a API (async nativo, validação via Pydantic, docs automáticas).
- **SQLAlchemy 2.0** (estilo `Mapped`/`mapped_column`) + **Alembic** para ORM e migrations.
- **Pydantic v2** para schemas e settings.
- **Celery + Celery Beat** para tasks assíncronas e agendamento.
- **PostgreSQL 16** com `pgvector` (similaridade) e `pg_trgm` (busca textual).
- **Redis** como cache e broker do Celery.

### Alternativas consideradas
- Django/DRF — Pró: baterias inclusas, admin. Contra: mais opinativo e pesado do que
  o necessário; menos alinhado ao objetivo de entender as peças separadamente.
- Flask — Pró: minimalista. Contra: async e validação exigem montagem manual que o
  FastAPI já entrega.
- Banco vetorial dedicado (Pinecone/Weaviate) — Pró: especializado. Contra: mais um
  serviço para operar; `pgvector` mantém tudo no Postgres nesta escala.
- RQ/Dramatiq no lugar do Celery — Pró: mais simples. Contra: Celery Beat cobre o
  agendamento recorrente sem componente extra.

### Consequências
- Positivas: stack coesa e amplamente documentada; um único banco cobre relacional +
  textual + vetorial; cada peça é substituível graças à separação de camadas (ADR-002).
- Negativas / trade-offs aceitos: Celery + Redis + Postgres elevam a complexidade
  operacional (vários serviços no compose); curva de aprendizado de SQLAlchemy 2.0.

---

## ADR-005 — Modelo de dados inicial (`Source` + `Article`)
**Data:** 2026-05-24
**Status:** Aceita

### Contexto
Primeira migration do projeto. Antes de coletar qualquer notícia é preciso definir
como uma fonte e um artigo são representados, garantindo idempotência no scraping
(rodar duas vezes não duplica) e respeitando o princípio de **não republicar conteúdo
integral**. Três pontos concentram o trade-off: a chave de deduplicação do artigo, a
política de exclusão de fontes e o armazenamento do texto bruto.

### Decisão
Criar `sources` e `articles` com PK inteira surrogate. Usar **`url` como chave natural
única** do artigo. FK `articles.source_id → sources.id` com **`ON DELETE RESTRICT`**.
Armazenar o texto integral em **`raw_text` (nullable)** para uso interno do NLP, sem
nunca expô-lo na API. Timestamps `created_at`/`updated_at` via `TimestampMixin`, todos
`TIMESTAMP WITH TIME ZONE` (princípio UTC). Índices apenas em PK, FK e colunas unique.

### Alternativas consideradas
- **Deduplicação por `url` unique** vs `(source_id, external_id)` — `external_id`
  (id interno do portal/feed) é mais estável a mudanças cosméticas de URL, mas nem
  toda fonte expõe um. `url` está sempre presente; a normalização da URL (remover
  tracking, barra final) fica no scraper, mantendo o banco simples. Escolhido `url`.
- **FK RESTRICT** vs `CASCADE` vs `SET NULL` — `CASCADE` apagaria silenciosamente o
  histórico de artigos ao remover uma fonte (perda de dado que alimenta séries
  temporais); `SET NULL` exigiria `source_id` nullable e deixaria artigos órfãos.
  `RESTRICT` força uma decisão explícita antes de remover uma fonte com artigos.
- **`raw_text` no banco** vs processar-e-descartar — descartar minimizaria
  armazenamento e dúvida sobre republicação, mas impediria reprocessar com um modelo
  NLP novo sem re-scrapear (e o `model_version` pressupõe reprocessamento). Guardar o
  texto **não** é republicar: armazenar para processamento interno é distinto de
  servir o conteúdo. O controle de republicação vive no schema de resposta da API,
  que expõe só título, resumo e link — `raw_text` jamais é serializado.

### Consequências
- Positivas: idempotência garantida pela unique em `url`; histórico de artigos
  protegido contra exclusão acidental de fonte; reprocessamento de NLP possível sem
  re-scrapear; banco inteiro em UTC.
- Negativas / trade-offs aceitos: depender de `url` exige normalização cuidadosa no
  scraper (URLs equivalentes não normalizadas viram duplicatas); `RESTRICT` obriga
  limpar/realocar artigos antes de remover uma fonte; `raw_text` cresce o banco e
  impõe a disciplina permanente de nunca expô-lo via API.
