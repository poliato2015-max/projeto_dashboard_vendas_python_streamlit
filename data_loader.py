"""Carregamento cacheado dos dados do banco SQLite."""

import streamlit as st

from database_reader import carregar_dados, carregar_metas

@st.cache_data(ttl=600)
def buscar_dados():
    """Carrega os dados existentes no banco SQLite com cache de 10 minutos."""
    return carregar_dados()

@st.cache_data(ttl=600)
def buscar_metas():
    """Carrega as metas detalhadas com cache de 10 minutos."""
    return carregar_metas()
