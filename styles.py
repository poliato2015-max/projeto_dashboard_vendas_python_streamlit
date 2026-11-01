"""Tema visual e estilos CSS customizados do dashboard."""

import streamlit as st


def set_custom_theme() -> None:
    """Injeta os estilos visuais customizados na aplicação."""
    card_bg_color = "#EDEDF3"
    text_color = "#0E0101"
    gold_color = "#E7B40C"
    dark_text = "#070606"

    css = f"""
    <style>
        /* --- Largura da Sidebar --- */
        [data-testid="stSidebar"] {{
            min-width: 280px !important;
            max-width: 280px !important;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            width: 280px !important;
        }}

        /* --- Estilização dos Cards de KPI --- */
        .metric-card {{
            background-color: {card_bg_color};
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #919191;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 10px;
            min-height: 130px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .metric-card h3 {{
            margin: 0;
            font-size: clamp(0.85rem, 1.2vw, 1.1rem);
            color: #394039;
            font-weight: normal;
            white-space: nowrap;
        }}

        .metric-card h2 {{
            margin: 10px 0 0 0;
            font-size: clamp(1rem, 1.7vw, 1.6rem);
            color: {text_color};
            font-weight: bold;
            white-space: nowrap;
        }}

        .metric-card .delta {{
            font-size: clamp(0.7rem, 0.9vw, 0.9rem);
            color: #4CAF50;
            margin-top: 5px;
            white-space: nowrap;
        }}

        /* --- Estilização dos itens selecionados nos multiselects --- */
        [data-baseweb="tag"] {{
            background-color: {gold_color} !important;
            color: {dark_text} !important;
            border-radius: 4px !important;
        }}

        [data-baseweb="tag"] svg {{
            color: {dark_text} !important;
        }}

        [data-baseweb="tag"] svg:hover {{
            color: #FF0000 !important;
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
