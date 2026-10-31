# == Módulo 1: Importação de Bibliotecas e Configuração da Página
# Para interagir com o banco de dados SQLite

# Importa bibliotecas de manipulação e análise de dados
import numpy as np   # Para operações numéricas e geração de dados aleatórios
import pandas as pd  # Para manipulação e análise de dados (DataFrames)
import hashlib # Para gerar uma assinatura dos dados filtrados

# Importa bibliotecas de visualização e web app
import plotly.express as px  # Para criação de gráficos interativos
import streamlit as st       # A biblioteca principal para criar a Data App

# Importa a biblioteca de geração de PDF e seus componentes
from fpdf import FPDF
from fpdf.enums import XPos, YPos  # Enumerações para posicionamento no PDF

from database_reader import carregar_dados

# Importa módulos de data e hora
from datetime import datetime, date  # Para manipular datas e calcular períodos

# Funções auxiliares de formatação
def formatar_moeda_br(valor):
    """Formata valores monetários no padrão brasileiro."""
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

def formatar_numero_br(valor):
    """Formata números no padrão brasileiro."""
    return f"{valor:,.0f}".replace(",", ".")

# Configuração Inicial da Aplicação Streamlit
st.set_page_config(
    page_title="Dashboard Sales Analytics",  # Título que aparece na aba do navegador
    page_icon=":bar_chart:",                 # Ícone (emoji) que aparece na aba do navegador
    layout="wide",                           # Define o layout da página para usar a largura total da tela
    initial_sidebar_state="expanded",        # Inicia a parte de sidebar (menu lateral) de forma aberta
)

# == Módulo 2: Carregamento do Banco de Dados
@st.cache_data(ttl=600) # Função de Carregamento de Dados com Cache
def buscar_dados():
    """Carrega os dados existentes no banco SQLite.

    A função somente lê a tabela ``tb_vendas`` por meio do módulo
    ``database_reader``. Ela não cria o banco, não cria tabelas e não insere
    ou altera registros.

    """
    return carregar_dados()

# == Módulo 3: Função da Sidebar e Filtros
# Função com os filtros na barra lateral
def filtros_sidebar(df):
    """
    Cria todos os widgets da sidebar (menu lateral).
    1. Exibe a parte do logo do painel.
    2. Cria os filtros de data, região, categoria e produto.
    3. Aplica os filtros ao DataFrame.
    4. Retorna o DataFrame filtrado.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame original completo (antes dos filtros).
    """
    
    # Banner da Sidebar
    # 'st.sidebar' ancora qualquer elemento streamlit na barra lateral
    # 'markdown' renderiza texto formatado.
    # 'unsafe_allow_html=True' é necessário para renderizar o bloco HTML/CSS customizado

    # Ícone e nome do dashboard na barra lateral
    st.sidebar.markdown(
    """
    <div style="text-align: left; display: flex; flex-direction: column; gap: 3px;">
        <h1 style="
            background: linear-gradient(135deg, #0B3366 0%, #1D5CA8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-fill-color: transparent;
            margin: 0;
            font-size: 1.95rem;
            line-height: 1.45;
            font-weight: 600;
            letter-spacing: -0.02em;
            text-transform: uppercase;
            font-family: sans-serif;
            white-space: nowrap;
        ">
            <span style="-webkit-text-fill-color: initial; text-fill-color: initial; background: none; margin-right: 8px;">📊</span>DASHBOARD<br>SALES ANALYTICS
        </h1>
    </div>
    """,
    unsafe_allow_html=True
    )

    # Adiciona uma linha horizontal para separar o logo do filtro
    st.sidebar.markdown("---")
    
    # Adiciona um cabeçalho para a seção de filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Data
    # Encontra a data mínima e máxima no DataFrame para definir os limites do filtro
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    
    # Cria o widget de seleção de intervalo de datas (calendário)
    # O valor padrão 'value' é uma tupla com o intervalo completo (min_date, max_date)
    date_range = st.sidebar.date_input("Período de Análise", (min_date, max_date), min_value = min_date, max_value = max_date)

    # Filtros de Seleção Múltipla (Multiselect)
    # Filtro de Região
    # 1. Pega todos os valores únicos da coluna 'regiao'
    # 2. 'sorted()' os coloca em ordem alfabética para o menu
    all_regioes = sorted(df["regiao"].unique())
    
    # Cria o widget. 'default=all_regioes' faz com que todas as opções comecem selecionadas por padrão.
    selected_regioes = st.sidebar.multiselect("Regiões", all_regioes, default = all_regioes)

    # Filtro de Categoria
    all_categorias = sorted(df["categoria"].unique())
    selected_categorias = st.sidebar.multiselect("Categorias", all_categorias, default = all_categorias)
    
    # Filtro de Produto
    all_produtos = sorted(df["produto"].unique())
    with st.sidebar.container(key="container-filtro-produtos"):
        selected_produtos = st.multiselect("Produtos", all_produtos,
        default=all_produtos
    )

    # Lógica de Aplicação dos Filtros
    # Validação para garantir que o 'date_range' retornou um início e fim
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        # Fallback caso algo dê errado (ex: usuário limpa o campo)
        start_date, end_date = min_date, max_date

    # Aplica a filtragem no DataFrame principal ('df') usando boolean indexing do Pandas
    df_filtrado = df[

        # Filtro de Data: Compara a data da linha com o 'start_date' e 'end_date'
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date) &
        
        # Filtros de Categoria: '.isin()' verifica se o valor da linha está presente na lista de itens selecionados no multiselect
        (df["regiao"].isin(selected_regioes)) &
        (df["categoria"].isin(selected_categorias)) &
        (df["produto"].isin(selected_produtos))
    ].copy() # .copy() cria um novo DataFrame independente, em vez de uma "fatia"

    # Rodapé da Sidebar
        # Adiciona uma linha horizontal para separar os filtros do rodapé
    st.sidebar.markdown("---")

    # Adiciona uma legenda de rodapé com 'st.sidebar.caption'
    st.sidebar.caption("Versão 1.0")

    # Retorna o DataFrame recém-filtrado para ser usado no corpo principal da página
    return df_filtrado

