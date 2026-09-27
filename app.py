import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Sistema de Inteligência Comercial")
st.subheader("Análise de Oportunidades de Exportação — Embalagens Plásticas Flexíveis")

# Carrega os dados
ranking_completo = pd.read_csv("dados_processados/ranking_ipm.csv", sep=";")
resumo_completo = pd.read_csv("dados_brutos/resumo_pais_ano.csv", sep=";")

# === TELA 1: Seleção do produto (NCM) — barra lateral
opcoes_ncm = ranking_completo[["CO_NCM", "NO_NCM_POR"]].drop_duplicates().sort_values("CO_NCM")
opcoes_ncm["rotulo"] = opcoes_ncm["CO_NCM"].astype(str) + " — " + opcoes_ncm["NO_NCM_POR"]

st.sidebar.header("Seleção do Produto")
rotulo_escolhido = st.sidebar.selectbox(
    "Escolha o NCM a ser analisado:",
    opcoes_ncm["rotulo"]
)
ncm_escolhido = opcoes_ncm[opcoes_ncm["rotulo"] == rotulo_escolhido]["CO_NCM"].iloc[0]

st.markdown(f"### Produto selecionado: `{rotulo_escolhido}`")

# Filtra o ranking só pro NCM escolhido
ranking = ranking_completo[ranking_completo["CO_NCM"] == ncm_escolhido].copy()
ranking = ranking.sort_values("IPM", ascending=False)

resumo = resumo_completo[resumo_completo["CO_NCM"] == ncm_escolhido].copy()

# Cria as abas do sistema
tab_visao_global, tab_oportunidades = st.tabs(["Visão Global", "Análise de Oportunidades"])

# === TELA 2: Visão Global ===
with tab_visao_global:
    st.markdown("### Top 10 Países de Destino (por Volume Médio Exportado)")

    top10_volume = ranking.sort_values("volume_medio_usd", ascending=False).head(10)

    fig_top10 = px.bar(
        top10_volume,
        x="volume_medio_usd",
        y="NO_PAIS",
        orientation="h",
        title=f"Top 10 Destinos — NCM {ncm_escolhido}",
        labels={"volume_medio_usd": "Volume Médio Exportado (US$)", "NO_PAIS": "País"},
        text="volume_medio_usd"
    )
    fig_top10.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_top10.update_traces(texttemplate="%{text:,.0f}", textposition="outside")

    st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("### Evolução das Exportações — Top 5 Países (2021-2025)")

    top5_paises = top10_volume.head(5)["NO_PAIS"].tolist()
    resumo_top5 = resumo[resumo["NO_PAIS"].isin(top5_paises)]

    fig_evolucao = px.line(
        resumo_top5,
        x="CO_ANO",
        y="valor_exportado_usd",
        color="NO_PAIS",
        title=f"Evolução das Exportações — NCM {ncm_escolhido}",
        labels={"CO_ANO": "Ano", "valor_exportado_usd": "Valor Exportado (US$)", "NO_PAIS": "País"},
        markers=True
    )

    st.plotly_chart(fig_evolucao, use_container_width=True)

# === TELA 3: Análise de Oportunidades ===
with tab_oportunidades:
    st.markdown("### Ranking de Países por Índice de Potencial de Mercado (IPM)")

    top10_ipm = ranking.head(10)

    fig_ipm = px.bar(
        top10_ipm,
        x="IPM",
        y="NO_PAIS",
        orientation="h",
        title=f"Top 10 Países por IPM — NCM {ncm_escolhido}",
        labels={"IPM": "IPM (0 a 100)", "NO_PAIS": "País"},
        text="IPM"
    )
    fig_ipm.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_ipm.update_traces(texttemplate="%{text:.1f}", textposition="outside")

    st.plotly_chart(fig_ipm, use_container_width=True)

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