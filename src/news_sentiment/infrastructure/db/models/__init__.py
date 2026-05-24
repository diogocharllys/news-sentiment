"""Registra os modelos ORM no ``Base.metadata``.

Por que esse arquivo existe: quando você roda Alembic com
``--autogenerate``, ele compara o estado atual do banco com
``Base.metadata``. Mas o ``Base.metadata`` só "enxerga" um modelo
**depois** que o módulo desse modelo é importado em algum lugar.

Importando aqui, basta que algo (ex.: ``alembic/env.py``) faça
``import news_sentiment.infrastructure.db.models`` para que todos os
modelos fiquem registrados.

Para a primeira migration (manual) isso não é estritamente necessário,
mas é hábito que evita "autogenerate diz que não há mudanças" depois.
"""

from news_sentiment.infrastructure.db.models.article import Article
from news_sentiment.infrastructure.db.models.source import Source

__all__ = ["Article", "Source"]
