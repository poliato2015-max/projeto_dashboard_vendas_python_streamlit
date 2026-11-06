"""Ponto de entrada do Dashboard de Vendas."""

import hashlib

import pandas as pd
import streamlit as st

from charts import renderiza_graficos
from config import configurar_pagina
from data_loader import buscar_dados, buscar_metas
from exports import renderiza_exportacoes
from kpis import renderiza_cards_kpis
from sidebar import filtros_sidebar
from styles import set_custom_theme
from calendar import monthrange


configurar_pagina()


def calcular_hash_filtro(df_filtrado) -> str:
    """Cria uma assinatura estável do conjunto de dados filtrado."""
    return hashlib.md5(
        pd.util.hash_pandas_object(df_filtrado, index=True).values.tobytes()
    ).hexdigest()


def calcular_meta_proporcional(
    df_metas,
    start_date,
    end_date,
) -> float:
    """Calcula a meta proporcional ao intervalo de datas selecionado."""
    meta_total = 0.0

    for periodo, grupo in df_metas.groupby("periodo"):
        ano, mes = map(int, periodo.split("-"))

        ultimo_dia = monthrange(ano, mes)[1]
        inicio_mes = start_date.replace(year=ano, month=mes, day=1)
        fim_mes = start_date.replace(
            year=ano,
            month=mes,
            day=ultimo_dia,
        )

        inicio_rateio = max(start_date, inicio_mes)
        fim_rateio = min(end_date, fim_mes)

        if inicio_rateio <= fim_rateio:
            dias_selecionados = (
                fim_rateio - inicio_rateio
            ).days + 1

            meta_mensal = grupo["meta_faturamento"].sum()

            meta_total += (
                meta_mensal
                * dias_selecionados
                / ultimo_dia
            )

    return meta_total


def renderiza_aplicacao(df_filtrado, meta_faturamento) -> None:
    """Renderiza KPIs, abas, gráficos, tabela e exportações."""
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return

    filtro_atual = calcular_hash_filtro(df_filtrado)
    total_faturamento, total_qty, avg_ticket = renderiza_cards_kpis(df_filtrado, meta_faturamento)

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
    df_metas = buscar_metas()
    
    (
        df_filtrado,
        start_date,
        end_date,
        selected_regioes,
        selected_categorias,
        selected_produtos,
    ) = filtros_sidebar(df)

    periodo_inicio = start_date.strftime("%Y-%m")
    periodo_fim = end_date.strftime("%Y-%m")

    df_metas_filtrado = df_metas[
        (df_metas["periodo"] >= periodo_inicio)
        & (df_metas["periodo"] <= periodo_fim)
        & (df_metas["regiao"].isin(selected_regioes))
        & (df_metas["categoria"].isin(selected_categorias))
        & (df_metas["produto"].isin(selected_produtos))
    ].copy()

    meta_faturamento = calcular_meta_proporcional(
        df_metas_filtrado,
        start_date,
        end_date,
    )

    renderiza_aplicacao(df_filtrado, meta_faturamento)

if __name__ == "__main__":
    func_principal()
