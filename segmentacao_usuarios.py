import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium


st.title("🔦 Lighter Tracker - Dashboard com Insights Iniciais")

st.sidebar.title("Filtros")

# Configuração da página
st.set_page_config(page_title="Segmentação de Usuários", layout="wide")
st.title("Segmentação de Usuários")
st.write("Análise demográfica e comportamental dos usuários de isqueiros.")


# Carregar o dataframe
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("bases_sistema_usuario/df_perfil.csv")
        return df
    except FileNotFoundError:
        st.error("Arquivo 'df_perfil.csv' não encontrado. Verifique se o arquivo está no diretório correto.")
        return None


df_perfil = carregar_dados()

if df_perfil is not None:
    # Filtros interativos na barra lateral
    st.sidebar.title("Filtros")
    faixa_etaria = st.sidebar.slider("Selecione a faixa etária", 
                                    min_value=int(df_perfil["Idade"].min()), 
                                    max_value=int(df_perfil["Idade"].max()), 
                                    value=(int(df_perfil["Idade"].min()), int(df_perfil["Idade"].max())))
    
    generos = st.sidebar.multiselect("Selecione o gênero", 
                                     options=df_perfil["Genero"].unique(), 
                                     default=df_perfil["Genero"].unique())
    
    faixas_renda = st.sidebar.multiselect("Selecione a faixa de renda", 
                                          options=df_perfil["FaixaRenda"].unique(), 
                                          default=df_perfil["FaixaRenda"].unique())
    
    fumante = st.sidebar.multiselect("Selecione o status de fumante", 
                                     options=df_perfil["Fumante_Label"].unique(), 
                                     default=df_perfil["Fumante_Label"].unique())

  # Filtrar o dataframe com base nos filtros
    df_filtrado = df_perfil[
        (df_perfil["Idade"].between(faixa_etaria[0], faixa_etaria[1])) &
        (df_perfil["Genero"].isin(generos)) &
        (df_perfil["FaixaRenda"].isin(faixas_renda)) &
        (df_perfil["Fumante_Label"].isin(fumante))
    ]


    # Verificar se há dados após o filtro
    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Visualizações
        st.header("Distribuições Demográficas")
        col1, col2 = st.columns(2)

        with col1:
            fig_idade = px.histogram(df_filtrado, x="Idade", 
                                    title="Distribuição de Idade",
                                    nbins=20,
                                    color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig_idade, use_container_width=True)

        with col2:
            fig_genero = px.histogram(df_filtrado, x="Genero", 
                                     title="Distribuição de Gênero",
                                     color_discrete_sequence=["#ff7f0e"])
            st.plotly_chart(fig_genero, use_container_width=True)

        st.header("Comportamento e Renda")
        col3, col4 = st.columns(2)

        with col3:
            fig_fumante = px.pie(df_filtrado, names="Fumante_Label", 
                                title="Proporção de Fumantes",
                                color_discrete_sequence=["#2ca02c", "#d62728"])
            st.plotly_chart(fig_fumante, use_container_width=True)

        with col4:
            fig_renda = px.histogram(df_filtrado, x="FaixaRenda", 
                                    title="Distribuição de Faixa de Renda",
                                    color_discrete_sequence=["#9467bd"])
            st.plotly_chart(fig_renda, use_container_width=True)


 # Resumo estatístico
        st.header("Resumo Estatístico")
        st.write(f"**Total de Usuários Filtrados**: {len(df_filtrado)}")
        st.write(f"**Idade Média**: {df_filtrado['Idade'].mean():.1f} anos")
        st.write(f"**Renda Familiar Média**: R${df_filtrado['RendaFamiliar'].mean():.2f}")

        # Dados brutos (opcional)
        if st.checkbox("Mostrar dados brutos"):
            st.dataframe(df_filtrado[["UsuarioID", "Nome", "Idade", "Genero", "FaixaRenda", "Fumante_Label"]])

