"""Ponto de entrada do Dashboard de Vendas."""

import hashlib

import pandas as pd
import streamlit as st

from charts import renderiza_graficos
from config import configurar_pagina
from data_loader import buscar_dados
from exports import renderiza_exportacoes
from kpis import renderiza_cards_kpis
from sidebar import filtros_sidebar
from styles import set_custom_theme


configurar_pagina()


def calcular_hash_filtro(df_filtrado) -> str:
    """Cria uma assinatura estável do conjunto de dados filtrado."""
    return hashlib.md5(
        pd.util.hash_pandas_object(df_filtrado, index=True).values.tobytes()
    ).hexdigest()


def renderiza_aplicacao(df_filtrado) -> None:
    """Renderiza KPIs, abas, gráficos, tabela e exportações."""
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return

    filtro_atual = calcular_hash_filtro(df_filtrado)
    total_faturamento, total_qty, avg_ticket = renderiza_cards_kpis(df_filtrado)

    st.markdown("---")
    tab1, tab2 = st.tabs(["📶 Gráficos", "🔽 Relatório & Exportação"])

    with tab1:
        renderiza_graficos(df_filtrado)

    with tab2:
        renderiza_exportacoes(
            df_filtrado,
            total_faturamento,
            total_qty,
            avg_ticket,
            filtro_atual,
        )

    st.markdown("---")
    with st.expander("⚠️ Sobre este Aplicativo", expanded=False):
        st.markdown(
            """
            **Recursos Integrados:**
            - **Engine:** Python + Streamlit + SQLite.
            - **Visualização:** Plotly Express.
            - **Relatórios:** Geração de PDF com FPDF (compatível com Latin-1).
            - **Performance:** Cache de dados (`@st.cache_data`).
            """
        )


def func_principal() -> None:
    """Coordena o fluxo principal do dashboard."""
    set_custom_theme()
    df = buscar_dados()
    df_filtrado = filtros_sidebar(df)
    renderiza_aplicacao(df_filtrado)


if __name__ == "__main__":
    func_principal()
