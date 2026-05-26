"""Módulo para buscar itens do feed de economia da Agência Brasil."""

from dataclasses import dataclass
from datetime import UTC, datetime

import feedparser

FEED_URL = "https://agenciabrasil.ebc.com.br/rss/economia/feed.xml"


@dataclass(frozen=True)  # Using dataclass to define a simple data structure for feed items
class FeedItem:
    title: str
    url: str
    published_at: datetime | None
    raw_text: str


def fetch_economia_items() -> list[FeedItem]:
    """Buscar os itens do feed de economia da Agência Brasil e retornar uma lista de FeedItem."""
    feed = feedparser.parse(FEED_URL)
    if feed.bozo:
        raise ValueError(f"Erro ao analisar o feed: {feed.bozo_exception}")
    items = []
    for entry in feed.entries:
        published_at = None
        if "published_parsed" in entry and entry.published_parsed is not None:
            published_at = datetime(*entry.published_parsed[:6]).replace(tzinfo=UTC)
        item = FeedItem(
            title=entry.title, url=entry.link, published_at=published_at, raw_text=entry.summary
        )
        items.append(item)
    return items


if __name__ == "__main__":  # This block is for testing the function when the script is run directly
    items = fetch_economia_items()
    for item in items:
        print(item)
