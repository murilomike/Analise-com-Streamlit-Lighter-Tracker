import streamlit as st
import pandas as pd
import plotly.express as px


# Configuração da página
st.set_page_config(page_title="Popularidade e Desempenho de Isqueiros", layout="wide")
st.title("Popularidade e Desempenho de Isqueiros")
st.write("Análise de marcas, modelos e categorias de isqueiros mais populares com base nas vendas.")

# Carregar o dataframe
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("df_pop_isqueiros.csv")
        return df
    except FileNotFoundError:
        st.error("Arquivo 'df_pop_isqueiros.csv' não encontrado. Verifique se o arquivo está no diretório correto.")
        return None

df_pop_isqueiros = carregar_dados()

f_pop_isqueiros = carregar_dados()

if df_pop_isqueiros is not None:
    # Filtros interativos na barra lateral
    st.sidebar.title("Filtros")
    top_n = st.sidebar.selectbox("Selecione o número de itens a exibir", [5, 10, 15], index=0)
    marcas = st.sidebar.multiselect("Selecione as marcas", 
                                   options=df_pop_isqueiros["NomeMarca"].unique(), 
                                   default=df_pop_isqueiros["NomeMarca"].unique())
    categorias = st.sidebar.multiselect("Selecione as categorias", 
                                       options=df_pop_isqueiros["NomeCategoria"].unique(), 
                                       default=df_pop_isqueiros["NomeCategoria"].unique())
    faixa_preco = st.sidebar.slider("Selecione a faixa de preço unitário (R$)", 
                                   min_value=float(df_pop_isqueiros["PrecoUnitario"].min()), 
                                   max_value=float(df_pop_isqueiros["PrecoUnitario"].max()), 
                                   value=(float(df_pop_isqueiros["PrecoUnitario"].min()), 
                                          float(df_pop_isqueiros["PrecoUnitario"].max())))



    # Filtrar o dataframe com base nos filtros
    df_filtrado = df_pop_isqueiros[
        (df_pop_isqueiros["NomeMarca"].isin(marcas)) &
        (df_pop_isqueiros["NomeCategoria"].isin(categorias)) &
        (df_pop_isqueiros["PrecoUnitario"].between(faixa_preco[0], faixa_preco[1]))
    ]


    
    # Verificar se há dados após o filtro
    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        # Visualizações
        st.header("Popularidade por Marca e Categoria")
        col1, col2 = st.columns(2)

        with col1:
            df_marca = df_filtrado.groupby("NomeMarca")["Quantidade"].sum().reset_index().nlargest(top_n, "Quantidade")
            fig_marca = px.bar(df_marca, x="NomeMarca", y="Quantidade", 
                              title=f"Top {top_n} Marcas Mais Populares",
                              color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig_marca, use_container_width=True)

        with col2:
            df_categoria = df_filtrado.groupby("NomeCategoria")["Quantidade"].sum().reset_index().nlargest(top_n, "Quantidade")
            fig_categoria = px.bar(df_categoria, x="NomeCategoria", y="Quantidade", 
                                  title=f"Top {top_n} Categorias Mais Populares",
                                  color_discrete_sequence=["#ff7f0e"])
            st.plotly_chart(fig_categoria, use_container_width=True)

        st.header("Análise de Preços e Descontos")
        col3, col4 = st.columns(2)

        with col3:
            fig_preco = px.histogram(df_filtrado, x="PrecoUnitario", 
                                    title="Distribuição de Preço Unitário",
                                    nbins=20,
                                    color_discrete_sequence=["#2ca02c"])
            st.plotly_chart(fig_preco, use_container_width=True)

        with col4:
            fig_desconto = px.scatter(df_filtrado, x="Desconto", y="Quantidade", 
                                     title="Relação entre Desconto e Quantidade Vendida",
                                     color="NomeCategoria", size="PrecoUnitario",
                                     color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig_desconto, use_container_width=True)

        # Resumo estatístico
        st.header("Resumo Estatístico")
        st.write(f"**Total de Itens Vendidos**: {int(df_filtrado['Quantidade'].sum())}")
        st.write(f"**Preço Unitário Médio**: R${df_filtrado['PrecoUnitario'].mean():.2f}")
        st.write(f"**Desconto Médio**: R${df_filtrado['Desconto'].mean():.2f}")
        st.write(f"**Subtotal Médio por Item**: R${df_filtrado['SubTotal'].mean():.2f}")

        # Dados brutos (opcional)
        if st.checkbox("Mostrar dados brutos"):
            st.dataframe(df_filtrado[["ItemCompraID", "NomeMarca", "NomeCategoria", "Modelo", "Quantidade", "PrecoUnitario", "Desconto", "SubTotal"]])

