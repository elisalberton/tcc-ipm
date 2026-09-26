import pandas as pd
import plotly.express as px

ranking = pd.read_csv("dados_brutos/ranking_ipm.csv", sep=";")

top10 = ranking.sort_values("IPM", ascending=False).head(10)

fig = px.bar(
    top10,
    x="IPM",
    y="NO_PAIS",
    orientation="h",  # barras horizontais, fica mais fácil de ler o nome dos países
    title="Top 10 Países por Índice de Potencial de Mercado (IPM)",
    labels={"IPM": "IPM (0 a 100)", "NO_PAIS": "País"},
    text="IPM"  # mostra o valor do IPM ao lado de cada barra
)

# Inverte a ordem do eixo Y, pra o país com maior IPM ficar no topo do gráfico
fig.update_layout(yaxis={"categoryorder": "total ascending"})

# Formata o número mostrado em cada barra (arredondado, sem casas decimais demais)
fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")

fig.write_html("dados_brutos/grafico_top10_ipm.html")
print("Gráfico salvo em dados_brutos/grafico_top10_ipm.html — abra esse arquivo manualmente no navegador.")

# === Segundo gráfico: evolução das exportações ao longo dos anos ===

resumo = pd.read_csv("dados_brutos/resumo_pais_ano.csv", sep=";")

# Pega a lista dos 5 países com maior IPM, pra não poluir o gráfico com 162 linhas
top5_paises = ranking.sort_values("IPM", ascending=False).head(5)["NO_PAIS"].tolist()

resumo_top5 = resumo[resumo["NO_PAIS"].isin(top5_paises)]

fig2 = px.line(
    resumo_top5,
    x="CO_ANO",
    y="valor_exportado_usd",
    color="NO_PAIS",  # uma linha colorida por país
    title="Evolução das Exportações — Top 5 Países por IPM (2021-2025)",
    labels={"CO_ANO": "Ano", "valor_exportado_usd": "Valor Exportado (US$)", "NO_PAIS": "País"},
    markers=True  # mostra um pontinho em cada ano, facilita leitura
)

fig2.write_html("dados_brutos/grafico_evolucao_top5.html")
print("Gráfico de evolução salvo em dados_brutos/grafico_evolucao_top5.html")