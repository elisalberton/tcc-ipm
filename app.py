import pandas as pd
import plotly.express as px
import streamlit as st

def formatar_moeda(valor):
    """Formata um número no padrão brasileiro: ponto para milhar, vírgula para decimal."""
    texto = f"{valor:,.0f}"
    return "US$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_moeda_curta(valor):
    """Formata valores grandes de forma abreviada (mil, mi, bi), no padrão brasileiro."""
    if valor >= 1_000_000_000:
        numero = formatar_numero(valor / 1_000_000_000, 1)
        return f"US$ {numero} bi"
    elif valor >= 1_000_000:
        numero = formatar_numero(valor / 1_000_000, 1)
        return f"US$ {numero} mi"
    elif valor >= 1_000:
        numero = formatar_numero(valor / 1_000, 1)
        return f"US$ {numero} mil"
    else:
        return formatar_moeda(valor)


def formatar_numero(valor, casas=1):
    """Formata um número decimal no padrão brasileiro (vírgula)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

st.title("Sistema de Inteligência Comercial")
st.subheader("Análise de Oportunidades de Exportação — Embalagens Plásticas Flexíveis")

# Carrega os dados
ranking_completo = pd.read_csv("dados_processados/ranking_ipm.csv", sep=";")
resumo_completo = pd.read_csv("dados_processados/resumo_pais_ano.csv", sep=";")

# === TELA 1: Seleção do produto (NCM) — barra lateral
opcoes_ncm = ranking_completo[["CO_NCM", "NO_NCM_POR"]].drop_duplicates().sort_values("CO_NCM")
opcoes_ncm["rotulo"] = opcoes_ncm["CO_NCM"].astype(str) + " — " + opcoes_ncm["NO_NCM_POR"]

st.sidebar.header("Seleção do Produto")
rotulo_escolhido = st.sidebar.selectbox(
    "Escolha o NCM a ser analisado:",
    opcoes_ncm["rotulo"]
)
ncm_escolhido = opcoes_ncm[opcoes_ncm["rotulo"] == rotulo_escolhido]["CO_NCM"].iloc[0]
st.sidebar.markdown("---")
st.sidebar.markdown("**Contexto da análise**")
st.sidebar.markdown(f"Produto: `{ncm_escolhido}`")
st.sidebar.markdown("Período: 2021-2025")
st.sidebar.markdown("Fonte: MDIC / Comex Stat")

with st.expander("Como o IPM é calculado?"):
    st.markdown(
        """
O **Índice de Potencial de Mercado (IPM)** combina três indicadores de comércio exterior em uma pontuação única, de 0 a 100, calculada separadamente para cada produto (NCM):

- **Volume médio (peso 65%)** — média do valor exportado pelo Brasil para o país, nos anos com dados disponíveis.
- **Crescimento (peso 15%)** — variação percentual entre o primeiro e o último ano com registro. Valores muito altos são limitados ao percentil 90 do NCM, para que casos isolados não distorçam a comparação.
- **Estabilidade (peso 20%)** — quanto menos o valor exportado varia de um ano para o outro, maior a pontuação.

$$
IPM = 0{,}15 \\times \\text{Crescimento} + 0{,}65 \\times \\text{Volume} + 0{,}20 \\times \\text{Estabilidade}
$$

Cada indicador é normalizado dentro do próprio NCM (o melhor valor do produto vira 100, o pior vira 0), então **pontuações de NCMs diferentes não são comparáveis entre si**.

Só entram no ranking os países com volume médio de pelo menos 10% do maior exportador daquele NCM — por isso o número de países varia conforme o produto selecionado.

