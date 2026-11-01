"""Gráficos analíticos exibidos na aba principal do dashboard."""

import plotly.express as px
import streamlit as st


def _titulo_grafico(texto: str) -> None:
    st.markdown(
        f"<h3 style='text-align: center;'>{texto}</h3>",
        unsafe_allow_html=True,
    )


def renderiza_graficos(df_filtrado) -> None:
    """Renderiza os cinco gráficos analíticos do dashboard."""
    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True):
            _titulo_grafico("Evolução da Receita Diária")
            daily_rev = (
                df_filtrado.groupby("date")["faturamento"]
                .sum()
                .reset_index()
            )
            fig_line = px.line(
                daily_rev,
                x="date",
                y="faturamento",
                template="plotly_dark",
                height=400,
            )
            fig_line.update_traces(
                fill="tozeroy",
                line=dict(color="#00CC96", width=3),
            )
            st.plotly_chart(fig_line, width="stretch")

    with col_right:
        with st.container(border=True):
            _titulo_grafico("Mix de Categorias")
            cat_rev = (
                df_filtrado.groupby("categoria")["faturamento"]
                .sum()
                .reset_index()
            )
            fig_pie = px.pie(
                cat_rev,
                values="faturamento",
                names="categoria",
                hole=0.4,
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig_pie, width="stretch")

    c_a, c_b = st.columns(2)

    with c_a:
        with st.container(border=True):
            _titulo_grafico("Performance Regional")
            region_rev = (
                df_filtrado.groupby("regiao", as_index=False)["faturamento"]
                .sum()
                .sort_values("faturamento", ascending=False)
            )
            fig_bar = px.bar(
                region_rev,
                x="faturamento",
                y="regiao",
                color="regiao",
                template="plotly_dark",
                text_auto=".2s",
                orientation="h",
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, width="stretch")

    with c_b:
        with st.container(border=True):
            _titulo_grafico("Análise Dia da Semana")
            dias_pt_map = {
                0: "Segunda-feira",
                1: "Terça-feira",
                2: "Quarta-feira",
                3: "Quinta-feira",
                4: "Sexta-feira",
                5: "Sábado",
                6: "Domingo",
            }
            dias_pt_ordem = [
                "Segunda-feira",
                "Terça-feira",
                "Quarta-feira",
                "Quinta-feira",
                "Sexta-feira",
                "Sábado",
                "Domingo",
            ]
            df_weekday = df_filtrado.copy()
            df_weekday["weekday_num"] = df_weekday["date"].dt.dayofweek
            df_weekday["dia_semana"] = df_weekday["weekday_num"].map(dias_pt_map)
            wd_rev = (
                df_weekday.groupby("dia_semana")["faturamento"]
                .mean()
                .reindex(dias_pt_ordem)
                .reset_index()
            )
            fig_heat = px.bar(
                wd_rev,
                x="dia_semana",
                y="faturamento",
                title="Receita Média x Dia",
                template="plotly_dark",
            )
            st.plotly_chart(fig_heat, width="stretch")

    with st.container(border=True):
        _titulo_grafico("Dispersão: Quantidade x Faturamento x Produto")
        fig_scat = px.scatter(
            df_filtrado,
            x="quantidade",
            y="faturamento",
            color="categoria",
            size="faturamento",
            hover_data=["produto"],
            template="plotly_dark",
            height=500,
        )
        st.plotly_chart(fig_scat, width="stretch")
