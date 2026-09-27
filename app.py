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

# Abas do sistema
tab_visao_global, tab_oportunidades, tab_analise_pais, tab_recomendacao = st.tabs(
    ["Visão Global", "Análise de Oportunidades", "Análise por País", "Recomendação"]
)

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

    # === TELA 4: Análise por País ===
with tab_analise_pais:
    st.markdown("### Análise Detalhada por País")

    lista_paises = ranking.sort_values("NO_PAIS")["NO_PAIS"].tolist()
    pais_escolhido = st.selectbox("Escolha um país para analisar:", lista_paises)

    # Dados do país escolhido dentro do ranking do NCM selecionado
    dados_pais = ranking[ranking["NO_PAIS"] == pais_escolhido].iloc[0]

    ranking_ordenado = ranking.sort_values("IPM", ascending=False).reset_index(drop=True)
    posicao = ranking_ordenado[ranking_ordenado["NO_PAIS"] == pais_escolhido].index[0] + 1
    total_paises = len(ranking_ordenado)

    st.markdown(f"**Posição no ranking:** {posicao}º de {total_paises} países analisados para este NCM")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("IPM", f"{dados_pais['IPM']:.1f}")
    col2.metric("Volume Médio (US$)", f"{dados_pais['volume_medio_usd']:,.0f}")
    col3.metric("Crescimento (%)", f"{dados_pais['crescimento_pct']:.1f}%")
    col4.metric("Coef. Variação", f"{dados_pais['coef_variacao']:.2f}")

    st.markdown(f"### Evolução das Exportações Brasileiras para {pais_escolhido}")

    resumo_pais = resumo[resumo["NO_PAIS"] == pais_escolhido].sort_values("CO_ANO")

    fig_pais = px.line(
        resumo_pais,
        x="CO_ANO",
        y="valor_exportado_usd",
        title=f"Exportações Brasileiras para {pais_escolhido} — NCM {ncm_escolhido}",
        labels={"CO_ANO": "Ano", "valor_exportado_usd": "Valor Exportado (US$)"},
        markers=True
    )

    st.plotly_chart(fig_pais, use_container_width=True)

    # === TELA 5: Recomendação Automática ===
with tab_recomendacao:
    st.markdown("### Recomendação de Mercado Prioritário")

    melhor_pais = ranking.sort_values("IPM", ascending=False).iloc[0]

    nome_pais = melhor_pais["NO_PAIS"]
    ipm_valor = melhor_pais["IPM"]
    crescimento = melhor_pais["crescimento_pct"]
    volume = melhor_pais["volume_medio_usd"]
    estabilidade = melhor_pais["coef_variacao"]

    # Classifica o crescimento em texto, por faixa
    if crescimento > 30:
        texto_crescimento = "crescimento expressivo"
    elif crescimento > 0:
        texto_crescimento = "crescimento moderado"
    else:
        texto_crescimento = "retração"

    # Classifica a estabilidade em texto (coef_variacao menor = mais estável)
    if estabilidade < 0.15:
        texto_estabilidade = "alta estabilidade"
    elif estabilidade < 0.30:
        texto_estabilidade = "estabilidade moderada"
    else:
        texto_estabilidade = "volatilidade considerável"

    recomendacao = (
        f"**{nome_pais}** apresenta o maior Índice de Potencial de Mercado (IPM = {ipm_valor:.1f}) "
        f"entre os países analisados para o NCM {ncm_escolhido}. O mercado exibe {texto_crescimento} "
        f"nas exportações brasileiras ao longo do período analisado ({crescimento:.1f}%), "
        f"volume médio exportado de aproximadamente US$ {volume:,.0f} por ano, e {texto_estabilidade} "
        f"na demanda observada (coeficiente de variação de {estabilidade:.2f})."
    )

    st.info(recomendacao)

    st.markdown("#### Demais mercados em destaque")
    proximos = ranking.sort_values("IPM", ascending=False).iloc[1:4]

    for _, linha in proximos.iterrows():
        st.write(
            f"- **{linha['NO_PAIS']}** (IPM = {linha['IPM']:.1f}): "
            f"crescimento de {linha['crescimento_pct']:.1f}%, "
            f"volume médio de US$ {linha['volume_medio_usd']:,.0f}"
        )

    st.caption(
        "Esta recomendação é gerada automaticamente a partir de regras de negócio aplicadas "
        "aos indicadores calculados pelo sistema, com base exclusivamente em dados de exportações "
        "brasileiras. Não considera participação de mercado, condições tarifárias ou barreiras "
        "comerciais específicas de cada país, devendo ser interpretada como apoio à decisão, "
        "não como recomendação definitiva."
    )