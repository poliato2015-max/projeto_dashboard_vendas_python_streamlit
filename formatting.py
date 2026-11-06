"""Funções de formatação utilizadas na interface e nos relatórios."""


def formatar_moeda_br(valor) -> str:
    """Formata valores monetários no padrão brasileiro."""
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )


def formatar_numero_br(valor) -> str:
    """Formata números inteiros no padrão brasileiro."""
    return f"{valor:,.0f}".replace(",", ".")