# === Módulo 4: Função para Renderizar os Cards de KPIs

# Função para os KPIs
def renderiza_cards_kpis(df):

    """
    Calcula e exibe os 4 principais KPIs (Indicadores-Chave de Performance)
    em cards estilizados no topo da página.
    
    Utiliza o DataFrame JÁ FILTRADO para fazer os cálculos.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame filtrado pela sidebar.
    
    Retorna:
    (tuple): Uma tupla com os valores calculados (total_faturamento, total_qty, avg_ticket)
             para que possam ser reutilizados (ex: no PDF).
    """

    # 1. Cálculos dos KPIs
    
    # Soma a coluna 'faturamento' para obter o total
    total_faturamento = df["faturamento"].sum()
    
    # Soma a coluna 'quantidade'
    total_qty = df["quantidade"].sum()
    
    # Calcula o Ticket Médio (Faturamento / Quantidade)
    # Inclui uma verificação 'if total_qty > 0' para evitar um erro de Divisão por Zero
    # se o DataFrame filtrado estiver vazio.
    avg_ticket = total_faturamento / total_qty if total_qty > 0 else 0
    
    # Gera um número aleatório para SIMULAR uma variação (delta) vs. meta.
    # Este é um valor fictício apenas para fins de design do dashboard.
    delta_rev = np.random.uniform(-5, 15)
    
    # --- 2. Criação do Layout ---
    # 'st.columns(4)' cria 4 colunas virtuais de mesmo tamanho
    # 'c1', 'c2', 'c3', 'c4' se tornam "containers" para esses espaços
    c1, c2, c3, c4 = st.columns(4)
    
    # --- 3. Renderização dos Cards ---
    
    # Bloco 'with' garante que o conteúdo a seguir seja renderizado dentro da Coluna 1
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Receita Total</h3>
            <h2>{formatar_moeda_br(total_faturamento)}</h2>
            <div class="delta" style="color: {'#4CAF50' if delta_rev > 0 else '#FF5252'}">
                {delta_rev:+.1f}% vs meta
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Renderiza o Card 2 na Coluna 2
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Vendas (Qtd)</h3>
            <h2>{formatar_numero_br(total_qty)}</h2>
            <div class="delta">Unidades vendidas</div>
        </div>
        """, unsafe_allow_html=True)

    # Renderiza o Card 3 na Coluna 3
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Ticket Médio</h3>
            <h2>{formatar_moeda_br(avg_ticket)}</h2>
            <div class="delta">Por transação</div>
        </div>
        """, unsafe_allow_html=True)

    # Renderiza o Card 4 na Coluna 4
    with c4:
        transactions = df.shape[0]
        st.markdown(f"""
        <div class="metric-card">
            <h3>Transações</h3>
            <h2>{formatar_numero_br(transactions)}</h2>
            <div class="delta">Volume total</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Retorna os valores calculados para que func_principal()
    # possa utilizá-los na geração do PDF.
    return total_faturamento, total_qty, avg_ticket


# === Módulo 5: Função de Geração de Relatório PDF

# Função para gerar o relatório em pdf
def gera_pdf_report(df_filtrado, total_faturamento, total_quantidade, avg_ticket):

    """
    Gera um relatório PDF customizado usando a biblioteca FPDF.
    
    Parâmetros:
    df_filtrado (pd.DataFrame): O DataFrame filtrado.
    total_faturamento (float): O valor do KPI de faturamento.
    total_quantidade (int): O valor do KPI de quantidade.
    avg_ticket (float): O valor do KPI de ticket médio.
    
    Retorna:
    (bytes): Os bytes brutos do arquivo PDF gerado.
    """
    
    # 1. Configuração Inicial do PDF
    # Inicializa o objeto FPDF
    pdf = FPDF()
    
    # Habilita a quebra de página automática com 15mm de margem inferior
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Adiciona uma nova página ao documento
    pdf.add_page()

    # 2. Título e Metadados
    # Define a fonte ("Helvetica", Negrito, Tamanho 16)
    # A fonte "Helvetica" é a substituta moderna da "Arial" para evitar warnings.
    pdf.set_font("Helvetica", "B", 16)
    
    # Cria a célula do título.
    # Parâmetros: (largura, altura, texto, alinhamento)
    # new_x/new_y são a sintaxe moderna para substituir o 'ln=True' (quebra de linha)
    pdf.cell(0, 10, "Relatório Executivo de Vendas", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Adiciona um espaço vertical (quebra de linha) de 5 pontos
    pdf.ln(5)

    # Adiciona o carimbo de data/hora da geração
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # 3. Bloco de Resumo de KPIs (com fundo cinza)
    # Define a cor de preenchimento (cinza claro) e desenha um retângulo
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 35, 190, 25, 'F')
    
    # Define a posição Y (vertical) do cursor para 40,
    # para que o texto seja escrito EM CIMA do retângulo
    pdf.set_y(40)
    
    # Escreve os cabeçalhos dos KPIs
    pdf.set_font("Helvetica", "B", 12)
    
    # new_x=XPos.RIGHT, new_y=YPos.TOP: move o cursor para a direita, mas mantém na mesma linha
    pdf.cell(60, 8, f"Receita Total", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, f"Quantidade", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    
    # new_x=XPos.LMARGIN, new_y=YPos.NEXT: quebra a linha após esta célula
    pdf.cell(60, 8, f"Ticket Médio", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Escreve os valores dos KPIs (logo abaixo dos cabeçalhos)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(60, 8, formatar_moeda_br(total_faturamento), align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, formatar_numero_br(total_quantidade), align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, formatar_moeda_br(avg_ticket), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Adiciona um espaço vertical grande após o bloco de KPIs
    pdf.ln(15)

    # 4. Tabela "Top 15 Vendas"
    # Adiciona o subtítulo da tabela
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Top 15 Vendas (por receita):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Define as larguras de cada coluna da tabela e os nomes dos cabeçalhos
    col_widths = [30, 30, 30, 40, 25, 35] 
    headers = ["Data", "Região", "Categoria", "Produto", "Qtd", "Receita"]
    
    # Loop para desenhar o CABEÇALHO da tabela
    pdf.set_font("Helvetica", "B", 9)
    for i, h in enumerate(headers):
        
        # O '1' no quarto parâmetro desenha a borda da célula
        pdf.cell(col_widths[i], 8, h, 1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
    
    pdf.ln() # Quebra a linha após o cabeçalho estar completo
    
    # 5. População da Tabela com Dados
    # Prepara os dados: ordena o DataFrame pelo faturamento e pega os 15 primeiros
    pdf.set_font("Helvetica", "", 9)
    df_top = df_filtrado.sort_values("faturamento", ascending=False).head(15)
    
    # Loop principal (externo): itera sobre cada linha do DataFrame df_top
    for _, row in df_top.iterrows():
        
        # Extrai os dados da linha do Pandas para uma lista simples
        # Trunca o nome do produto para 20 caracteres para caber na célula
        # Formata valores para números e moeda Brasil.
        data = [
         row["date"].strftime("%d/%m/%Y"),
         row["regiao"],
         row["categoria"],
         row["produto"][:20],
         formatar_numero_br(row["quantidade"]),
         formatar_moeda_br(row["faturamento"])
        ]
        
        # Loop interno: itera sobre cada item (célula) da linha atual
        for i, d in enumerate(data):
            
            # TRATAMENTO DE ENCODING:
            # O FPDF (baseado em Latin-1) quebra com caracteres especiais (ex: ç, ã).
            # Esta linha força o texto para o encoding 'latin-1', substituindo
            # caracteres inválidos por um '?' para evitar que o PDF quebre.
            safe_txt = str(d).encode("latin-1", "replace").decode("latin-1")
            
            # Desenha a célula de dados com o texto seguro e borda
            pdf.cell(col_widths[i], 7, safe_txt, 1, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        pdf.ln() # Quebra a linha após desenhar todas as células da linha

    # 6. Geração e Retorno do PDF
    # .output() sem parâmetros retorna o conteúdo do PDF como bytes (substitui o antigo 'dest="S"')
    result = pdf.output() 

    # Retorna os bytes brutos do PDF, prontos para o botão de download
    return result.encode("latin-1") if isinstance(result, str) else bytes(result)


# === Módulo 6: Função de Estilização (Tema Customizado)

# Função para customização da interface com CSS
def set_custom_theme():

    """
    Define e injeta CSS customizado no app Streamlit.
    Isso é usado para alterar a aparência de elementos que
    o Streamlit não permite customizar nativamente (ex: cores de filtros, cards).
    """

    # 1. Definição das Cores do Tema

    # Cores usadas nos estilos CSS abaixo
    card_bg_color = "#EDEDF3"  # Fundo para os cards de KPI
    text_color = "#0E0101"     # Cor do texto principal
    gold_color = "#E7B40C"     # Cor para os filtros selecionados
    dark_text = "#070606"      # Cor do texto para os filtros selecionados

    # 2. Criação do Bloco de Estilo CSS

    # 'css' é uma "f-string" gigante que contém todo o código CSS.
    # As variáveis Python (ex: {gold_color}) são injetadas no texto.
    css = f"""
    <style>

        /* --- Aumentar Altura Mínima dos Filtros Multiselect --- */
        /* [data-testid="stMultiSelect"]... : É um seletor CSS complexo que "mira" 
           exatamente na caixa interna do widget multiselect da sidebar. */
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:first-child {{
            min-height: 100px !important;  /* Define uma altura mínima de 100px */
            overflow-y: auto !important;   /* Adiciona scroll vertical se os itens estourarem */
        }}

        /* --- Aumentar especificamente o filtro de Produtos --- */
            .st-key-container-filtro-produtos
            [data-testid="stMultiSelect"]
            div[data-baseweb="select"] > div:first-child {{
            min-height: 250px !important;
            height: 250px !important;
            overflow-y: auto !important;
            align-items: flex-start !important;
        }}
    
        /* --- Estilização dos Cards de KPI --- */
        /* Define a aparência da classe 'metric-card' */
        .metric-card {{
            background-color: {card_bg_color};
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #919191;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3); /* Sombra sutil */
            text-align: center;
            margin-bottom: 10px; /* Espaçamento inferior */
        }}

        /* Estilo do subtítulo do card (ex: "Receita Total") */
        .metric-card h3 {{
            margin: 0;
            font-size: 1.2rem;
            color: #394039;
            font-weight: normal;
        }}

        /* Estilo do valor principal do card (ex: "R$ 1.500.000") */
        .metric-card h2 {{
            margin: 10px 0 0 0;
            font-size: 2rem;
            color: {text_color};
            font-weight: bold;
        }}

        /* Estilo do texto 'delta' (ex: "+5.0% vs meta") */
        .metric-card .delta {{
            font-size: 0.99rem;
            color: #4CAF50;
            margin-top: 5px;
        }}
                
        /* --- Estilização dos Itens de Filtro Selecionados (Bege-Ouro) --- */
        /* [data-baseweb="tag"]: Mira nas "pílulas" dos itens selecionados
           dentro da caixa do multiselect. */
        [data-baseweb="tag"] {{
            background-color: {gold_color} !important;
            color: {dark_text} !important;
            border-radius: 4px !important;
        }}
        
        /* Mira no ícone 'X' dentro da pílula */
        [data-baseweb="tag"] svg {{
            color: {dark_text} !important;
        }}
        
        /* Muda a cor do 'X' para vermelho ao passar o mouse, indicando "excluir" */
        [data-baseweb="tag"] svg:hover {{
            color: #FF0000 !important; 
        }}
        
    </style>
    """
    
    # 3. Injeção do CSS na Página

    # st.markdown é usado para renderizar o bloco CSS.
    # 'unsafe_allow_html=True' é OBRIGATÓRIO para que o <style> seja aplicado.
    st.markdown(css, unsafe_allow_html = True)

# === Módulo 7: Função Principal
# Esta função coordena a execução de todas as etapas do aplicativo:
# 1. Aplica o tema visual personalizado;
# 2. Carrega os dados do banco SQLite;
# 3. Exibe a sidebar e aplica os filtros;
# 4. Renderiza o conteúdo principal;
# 5. Exibe os KPIs, gráficos, tabela e exportações.

# Função principal
def func_principal():

    # Aplica o tema visual personalizado antes da renderização
    # dos filtros, cards e demais componentes da interface.
    set_custom_theme()
    # Carrega o DataFrame principal. 
    # Graças ao cache (@st.cache_data), isso só executa a consulta SQL
    # uma vez a cada 10 minutos, tornando o app muito rápido.
    df = buscar_dados()
    
    # Exibe a sidebar, coleta as seleções do usuário e retorna
    # o DataFrame já filtrado (df_filtrado) com base nas seleções do usuário.
    df_filtrado = filtros_sidebar(df)

    # Início: Layout da Página Principal
    
    # Verificação de Segurança
    # Se os filtros do usuário resultarem em um DataFrame vazio,
    # exibe um aviso e encerra a execução da função principal.
    # Isso evita que os cálculos de KPIs e gráficos quebrem.
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return # Para a execução da função

    # Cria uma assinatura dos dados atualmente filtrados.
    filtro_atual = hashlib.md5(pd.util.hash_pandas_object(df_filtrado,index=True).values.tobytes()).hexdigest()

    # Inicializa o estado do PDF.
    if "pdf_bytes" not in st.session_state:
        st.session_state.pdf_bytes = None

    if "pdf_filtro_hash" not in st.session_state:
        st.session_state.pdf_filtro_hash = None

    # Invalida o PDF quando os filtros alteram os dados filtrados.
    if st.session_state.pdf_filtro_hash != filtro_atual:
       st.session_state.pdf_bytes = None
       st.session_state.pdf_filtro_hash = None

    # Chama a função para renderizar os 4 cards de KPI.
    # Ela usa o DataFrame *filtrado* para os cálculos.
    # Também armazena os valores retornados (total_faturamento, etc.)
    # para usá-los mais tarde na geração do PDF.
    total_faturamento, total_qty, avg_ticket = renderiza_cards_kpis(df_filtrado)

    # Adiciona uma linha horizontal para separar os KPIs das abas
    st.markdown("---")

    # Layout de Abas

    # Cria a navegação principal da página com duas abas
    tab1, tab2 = st.tabs(["📶 Gráficos", "🔽 Relatório & Exportação"])

    # Conteúdo da Aba 1: Gráficos
    with tab1:

        # Cria a primeira linha de layout da aba: 
        # Cria a segunda linha de layout da aba: duas colunas de tamanho igual
        col_left, col_right = st.columns(2)

        # Bloco do Gráfico 1: Evolução da Receita (Coluna da Esquerda)
        with col_left:

           # Coloca o gráfico em uma caixa ( estilo de bordas )
           with st.container(border=True):

                # centralizar o título do gráfico com HTML
                st.markdown(
                  "<h3 style='text-align: center;'>Evolução da Receita Diária</h3>",
                  unsafe_allow_html=True
                )

                # Agrupa os dados por data e soma o faturamento
                daily_rev = (df_filtrado.groupby("date")[["faturamento"]].sum().reset_index())

                # Cria o gráfico de linha com Plotly Express
                fig_line = px.line(daily_rev,x="date",y="faturamento",template="plotly_dark",height=400)

                # Adiciona uma estilização: preenchimento verde sob a linha
                fig_line.update_traces(fill="tozeroy",line=dict(color="#00CC96", width=3))

                # Renderiza o gráfico no Streamlit, usando a largura total da coluna
                st.plotly_chart(fig_line, width="stretch")

        # Bloco do Gráfico 2: Mix de Categorias (Coluna da Direita)
        with col_right:

            # Coloca o gráfico em uma caixa ( estilo de bordas )
            with st.container(border=True):
            
                # centralizar o título do gráfico com HTML
                st.markdown(
                  "<h3 style='text-align: center;'>Mix de Categorias</h3>",
                  unsafe_allow_html=True
                )

                # Agrupa por categoria e soma o faturamento
                cat_rev = df_filtrado.groupby("categoria")[["faturamento"]].sum().reset_index()
            
                # Cria um gráfico de pizza (donut)
                fig_pie = px.pie(cat_rev, values="faturamento", names="categoria", hole=0.4, template="plotly_dark", height=400)
                st.plotly_chart(fig_pie, width='stretch') 

        # Cria a segunda linha de layout da aba: duas colunas de tamanho igual
        c_a, c_b = st.columns(2)
        
        # Bloco do Gráfico 3: Performance Regional
        with c_a:

          # Coloca o gráfico em uma caixa ( estilo de bordas )
          with st.container(border=True):

            # centralizar o título do gráfico com HTML
            st.markdown(
              "<h3 style='text-align: center;'>Performance Regional</h3>",
               unsafe_allow_html=True
            )

            region_rev = (
            df_filtrado.groupby("regiao", as_index=False)["faturamento"].sum()
            .sort_values("faturamento", ascending=False)
            )

            fig_bar = px.bar(
                region_rev,
                x="faturamento", y="regiao", color="regiao", template="plotly_dark",
                  text_auto='.2s', orientation="h"
            )

            # oculta a legenda do gráfico
            fig_bar.update_layout(showlegend=False)

            st.plotly_chart(fig_bar, width='stretch') 
            
        # Bloco do Gráfico 4: Análise de Dia da Semana (com tradução)
        with c_b:

          # Coloca o gráfico em uma caixa ( estilo de bordas )
          with st.container(border=True):

            # centralizar o título do gráfico com HTML
            st.markdown(
              "<h3 style='text-align: center;'>Análise Dia da Semana</h3>",
              unsafe_allow_html=True
            )

            # Mapeamento para traduzir os dias da semana para Português
            dias_pt_map = {
                0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
                3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
            }

            # Lista para garantir a ordem correta no gráfico
            dias_pt_ordem = [
                "Segunda-feira", "Terça-feira", "Quarta-feira", 
                "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
            ]

            # Cria uma cópia exclusiva para o gráfico semanal.
            # Assim, as colunas auxiliares não são adicionadas ao df_filtrado
            # utilizado pela tabela, pelo CSV e pelo relatório PDF.
            df_weekday = df_filtrado.copy()

            # Cria a coluna numérica do dia da semana.
            # Segunda-feira = 0 e Domingo = 6.
            df_weekday["weekday_num"] = (
                df_weekday["date"].dt.dayofweek
            )

            # Traduz os números dos dias para os nomes em português.
            df_weekday["dia_semana"] = (
                df_weekday["weekday_num"].map(dias_pt_map)
            )

            # Agrupa a receita média por dia da semana
            # e mantém a ordem correta dos dias.
            wd_rev = (
                df_weekday
                .groupby("dia_semana")[["faturamento"]]
                .mean()
                .reindex(dias_pt_ordem)
                .reset_index()
            )

            # Cria o gráfico de barras
            fig_heat = px.bar(wd_rev, x="dia_semana", y="faturamento", title="Receita Média x Dia", template="plotly_dark")
            st.plotly_chart(fig_heat, width='stretch')

        # Coloca o gráfico em uma caixa ( estilo de bordas )
        with st.container(border=True):    
        
        # Bloco do Gráfico 5: Dispersão (Scatter Plot)
        # centralizar o título do gráfico com HTML
            st.markdown(
             "<h3 style='text-align: center;'>Dispersão: Quantidade x Faturamento x Produto</h3>",
                 unsafe_allow_html=True
            )

        # Este gráfico mostra a correlação positiva que criamos nos dados fictícios
            fig_scat = px.scatter(
              df_filtrado, x="quantidade", y="faturamento", color="categoria", size="faturamento",
              hover_data=["produto"], template="plotly_dark", height=500
            )
            st.plotly_chart(fig_scat, width='stretch') 

    # Conteúdo da Aba 2: Dados e Exportação
    with tab2:
        
            # Converte os dados filtrados para CSV em memória.
            # utf-8-sig melhora a compatibilidade com o Excel.
            csv_data = df_filtrado.to_csv(
                index=False
            ).encode("utf-8-sig")

            with st.container(border=False):

                col_titulo, col_csv, col_gerar_pdf, col_baixar_pdf = st.columns([2.5, 1, 1, 1])

            with col_titulo:
               st.markdown(
                 "<h3 style='margin: 0;'>Relatório Tabular</h3>",
                 unsafe_allow_html=True
                )

            with col_csv:
               st.download_button(
                label="Baixar CSV",
                data=csv_data,
                file_name="dados_filtrados.csv",
                mime="text/csv",
                width="stretch",
                key="download-csv"
               )

            with col_gerar_pdf:
               if st.button(
               "Gerar PDF",
               width="stretch",
               key="gerar-pdf"
               ):
        
                with st.spinner("Renderizando PDF..."):
                     st.session_state.pdf_bytes = gera_pdf_report(
                     df_filtrado,
                     total_faturamento,
                     total_qty,
                     avg_ticket
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
                key="download-pdf"
                 )
              else:
                st.button(
                "Baixar PDF",
                width="stretch",
                disabled=True,
                key="download-pdf-disabled"
                )

            st.dataframe(
                df_filtrado,
                width="stretch",
                height=400,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn(
                        "ID",
                        format="%d"
                    ),
                    "date": st.column_config.DateColumn(
                        "Data",
                        format="DD/MM/YYYY"
                    ),
                    "regiao": st.column_config.TextColumn("Região"),
                    "categoria": st.column_config.TextColumn("Categoria"),
                    "produto": st.column_config.TextColumn("Produto"),
                    "faturamento": st.column_config.NumberColumn(
                        "Faturamento",
                        format="R$ %.2f"
                    ),
                    "quantidade": st.column_config.NumberColumn(
                        "Quantidade",
                        format="%d"
                    ),
                }
            )

    # Rodapé da Página Principal
    st.markdown("---")
    
    # Caixa "expander" (sanfona) com informações sobre o app
    with st.expander("⚠️ Sobre este Aplicativo", expanded=False):
        st.markdown("""
        **Recursos Integrados:**
        - **Engine:** Python + Streamlit + SQLite.
        - **Visualização:** Plotly Express.
        - **Relatórios:** Geração de PDF com FPDF (compatível com Latin-1).
        - **Performance:** Cache de dados (`@st.cache_data`).
        """)


# === Módulo 8: Ponto de Entrada da Execução

# Esta é uma construção padrão em Python.
# Python define internamente a variável '__name__' para todos os scripts.
# Se você executar este script DIRETAMENTE (ex: 'python app.py'),
# Python definirá __name__ = "__main__".
# Se este script for IMPORTADO por outro script,
# Python definirá __name__ = "app" (o nome do arquivo).

# Portanto, este 'if' garante que o código dentro dele (a chamada para 'func_principal()')
# só será executado se este arquivo for o ponto de partida,
# e não se ele for apenas importado como um módulo.
if __name__ == "__main__":
    
    # Chama a função principal do aplicativo.
    func_principal()