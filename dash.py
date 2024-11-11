import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from query import *
from datetime import datetime
from streamlit_modal import Modal
import plotly.graph_objects as go

st.set_page_config(
    page_title="Remama",  # título da página
    page_icon=":dragon:",  # ícone da página (opcional)
    layout="centered",  # ou "wide", se preferir layout mais amplo
    initial_sidebar_state='expanded'    #"collapsed"
)

query = "SELECT * FROM tb_dados"    # Consulta com o banco de dados.
df = conexao(query)                 # Carregar os dados do MySQL.

df['tempo_registro'] = pd.to_datetime(df['tempo_registro'])  # Converter para datetime

# MENU LATERAL
st.sidebar.image('images/remama-logo.png', width=200)
st.sidebar.header('Selecione a informação para gerar o gráfico')

# Seleção de colunas X
colunaX = st.sidebar.selectbox(
    'Eixo X',
    options=['tempo_registro', 'oximetro_saturacao_oxigenio', 'oximetro_frequencia_pulso', 'frequencia_cardiaca', 'temperatura'],
    index=0
)

# Seleção de colunas Y
colunaY = st.sidebar.selectbox(
    'Eixo Y',
    options=['oximetro_saturacao_oxigenio', 'oximetro_frequencia_pulso', 'frequencia_cardiaca', 'temperatura'],
    index=1
)

# Verificar se a coluna selecionada está nos eixos X ou Y
def filtros(atributo):
    return atributo in [colunaX, colunaY]

# Filtro de Range -> SLIDER
st.sidebar.header('Selecione o Filtro')

# Oximetro Saturação Oxigênio
if filtros('oximetro_saturacao_oxigenio'):
    oxigenio_range = st.sidebar.slider(
        'Oximetro Saturação Oxigênio',
        min_value=float(df['oximetro_saturacao_oxigenio'].min()),
        max_value=float(df['oximetro_saturacao_oxigenio'].max()),
        value=(float(df['oximetro_saturacao_oxigenio'].min()), float(df['oximetro_saturacao_oxigenio'].max())),
        step=0.1
    )

# Frequência Pulso
if filtros('oximetro_frequencia_pulso'):
    pulso_range = st.sidebar.slider(
        'Frequencia Pulso',
        min_value=float(df['oximetro_frequencia_pulso'].min()),
        max_value=float(df['oximetro_frequencia_pulso'].max()),
        value=(float(df['oximetro_frequencia_pulso'].min()), float(df['oximetro_frequencia_pulso'].max())),
        step=0.1
    )

# Frequência Cardíaca
if filtros('frequencia_cardiaca'):
    pressao_range = st.sidebar.slider(
        'Frequência Cardiaca',
        min_value=float(df['frequencia_cardiaca'].min()),
        max_value=float(df['frequencia_cardiaca'].max()),
        value=(float(df['frequencia_cardiaca'].min()), float(df['frequencia_cardiaca'].max())),
        step=0.1
    )

# Temperatura
if filtros('temperatura'):
    altitude_range = st.sidebar.slider(
        'Temperatura',
        min_value=float(df['temperatura'].min()),
        max_value=float(df['temperatura'].max()),
        value=(float(df['temperatura'].min()), float(df['temperatura'].max())),
        step=0.1
    )

# Tempo Registro
if filtros("tempo_registro"):
    # Extrair as datas mínimas e máximas em formato de datetime
    min_data = df["tempo_registro"].min()
    max_data = df["tempo_registro"].max()

    # Exibir dois campos de data para seleção de intervalo no sidebar
    data_inicio = st.sidebar.date_input(
        "Data de Início", 
        min_data.date(), 
        min_value=min_data.date(), 
        max_value=max_data.date(),
        format= "DD-MM-YYYY"
    )
    
    data_fim = st.sidebar.date_input(
        "Data de Fim", 
        max_data.date(), 
        min_value=min_data.date(), 
        max_value=max_data.date(),
        format= "DD-MM-YYYY"
    )

    # Converter as datas selecionadas para datetime, incluindo hora
    tempo_registro_range = (
        pd.to_datetime(data_inicio),
        pd.to_datetime(data_fim) + pd.DateOffset(days=1) - pd.Timedelta(seconds=1)
    )

# Cria uma cópia do df original
df_selecionado = df.copy()

# Aplicando os filtros de acordo com os ranges selecionados
if filtros('oximetro_saturacao_oxigenio'):
    df_selecionado = df_selecionado[
        (df_selecionado['oximetro_saturacao_oxigenio'] >= oxigenio_range[0]) &
        (df_selecionado['oximetro_saturacao_oxigenio'] <= oxigenio_range[1])
    ]

if filtros('oximetro_frequencia_pulso'):
    df_selecionado = df_selecionado[
        (df_selecionado['oximetro_frequencia_pulso'] >= pulso_range[0]) &
        (df_selecionado['oximetro_frequencia_pulso'] <= pulso_range[1])
    ]

if filtros('frequencia_cardiaca'):
    df_selecionado = df_selecionado[
        (df_selecionado['frequencia_cardiaca'] >= pressao_range[0]) &
        (df_selecionado['frequencia_cardiaca'] <= pressao_range[1])
    ]

