"""
Adaptadores de tradução de texto.

Inclui:
- MockTranslator: versão simulada para testes (não chama API real)
- DeepLTranslator: estrutura base para tradução real (DeepL ou OpenAI)
"""

from __future__ import annotations

from autodub.interfaces.translator_interface import ITranslator


class MockTranslator(ITranslator):
    """
    Adapter de tradução simulado (para testes e modo offline).

    Simplesmente devolve o texto original com uma marca de idioma.
    """

    def traduzir(self, texto: str, target_lang: str) -> str:
        return f"[{target_lang}] {texto}"


class DeepLTranslator(ITranslator):
    """
    Adapter de tradução real usando API (estrutura base).

    Substitua pela implementação real com DeepL, OpenAI ou MarianMT.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def traduzir(self, texto: str, target_lang: str) -> str:
        """
        Traduz texto para o idioma de destino.
        Esta implementação é apenas um placeholder.

        Para uso real, integre a API oficial:
        - DeepL (https://www.deepl.com/pro-api)
        - OpenAI GPT (com prompt de tradução)
        """
        # Aqui virá a integração real futuramente
        # Exemplo: chamada de API, client = deepl.Translator(self.api_key)
        return f"[traduzido-{target_lang}] {texto}"
