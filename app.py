import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Função para carregar dados
@st.cache_data
def carregar_dados_pop_isqueiros():
    try:
        df = pd.read_csv("bases_sistema_usuario/df_pop_isqueiros.csv")
        return df
    except FileNotFoundError:
        st.error("Arquivo 'df_pop_isqueiros.csv' não encontrado. Verifique se o arquivo está no diretório correto.")
        return None

@st.cache_data
def carregar_dados_perfil():
    try:
        df = pd.read_csv("bases_sistema_usuario/df_perfil.csv")
        return df
    except FileNotFoundError:
        st.error("Arquivo 'df_perfil.csv' não encontrado. Verifique se o arquivo está no diretório correto.")
        return None

# Configuração da página
st.set_page_config(page_title="Análise de Isqueiros e Usuários", layout="wide")

# Seção 1: Popularidade e Desempenho de Isqueiros
st.title("Popularidade e Desempenho de Isqueiros")
st.write("Análise de marcas, modelos e categorias de isqueiros mais populares com base nas vendas.")

df_pop_isqueiros = carregar_dados_pop_isqueiros()

if df_pop_isqueiros is not None:
    # Filtros interativos na barra lateral
    st.sidebar.title("Filtros - Popularidade")
    top_n = st.sidebar.selectbox("Selecione o número de itens a exibir", [5, 10, 15], index=0, key="top_n_pop")
    marcas = st.sidebar.multiselect("Selecione as marcas", 
                                   options=df_pop_isqueiros["NomeMarca"].unique(), 
                                   default=df_pop_isqueiros["NomeMarca"].unique(), key="marcas_pop")
    categorias = st.sidebar.multiselect("Selecione as categorias", 
                                       options=df_pop_isqueiros["NomeCategoria"].unique(), 
                                       default=df_pop_isqueiros["NomeCategoria"].unique(), key="categorias_pop")
    faixa_preco = st.sidebar.slider("Selecione a faixa de preço unitário (R$)", 
                                   min_value=float(df_pop_isqueiros["PrecoUnitario"].min()), 
                                   max_value=float(df_pop_isqueiros["PrecoUnitario"].max()), 
                                   value=(float(df_pop_isqueiros["PrecoUnitario"].min()), 
                                          float(df_pop_isqueiros["PrecoUnitario"].max())), key="faixa_preco_pop")

    # Filtrar o dataframe com base nos filtros
    df_filtrado_pop = df_pop_isqueiros[
        (df_pop_isqueiros["NomeMarca"].isin(marcas)) &
        (df_pop_isqueiros["NomeCategoria"].isin(categorias)) &
        (df_pop_isqueiros["PrecoUnitario"].between(faixa_preco[0], faixa_preco[1]))
    ]

    # Verificar se há dados após o filtro
    if df_filtrado_pop.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Visualizações
        st.header("Popularidade por Marca e Categoria")
        col1, col2 = st.columns(2)

        with col1:
            df_marca = df_filtrado_pop.groupby("NomeMarca")["Quantidade"].sum().reset_index().nlargest(top_n, "Quantidade")
            fig_marca = px.bar(df_marca, x="NomeMarca", y="Quantidade", 
                              title=f"Top {top_n} Marcas Mais Populares",
                              color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig_marca, use_container_width=True)

        with col2:
            df_categoria = df_filtrado_pop.groupby("NomeCategoria")["Quantidade"].sum().reset_index().nlargest(top_n, "Quantidade")
            fig_categoria = px.bar(df_categoria, x="NomeCategoria", y="Quantidade", 
                                  title=f"Top {top_n} Categorias Mais Populares",
                                  color_discrete_sequence=["#ff7f0e"])
            st.plotly_chart(fig_categoria, use_container_width=True)

        # Resumo estatístico
        st.header("Resumo Estatístico")
        st.write(f"**Total de Itens Vendidos**: {int(df_filtrado_pop['Quantidade'].sum())}")
        st.write(f"**Preço Unitário Médio**: R${df_filtrado_pop['PrecoUnitario'].mean():.2f}")
        st.write(f"**Desconto Médio**: R${df_filtrado_pop['Desconto'].mean():.2f}")
        st.write(f"**Subtotal Médio por Item**: R${df_filtrado_pop['SubTotal'].mean():.2f}")

        # Dados brutos (opcional) com chave única
        if st.checkbox("Mostrar dados brutos", key="checkbox_dados_brutos_pop"):
            st.dataframe(df_filtrado_pop[["ItemCompraID", "NomeMarca", "NomeCategoria", "Modelo", "Quantidade", "PrecoUnitario", "Desconto", "SubTotal"]])

