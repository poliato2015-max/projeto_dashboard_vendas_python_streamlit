"""Cálculo e renderização dos indicadores principais do dashboard."""

import streamlit as st

from formatting import formatar_moeda_br, formatar_numero_br


def renderiza_cards_kpis(df, meta_faturamento):
    """Calcula e renderiza os quatro cards de KPI."""
    total_faturamento = df["faturamento"].sum()
    total_qty = df["quantidade"].sum()
    avg_ticket = total_faturamento / total_qty if total_qty > 0 else 0

    delta_rev = (
    ((total_faturamento - meta_faturamento) / meta_faturamento) * 100
    if meta_faturamento > 0
    else None
    )

    if delta_rev is None:
        indicador_meta = "Meta indisponível"
        cor_meta = "#777777"
    else:
        indicador_meta = f"{delta_rev:+.1f}% vs meta"
        cor_meta = "#4CAF50" if delta_rev >= 0 else "#FF5252"

    transactions = df.shape[0]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3>Receita Total</h3>
                <h2>{formatar_moeda_br(total_faturamento)}</h2>
                <div class="delta" style="color: {cor_meta}">
                    {indicador_meta}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3>Vendas (Qtd)</h3>
                <h2>{formatar_numero_br(total_qty)}</h2>
                <div class="delta">Unidades vendidas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3>Ticket Médio</h3>
                <h2>{formatar_moeda_br(avg_ticket)}</h2>
                <div class="delta">Por transação</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3>Transações</h3>
                <h2>{formatar_numero_br(transactions)}</h2>
                <div class="delta">Volume total</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return total_faturamento, total_qty, avg_ticket
