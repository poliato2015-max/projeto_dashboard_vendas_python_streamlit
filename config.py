"""Configurações gerais da aplicação Streamlit."""

import streamlit as st


def configurar_pagina() -> None:
    """Configura título, ícone e layout da aplicação."""
    st.set_page_config(
        page_title="Dashboard Sales Analytics",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
