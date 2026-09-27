import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Sistema de Inteligência Comercial")
st.subheader("Análise de Oportunidades de Exportação — Embalagens Plásticas Flexíveis")

# Carrega o ranking já calculado
ranking = pd.read_csv("dados_processados/ranking_ipm.csv", sep=";")

# Ordena do maior IPM pro menor
ranking = ranking.sort_values("IPM", ascending=False)

st.markdown("### Ranking de Países por Índice de Potencial de Mercado (IPM)")

# Gráfico de barras dentro da tela do sistema
top10 = ranking.head(10)

fig = px.bar(
    top10,
    x="IPM",
    y="NO_PAIS",
    orientation="h",
    title="Top 10 Países por IPM",
    labels={"IPM": "IPM (0 a 100)", "NO_PAIS": "País"},
    text="IPM"
)
fig.update_layout(yaxis={"categoryorder": "total ascending"})
fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")

st.plotly_chart(fig, use_container_width=True)

# Tabela detalhada, com as colunas mais relevantes pra leitura
st.markdown("### Tabela Detalhada")

colunas_exibir = ["NO_PAIS", "volume_medio_usd", "crescimento_pct", "coef_variacao", "IPM"]
st.dataframe(
    ranking[colunas_exibir].rename(columns={
        "NO_PAIS": "País",
        "volume_medio_usd": "Volume Médio (US$)",
        "crescimento_pct": "Crescimento (%)",
        "coef_variacao": "Coef. Variação",
        "IPM": "IPM"
    }),
    use_container_width=True
)