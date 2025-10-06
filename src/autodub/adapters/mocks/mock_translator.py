"""
Mock de tradutor para testes de pipeline.

Este adaptador não traduz de verdade. Apenas gera texto simulado
indicando o idioma-alvo configurado.
"""

from typing import Protocol


class ITranslator(Protocol):
    def traduzir(self, texto: str, target_lang: str) -> str: ...


class MockTranslator:
    """Mock simples de tradutor — usado apenas em modo debug."""

    def traduzir(self, texto: str, target_lang: str) -> str:
        """
        Retorna uma tradução simulada.
        Exemplo: "[pt-br] Texto gerado devido ao uso de Mock"
        """
        return f"[{target_lang}] Texto gerado devido ao uso de Mock"