# Seção 2: Segmentação de Usuários
st.title("Segmentação de Usuários")
st.write("Análise demográfica e comportamental dos usuários de isqueiros.")

df_perfil = carregar_dados_perfil()

if df_perfil is not None:
    # Filtros interativos na barra lateral
    st.sidebar.title("Filtros - Segmentação")
    faixa_etaria = st.sidebar.slider("Selecione a faixa etária", 
                                    min_value=int(df_perfil["Idade"].min()), 
                                    max_value=int(df_perfil["Idade"].max()), 
                                    value=(int(df_perfil["Idade"].min()), int(df_perfil["Idade"].max())), key="faixa_etaria_seg")
    generos = st.sidebar.multiselect("Selecione o gênero", 
                                     options=df_perfil["Genero"].unique(), 
                                     default=df_perfil["Genero"].unique(), key="generos_seg")
    faixas_renda = st.sidebar.multiselect("Selecione a faixa de renda", 
                                          options=df_perfil["FaixaRenda"].unique(), 
                                          default=df_perfil["FaixaRenda"].unique(), key="faixas_renda_seg")
    fumante = st.sidebar.multiselect("Selecione o status de fumante", 
                                     options=df_perfil["Fumante_Label"].unique(), 
                                     default=df_perfil["Fumante_Label"].unique(), key="fumante_seg")

    # Filtrar o dataframe com base nos filtros
    df_filtrado_seg = df_perfil[
        (df_perfil["Idade"].between(faixa_etaria[0], faixa_etaria[1])) &
        (df_perfil["Genero"].isin(generos)) &
        (df_perfil["FaixaRenda"].isin(faixas_renda)) &
        (df_perfil["Fumante_Label"].isin(fumante))
    ]

    # Verificar se há dados após o filtro
    if df_filtrado_seg.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Visualizações
        st.header("Distribuições Demográficas")
        col1, col2 = st.columns(2)

        with col1:
            fig_idade = px.histogram(df_filtrado_seg, x="Idade", 
                                    title="Distribuição de Idade",
                                    nbins=20,
                                    color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig_idade, use_container_width=True)

        with col2:
            fig_genero = px.histogram(df_filtrado_seg, x="Genero", 
                                     title="Distribuição de Gênero",
                                     color_discrete_sequence=["#ff7f0e"])
            st.plotly_chart(fig_genero, use_container_width=True)

        st.header("Comportamento e Renda")
        col3, col4 = st.columns(2)

        with col3:
            fig_fumante = px.pie(df_filtrado_seg, names="Fumante_Label", 
                                title="Proporção de Fumantes",
                                color_discrete_sequence=["#2ca02c", "#d62728"])
            st.plotly_chart(fig_fumante, use_container_width=True)

        with col4:
            fig_renda = px.histogram(df_filtrado_seg, x="FaixaRenda", 
                                    title="Distribuição de Faixa de Renda",
                                    color_discrete_sequence=["#9467bd"])
            st.plotly_chart(fig_renda, use_container_width=True)

        # Resumo estatístico
        st.header("Resumo Estatístico")
        st.write(f"**Total de Usuários Filtrados**: {len(df_filtrado_seg)}")
        st.write(f"**Idade Média**: {df_filtrado_seg['Idade'].mean():.1f} anos")
        st.write(f"**Renda Familiar Média**: R${df_filtrado_seg['RendaFamiliar'].mean():.2f}")

        # Dados brutos (opcional) com chave única
        if st.checkbox("Mostrar dados brutos", key="checkbox_dados_brutos_seg"):
            st.dataframe(df_filtrado_seg[["UsuarioID", "Nome", "Idade", "Genero", "FaixaRenda", "Fumante_Label"]])