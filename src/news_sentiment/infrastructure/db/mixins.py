"""Mixins reutilizáveis para modelos ORM.

Mixin = classe Python "pura" (sem ``__tablename__``, sem herdar de
``Base``) cuja única função é **injetar colunas** em modelos que
herdam dela. Uso:

    class Source(Base, TimestampMixin):
        __tablename__ = "sources"
        ...

A ordem importa: ``Base`` vem primeiro (traz a ``metadata`` — registro
central de tabelas do SQLAlchemy). Mixins vêm depois — só contribuem
com colunas e comportamentos. Quem chama ``Base.metadata.create_all()``
ou roda Alembic vê as colunas do mixin como se estivessem no modelo.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adiciona ``created_at`` e ``updated_at`` a qualquer modelo."""

    # Padrão SQLAlchemy 2.0:
    #   - `Mapped[T]` é uma anotação de tipo que diz ao mypy/IDE
    #     "esse atributo, quando lido de uma instância, é um T".
    #   - `mapped_column(...)` é o que efetivamente configura a coluna
    #     no banco. Os parâmetros refletem o que vai pro SQL.
    #
    # `DateTime(timezone=True)` → no Postgres vira `TIMESTAMP WITH TIME
    # ZONE`. O banco armazena em UTC e converte na leitura. Cumpre o
    # princípio "UTC em todo o banco" do briefing.
    #
    # `server_default=func.now()` → o DEFAULT é definido no banco
    # (cláusula `DEFAULT now()` no SQL), não só no Python. Diferença
    # prática: um `INSERT` feito direto via psql também recebe o valor.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # `onupdate=func.now()` → SQLAlchemy emite a hora atual sempre que
    # um `UPDATE` for executado via ORM. (Atenção: isso é app-side. Um
    # `UPDATE` feito direto no banco não vai atualizar essa coluna a
    # menos que você crie um trigger no Postgres — fica pra depois.)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
