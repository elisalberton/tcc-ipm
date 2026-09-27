import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Sistema de Inteligência Comercial")
st.subheader("Análise de Oportunidades de Exportação — Embalagens Plásticas Flexíveis")

ranking_completo = pd.read_csv("dados_processados/ranking_ipm.csv", sep=";")

# === TELA 1: Seleção do produto (NCM) ===
# Dicionário = descrição do produto: código NCM
opcoes_ncm = ranking_completo[["CO_NCM", "NO_NCM_POR"]].drop_duplicates().sort_values("CO_NCM")
opcoes_ncm["rotulo"] = opcoes_ncm["CO_NCM"].astype(str) + " — " + opcoes_ncm["NO_NCM_POR"]

st.sidebar.header("Seleção do Produto")
rotulo_escolhido = st.sidebar.selectbox(
    "Escolha o NCM a ser analisado:",
    opcoes_ncm["rotulo"]
)

# Descobre qual CO_NCM corresponde ao rótulo escolhido
ncm_escolhido = opcoes_ncm[opcoes_ncm["rotulo"] == rotulo_escolhido]["CO_NCM"].iloc[0]

# Filtra o ranking só pro NCM escolhido
ranking = ranking_completo[ranking_completo["CO_NCM"] == ncm_escolhido].copy()
ranking = ranking.sort_values("IPM", ascending=False)

st.markdown(f"### Produto selecionado: `{rotulo_escolhido}`")

# === TELA 3: Análise de Oportunidades (reage à escolha acima) ===
st.markdown("### Ranking de Países por Índice de Potencial de Mercado (IPM)")

top10 = ranking.head(10)

fig = px.bar(
    top10,
    x="IPM",
    y="NO_PAIS",
    orientation="h",
    title=f"Top 10 Países por IPM — NCM {ncm_escolhido}",
    labels={"IPM": "IPM (0 a 100)", "NO_PAIS": "País"},
    text="IPM"
)
fig.update_layout(yaxis={"categoryorder": "total ascending"})
fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")

st.plotly_chart(fig, use_container_width=True)

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