O IPM classifica mercados; ele não substitui a análise do profissional de comércio exterior sobre tarifas, barreiras comerciais ou participação de mercado, informações que não fazem parte deste modelo.
        """
    )

# Filtra o ranking só pro NCM escolhido
ranking = ranking_completo[ranking_completo["CO_NCM"] == ncm_escolhido].copy()
ranking = ranking.sort_values("IPM", ascending=False)

st.sidebar.markdown(f"Países no ranking: {len(ranking)}")

resumo = resumo_completo[resumo_completo["CO_NCM"] == ncm_escolhido].copy()

# Abas do sistema
tab_visao_global, tab_oportunidades, tab_analise_pais, tab_recomendacao = st.tabs(
    ["Visão Global", "Análise de Oportunidades", "Análise por País", "Mercado em Destaque"]
)

# === TELA 2: Visão Global ===
with tab_visao_global:
    st.metric("Mercados no ranking", len(ranking))
    st.caption("Países que atendem ao critério de relevância do IPM para este NCM.")
    st.markdown("---")
    st.markdown("### Principais Países de Destino (por Volume Médio Exportado)")

    top10_volume = ranking.sort_values("volume_medio_usd", ascending=False).head(10)
    st.caption(
        "Considera os países que atendem ao critério de relevância do IPM (volume médio de pelo "
        f"menos 10% do maior destino do NCM selecionado). Para este NCM: {len(ranking)} países."
    )

    fig_top10 = px.bar(
        top10_volume,
        x="volume_medio_usd",
        y="NO_PAIS",
        orientation="h",
        title="Principais mercados por volume médio exportado",
        labels={"volume_medio_usd": "Volume Médio Exportado (US$)", "NO_PAIS": "País"},
        text="volume_medio_usd",
        color_discrete_sequence=["#2F6690"]
    )

    fig_top10.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_top10.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_top10.update_layout(separators=",.")
    
    st.caption(f"NCM {ncm_escolhido} · 2021-2025")

    st.plotly_chart(fig_top10, use_container_width=True)

    st.markdown("### Evolução das Exportações — Principais Destinos (2021-2025)")

    top5_paises = top10_volume.head(5)["NO_PAIS"].tolist()
    resumo_top5 = resumo[resumo["NO_PAIS"].isin(top5_paises)]

    fig_evolucao = px.line(
        resumo_top5,
        x="CO_ANO",
        y="valor_exportado_usd",
        color="NO_PAIS",
        title=f"Principais Destinos — NCM {ncm_escolhido}",
        labels={"CO_ANO": "Ano", "valor_exportado_usd": "Valor Exportado (US$)", "NO_PAIS": "País"},
        markers=True
    )

    fig_evolucao.update_layout(separators=",.")
    st.plotly_chart(fig_evolucao, use_container_width=True)

# === TELA 3: Análise de Oportunidades ===
with tab_oportunidades:
    pesos_tabela = pd.DataFrame({
        "Indicador": ["Volume médio", "Estabilidade", "Crescimento"],
        "Peso": ["65%", "20%", "15%"]
    })
    st.markdown("**Composição do IPM**")
    st.dataframe(pesos_tabela, use_container_width=True, hide_index=True)
    st.markdown("---")

    st.markdown("### Ranking de Países por Índice de Potencial de Mercado (IPM)")

    top10_ipm = ranking.head(10)

    fig_ipm = px.bar(
        top10_ipm,
        x="IPM",
        y="NO_PAIS",
        orientation="h",
        title="Priorização de mercados por Índice de Potencial de Mercado (IPM)",
        labels={"IPM": "IPM (0 a 100)", "NO_PAIS": "País"},
        text="IPM",
        color_discrete_sequence=["#3A8D5D"]
    )

    fig_ipm.update_layout(yaxis={"categoryorder": "total ascending"})
    fig_ipm.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_ipm.update_layout(separators=",.")

    st.caption(f"NCM {ncm_escolhido} · 2021-2025")

    st.plotly_chart(fig_ipm, use_container_width=True)

    st.markdown("### Tabela Detalhada")

    ranking_com_posicao = ranking.copy()
    ranking_com_posicao.insert(0, "Posição", range(1, len(ranking_com_posicao) + 1))

    tabela_formatada = ranking_com_posicao[["Posição", "NO_PAIS", "volume_medio_usd", "crescimento_pct", "coef_variacao", "IPM"]].copy()
    tabela_formatada["volume_medio_usd"] = tabela_formatada["volume_medio_usd"].apply(formatar_moeda)
    tabela_formatada["crescimento_pct"] = tabela_formatada["crescimento_pct"].apply(lambda x: formatar_numero(x, 1) + "%")
    tabela_formatada["coef_variacao"] = tabela_formatada["coef_variacao"].apply(lambda x: formatar_numero(x, 2))
    tabela_formatada["IPM"] = tabela_formatada["IPM"].apply(lambda x: formatar_numero(x, 1))

    st.dataframe(
        tabela_formatada.rename(columns={
            "Posição": "Posição",
            "NO_PAIS": "País",
            "volume_medio_usd": "Volume Médio",
            "crescimento_pct": "Crescimento",
            "coef_variacao": "Estabilidade (CV)",
            "IPM": "IPM"
        }),
        use_container_width=True,
        hide_index=True
    )
    st.caption("Quanto menor o CV (coeficiente de variação), maior a estabilidade relativa dos fluxos de exportação.")

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
    col1.metric("IPM", formatar_numero(dados_pais["IPM"], 1))
    col2.metric("Volume Médio", formatar_moeda_curta(dados_pais["volume_medio_usd"]))
    col3.metric("Crescimento", formatar_numero(dados_pais["crescimento_pct"], 1) + "%")
    col4.metric("Coef. Variação", formatar_numero(dados_pais["coef_variacao"], 2))

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
    
    fig_pais.update_layout(separators=",.")
    st.plotly_chart(fig_pais, use_container_width=True)

    # === TELA 5: Recomendação Automática ===
# === TELA 5: Mercado em Destaque ===
with tab_recomendacao:
    st.markdown("### Mercado com Maior Índice de Potencial de Mercado (IPM)")

    pais_destaque = ranking.sort_values("IPM", ascending=False).iloc[0]

    nome_pais = pais_destaque["NO_PAIS"]
    ipm_valor = pais_destaque["IPM"]
    crescimento = pais_destaque["crescimento_pct"]
    volume = pais_destaque["volume_medio_usd"]
    estabilidade = pais_destaque["coef_variacao"]

    if crescimento > 30:
        texto_crescimento = "crescimento expressivo"
    elif crescimento > 0:
        texto_crescimento = "crescimento moderado"
    else:
        texto_crescimento = "retração"

    if estabilidade < 0.15:
        texto_estabilidade = "alta estabilidade"
    elif estabilidade < 0.30:
        texto_estabilidade = "estabilidade moderada"
    else:
        texto_estabilidade = "volatilidade considerável"

    destaque = (
        f"**{nome_pais}** apresentou o maior Índice de Potencial de Mercado (IPM = {formatar_numero(ipm_valor, 1)}) "
        f"entre os países analisados para o NCM {ncm_escolhido}, segundo os critérios e pesos definidos "
        f"no modelo. O fluxo de exportações brasileiras para esse país exibiu {texto_crescimento} "
        f"ao longo do período disponível ({formatar_numero(crescimento, 1)}%), volume médio de aproximadamente "
        f"{formatar_moeda(volume)} por ano, e {texto_estabilidade} nas exportações observadas "
        f"(coeficiente de variação de {formatar_numero(estabilidade, 2)})."
    )

    st.info(destaque)

    ranking_ordenado = ranking.sort_values("IPM", ascending=False)
    LIMIAR_PROXIMIDADE = 2.0   # diferença mínima em IPM entre o 1º e o 2º no rankink
    MIN_PAISES = 5             # mínimo de países p ter referencia

    if len(ranking_ordenado) >= 2:
        segundo_colocado = ranking_ordenado.iloc[1]
        diferenca = ipm_valor - segundo_colocado["IPM"]
        if diferenca < LIMIAR_PROXIMIDADE:
            st.warning(
                f"Atenção: a diferença entre o 1º colocado ({nome_pais}) e o 2º colocado "
                f"({segundo_colocado['NO_PAIS']}) é de apenas {formatar_numero(diferenca, 1)} ponto(s) de IPM. "
                "Em testes com pesos e parâmetros alternativos, a ordem entre mercados com "
                "pontuações tão próximas pode se inverter. Interprete-os como mercados de "
                "potencial semelhante, e não como uma hierarquia definitiva."
            )

    if len(ranking_ordenado) < MIN_PAISES:
        st.warning(
            f"Atenção: apenas {len(ranking_ordenado)} países atendem aos critérios de relevância "
            "para este NCM. Com poucos mercados, a normalização do IPM (escala de 0 a 100 entre "
            "o menor e o maior valor) tende a exagerar diferenças pequenas, devendo o ranking ser interpretado com maior cautela."
        )

    st.markdown("#### Outros mercados nas primeiras posições")
    proximos = ranking.sort_values("IPM", ascending=False).iloc[1:4]

    for _, linha in proximos.iterrows():
        st.write(
            f"- **{linha['NO_PAIS']}** (IPM = {formatar_numero(linha['IPM'], 1)}): "
            f"crescimento de {formatar_numero(linha['crescimento_pct'], 1)}%, "
            f"volume médio de {formatar_moeda(linha['volume_medio_usd'])}"
        )

    st.caption(
        "O IPM prioriza os mercados analisados segundo os critérios e pesos definidos no modelo, "
        "com base exclusivamente em dados de exportações brasileiras. Não representa uma medida de "
        "demanda do mercado importador, participação de mercado, condições tarifárias ou barreiras "
        "comerciais específicas de cada país, devendo ser interpretado como instrumento de apoio "
        "à análise e à tomada de decisão."
    )