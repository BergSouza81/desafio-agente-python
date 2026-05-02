"""
Ferramenta simples para buscar conteúdo Markdown via HTTP.

Esta é a primeira parte do desafio: uma função que recebe uma URL
e retorna o conteúdo do arquivo Markdown.
"""

import requests
from typing import Optional


def fetch_markdown(url: str) -> Optional[str]:
    """
    Busca o conteúdo de um arquivo Markdown via HTTP.

    Args:
        url: URL do arquivo Markdown.

    Returns:
        Conteúdo do Markdown em caso de sucesso, None em caso de erro.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestError as e:
        print(f"Erro ao buscar Markdown: {e}")
        return None


if __name__ == "__main__":
    # Teste rápido
    test_url = "https://raw.githubusercontent.com/igortce/python-agent-challenge/refs/heads/main/python_agent_knowledge_base.md"
    content = fetch_markdown(test_url)
    if content:
        print(f"Conteúdo baixado com sucesso! ({len(content)} caracteres)")
        print(content[:200])  # Preview
    else:
        print("Falha ao baixar conteúdo")
