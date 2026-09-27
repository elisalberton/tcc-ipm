import pandas as pd

indicadores = pd.read_csv("dados_brutos/indicadores.csv", sep=";")

# Filtro de volume mínimo RELATIVO: cada país precisa ter pelo menos 10% do volume
# do maior exportador DAQUELE MESMO NCM, evitando que um limite fixo beneficie
# ou prejudique NCMs com escalas de mercado muito diferentes entre si
PERCENTUAL_MINIMO = 0.10
indicadores["volume_maximo_do_ncm"] = indicadores.groupby("CO_NCM")["volume_medio_usd"].transform("max")
indicadores = indicadores[
    indicadores["volume_medio_usd"] >= indicadores["volume_maximo_do_ncm"] * PERCENTUAL_MINIMO
].copy()

# Remove combinações sem crescimento ou estabilidade calculáveis (só 1 ano de dado)
indicadores = indicadores.dropna(subset=["crescimento_pct", "coef_variacao"]).copy()

print(f"Combinações NCM/país após filtro de volume mínimo relativo (>= {PERCENTUAL_MINIMO:.0%} do maior exportador de cada NCM): {len(indicadores)}")

# Tratamento de outliers: o teto de crescimento agora é calculado
# SEPARADAMENTE para cada NCM (transform aplica o cálculo dentro de cada grupo)
indicadores["teto_crescimento"] = indicadores.groupby("CO_NCM")["crescimento_pct"].transform(
    lambda x: x.quantile(0.90)
)
indicadores["crescimento_pct_ajustado"] = indicadores[["crescimento_pct", "teto_crescimento"]].min(axis=1)

# Função de normalização min-max (0 a 100), aplicada DENTRO de cada grupo de NCM
def normalizar_por_grupo(df, coluna, inverter=False):
    minimo = df.groupby("CO_NCM")[coluna].transform("min")
    maximo = df.groupby("CO_NCM")[coluna].transform("max")
    normalizado = (df[coluna] - minimo) / (maximo - minimo) * 100
    if inverter:
        normalizado = 100 - normalizado
    return normalizado

indicadores["score_crescimento"] = normalizar_por_grupo(indicadores, "crescimento_pct_ajustado")
indicadores["score_volume"] = normalizar_por_grupo(indicadores, "volume_medio_usd")
indicadores["score_estabilidade"] = normalizar_por_grupo(indicadores, "coef_variacao", inverter=True)

# Pesos: crescimento e volume têm peso maior, estabilidade menor
PESO_CRESCIMENTO = 0.15
PESO_VOLUME = 0.65
PESO_ESTABILIDADE = 0.20

indicadores["IPM"] = (
    indicadores["score_crescimento"] * PESO_CRESCIMENTO +
    indicadores["score_volume"] * PESO_VOLUME +
    indicadores["score_estabilidade"] * PESO_ESTABILIDADE
)

# Ranking final, agrupado por NCM e ordenado por IPM decrescente dentro de cada grupo
ranking = indicadores.sort_values(["CO_NCM", "IPM"], ascending=[True, False])

print("\n=== Top 5 por NCM ===")
for ncm in ranking["CO_NCM"].unique():
    print(f"\n--- NCM {ncm} ---")
    print(ranking[ranking["CO_NCM"] == ncm][["NO_PAIS", "score_crescimento", "score_volume", "score_estabilidade", "IPM"]].head(5))

ranking.to_csv("dados_processados/ranking_ipm.csv", index=False, sep=";")
print("\nArquivo 'ranking_ipm.csv' salvo com sucesso em dados_processados/!")