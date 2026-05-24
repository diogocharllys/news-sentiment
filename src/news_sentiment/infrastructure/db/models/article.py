"""Modelo ``Article`` — notícia coletada de uma ``Source``."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from news_sentiment.infrastructure.db.base import Base
from news_sentiment.infrastructure.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from news_sentiment.infrastructure.db.models.source import Source


class Article(Base, TimestampMixin):
    """Catálogo de notícias coletadas pelo scraper, associadas a uma fonte (``Source``)."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # FK para Source. O nome da coluna é "source_id" por convenção.
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # Resumo para exibição

    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # Texto bruto para NLP

    source: Mapped["Source"] = relationship("Source", back_populates="articles")

    # Observações pedagógicas (não vai pro código final):
    #
    # 1) Faltam índices? Sim — adicionar em colunas consultadas com frequência
    #    (ex.: ``published_at``). A migration manual pode criar índices.
