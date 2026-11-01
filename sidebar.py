"""Sidebar, filtros interativos e aplicação dos filtros ao DataFrame."""

import streamlit as st


def _renderizar_titulo_sidebar() -> None:
    """Renderiza o título da aplicação na sidebar."""
    st.sidebar.markdown(
        """
        <div style="
            text-align: left;
            color: var(--text-color);
            font-family: sans-serif;
            font-size: 1.45rem;
            line-height: 1.25;
            font-weight: 700;
            letter-spacing: -0.02em;
            text-transform: uppercase;
            margin: 0;
        ">
            <div style="white-space: nowrap;">
                <span style="color: #1D5CA8;">📊</span> DASHBOARD
            </div>
            <div style="white-space: nowrap;">
                SALES ANALYTICS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _renderizar_multiselect_popover(
    titulo: str,
    label: str,
    opcoes: list,
    chave: str,
) -> list:
    """Renderiza um filtro múltiplo compacto dentro de um popover."""
    st.sidebar.markdown(f"**{titulo}**")

    with st.sidebar.popover("Selecionar", use_container_width=True):
        return st.multiselect(
            label,
            options=opcoes,
            default=opcoes,
            key=chave,
            label_visibility="collapsed",
        )


def filtros_sidebar(df):
    """Renderiza os controles da sidebar e retorna o DataFrame filtrado."""
    _renderizar_titulo_sidebar()
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtros")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.sidebar.date_input(
        "Período de Análise",
        (min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
    )

    all_regioes = sorted(df["regiao"].unique())
    selected_regioes = _renderizar_multiselect_popover(
        "Regiões", "Selecione as regiões", all_regioes, "filtro-regioes"
    )

    all_categorias = sorted(df["categoria"].unique())
    selected_categorias = _renderizar_multiselect_popover(
        "Categorias", "Selecione as categorias", all_categorias, "filtro-categorias"
    )

    all_produtos = sorted(df["produto"].unique())
    selected_produtos = _renderizar_multiselect_popover(
        "Produtos", "Selecione os produtos", all_produtos, "filtro-produtos"
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    df_filtrado = df[
        (df["date"].dt.date >= start_date)
        & (df["date"].dt.date <= end_date)
        & (df["regiao"].isin(selected_regioes))
        & (df["categoria"].isin(selected_categorias))
        & (df["produto"].isin(selected_produtos))
    ].copy()

    st.sidebar.markdown("---")
    st.sidebar.caption("Versão 1.0")

    return df_filtrado