if filtros('temperatura'):
    df_selecionado = df_selecionado[
        (df_selecionado['temperatura'] >= altitude_range[0]) &
        (df_selecionado['temperatura'] <= altitude_range[1])
    ]

# Exibir Tabela
def Home():
    with st.expander('Tabela'):
        mostrarDados = st.multiselect(
            'Filtros: ',
            df_selecionado.columns,
            default=[],
            key='showData_home'
        )

        if mostrarDados:
            st.write(df_selecionado[mostrarDados])

    if not df_selecionado.empty:
        media_cardiaca = df_selecionado['frequencia_cardiaca'].mean()
        media_pulso = df_selecionado['oximetro_frequencia_pulso'].mean()
        media_oxigenio = df_selecionado['oximetro_saturacao_oxigenio'].mean()

        media1, media2 = st.columns(2, gap='large')

        with media1:
            st.info('Média de Frequência Cardíaca', icon='📍')
            st.metric(label='Média', value=f'{media_cardiaca:.2f}')

        with media2:
            st.info('Média de Saturação de Oxigênio', icon='📍')
            st.metric(label='Média', value=f'{media_oxigenio:.2f}')

        st.markdown('''-----------''')

# Geração de Gráficos
def graficos():
    st.title('Dashboard Monitoramento')

    grafico1, grafico2, grafico3, grafico4 = st.tabs(
        [
            'Gráfico de Barras',
            'Gráfico Linear',
            'Gráfico de Área',
            'Gráfico Y'
        ]
    )
    
    with grafico1:

        if df_selecionado.empty:
            st.write('Nenhum dado disponível para gerar o gráfico.')
            return

        if colunaX == colunaY:
            st.warning('Selecione colunas diferentes para os eixos X e Y')
            return

        try:
            grupo_dados = df_selecionado.groupby(by=[colunaX]).size().reset_index(name='Contagem')

            fig_valores = px.bar(
                grupo_dados,
                x=colunaX,
                y='Contagem',
                orientation='h',
                title=f'Contagem de Registros por {colunaX.capitalize()}',
                color_discrete_sequence=['#B388EB'],
                template='plotly_white'
            )
            st.plotly_chart(fig_valores, use_container_width=True, key="grafico_barras")

        except Exception as e:
            st.error(f'Erro ao criar o gráfico: {e}')

    with grafico2:

        if df_selecionado.empty:
            st.write('Nenhum dado disponível para gerar o gráfico.')
            return

        if colunaX == colunaY:
            st.warning('Selecione colunas diferentes para os eixos X e Y')
            return

        try:
            grupo_dados = df_selecionado.groupby(by=[colunaX])[colunaY].mean().reset_index(name=colunaY)
            fig_valores2 = px.line(
            grupo_dados,
            x=colunaX,
            y=colunaY,
            line_shape='linear',  # Tipo de linha
            title=f"Gráfico de Linhas:{colunaX.capitalize()} vs {colunaY.capitalize()}",
            markers=True  # Para mostrar marcadores nos pontos
            )

        except Exception as e:
            st.error(f"Erro ao criar gráfico de linhas: {e}")
        
        st.plotly_chart(fig_valores2, use_container_width=True, key="grafico_linha")

    with grafico3:
        if df_selecionado.empty:
            st.write('Nenhum dado disponível para gerar o gráfico.')
            return

        if colunaX == colunaY:
            st.warning('Selecione colunas diferentes para os eixos X e Y')
            return

        try:
            grupo_dados_X = df_selecionado.groupby(by=[colunaX]).size().reset_index(name='Contagem')
            grupo_dados_Y = df_selecionado.groupby(by=[colunaY]).size().reset_index(name='Contagem')

            fig_valores = go.Figure()

            fig_valores.add_trace(go.Scatter(
                x=grupo_dados_X[colunaX],       # Se pa o X é .count quantidade
                y=grupo_dados_X['Contagem'],       # Y fica com .size, ou seja tamanho
                fill='tozeroy',
                mode='none',
                name=f"Área de {colunaX.capitalize()}"
            ))

            # Adicionando a segunda trace (dados do eixo Y)
            fig_valores.add_trace(go.Scatter(
                x=grupo_dados_Y[colunaY],
                y=grupo_dados_Y['Contagem'],
                fill='tonexty',
                mode='none',
                name=f"Área de {colunaY.capitalize()}"
            ))

            # Estética
            fig_valores.update_layout(
                title=f'Gráfico de Área: {colunaX.capitalize()} vs {colunaY.capitalize()}',
                xaxis_title=colunaX.capitalize(),
                yaxis_title='Contagem',
                template='plotly_white'
            )

            st.plotly_chart(fig_valores, use_container_width=True, key="grafico_area")
        except Exception as e:
            st.error(f"Erro ao criar gráfico de linhas: {e}")
        
        #st.plotly_chart(fig_valores2, use_container_width=True)

# Exibir as funções
Home()
graficos()

if st.button("Atualizar dados"):     # Botão para atualização dos dados.
    df = conexao(query)