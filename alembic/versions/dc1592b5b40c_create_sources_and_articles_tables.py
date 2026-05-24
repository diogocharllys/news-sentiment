"""create sources and articles tables

Revision ID: dc1592b5b40c
Revises:
Create Date: 2026-05-23 23:45:30.509985

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dc1592b5b40c"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # ── Ordem importa ────────────────────────────────────────────────
    # `articles` tem FK para `sources`, então `sources` precisa existir
    # primeiro. No downgrade, a ordem é a inversa (dropar `articles`
    # antes de `sources`).

    # `op.create_table(...)` emite um CREATE TABLE. Cada `sa.Column(...)`
    # é uma coluna (tipo + flags). As `sa.*Constraint(...)` no fim são
    # constraints no nível da tabela.
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False),
        # `is_active` SEM server_default — espelha o modelo, que só tem
        # `default=True` (app-side). Consequência: um INSERT via SQL cru
        # precisa informar `is_active`; via ORM o default cobre.
        sa.Column("is_active", sa.Boolean(), nullable=False),
        # `server_default=sa.func.now()` => cláusula `DEFAULT now()` no
        # SQL. Espelha o `TimestampMixin`. Por isso o INSERT não precisa
        # passar created_at/updated_at.
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # Nomes de constraint explícitos seguindo a NAMING_CONVENTION do
        # Base.metadata. `op.f(...)` marca o nome como "já formatado" —
        # diz ao Alembic pra não reaplicar nenhuma convenção em cima.
        # Em migration manual a convenção não roda sozinha, então
        # nomeamos à mão pra bater com o que o --autogenerate produziria
        # (evita diffs fantasma no futuro).
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
        sa.UniqueConstraint("slug", name=op.f("uq_sources_slug")),
    )

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        # nullable=True => coluna aceita NULL (fonte sem data confiável).
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # FK source_id -> sources.id, com ON DELETE RESTRICT (decisão 7):
        # o banco recusa deletar uma Source que ainda tem Articles.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_articles_source_id_sources"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_articles")),
        sa.UniqueConstraint("url", name=op.f("uq_articles_url")),
    )
    # `index=True` no modelo (coluna source_id) vira um CREATE INDEX
    # separado. unique=False porque uma Source tem muitos Articles.
    op.create_index(
        op.f("ix_articles_source_id"),
        "articles",
        ["source_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f("ix_articles_source_id"), table_name="articles")
    op.drop_table("articles")
    op.drop_table("sources")
