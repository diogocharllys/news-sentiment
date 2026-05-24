"""Smoke test mínimo.

Não testa regra de negócio — apenas garante que o pacote está instalado e
importável. Serve de "canário" para problemas de empacotamento (layout ``src/``,
ver ADR-001) e mantém a suíte de testes não-vazia enquanto os testes reais não
chegam nas próximas fases.
"""

from importlib.metadata import version


def test_package_importavel() -> None:
    """O pacote pode ser importado (instalação/empacotamento OK)."""
    import news_sentiment  # noqa: F401


def test_versao_declarada() -> None:
    """Os metadados instalados expõem a versão definida no pyproject."""
    assert version("news-sentiment") == "0.1.0"
