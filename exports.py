"""Aba de dados detalhados e exportações CSV/PDF."""

from datetime import date

import streamlit as st

from reports import gera_pdf_report


def renderiza_exportacoes(
    df_filtrado,
    total_faturamento,
    total_qty,
    avg_ticket,
    filtro_atual: str,
) -> None:
    """Renderiza tabela, exportação CSV e fluxo de geração/download do PDF."""
    if "pdf_bytes" not in st.session_state:
        st.session_state.pdf_bytes = None

    if "pdf_filtro_hash" not in st.session_state:
        st.session_state.pdf_filtro_hash = None

    if st.session_state.pdf_filtro_hash != filtro_atual:
        st.session_state.pdf_bytes = None
        st.session_state.pdf_filtro_hash = None

    csv_data = df_filtrado.to_csv(index=False).encode("utf-8-sig")

    col_titulo, col_csv, col_gerar_pdf, col_baixar_pdf = st.columns([2.5, 1, 1, 1])

    with col_titulo:
        st.markdown(
            "<h3 style='margin: 0;'>Relatório Tabular</h3>",
            unsafe_allow_html=True,
        )

    with col_csv:
        st.download_button(
            label="Baixar CSV",
            data=csv_data,
            file_name="dados_filtrados.csv",
            mime="text/csv",
            width="stretch",
            key="download-csv",
        )

    with col_gerar_pdf:
        if st.button("Gerar PDF", width="stretch", key="gerar-pdf"):
            with st.spinner("Renderizando PDF..."):
                st.session_state.pdf_bytes = gera_pdf_report(
                    df_filtrado,
                    total_faturamento,
                    total_qty,
                    avg_ticket,
                )
            st.session_state.pdf_filtro_hash = filtro_atual
            st.success("PDF gerado com sucesso, agora clique em Baixar PDF.")

    with col_baixar_pdf:
        if st.session_state.pdf_bytes is not None:
            st.download_button(
                label="Baixar PDF",
                data=st.session_state.pdf_bytes,
                file_name=f"Relatorio_Vendas_{date.today()}.pdf",
                mime="application/pdf",
                width="stretch",
                key="download-pdf",
            )
        else:
            st.button(
                "Baixar PDF",
                width="stretch",
                disabled=True,
                key="download-pdf-disabled",
            )

    st.dataframe(
        df_filtrado,
        width="stretch",
        height=400,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "date": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "regiao": st.column_config.TextColumn("Região"),
            "categoria": st.column_config.TextColumn("Categoria"),
            "produto": st.column_config.TextColumn("Produto"),
            "faturamento": st.column_config.NumberColumn("Faturamento", format="R$ %.2f"),
            "quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
        },
    )
