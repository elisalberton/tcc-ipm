import pandas as pd

indicadores = pd.read_csv("dados_brutos/indicadores.csv", sep=";")

# Filtro de volume mínimo: remove países com exportação muito baixa,
# que distorcem o indicador de estabilidade (ex: Vanuatu com US$ 39 de volume médio)
VOLUME_MINIMO = 500000  # US$ 500 mil - ajustado após validação: filtro anterior deixava passar países irrelevantes
indicadores = indicadores[indicadores["volume_medio_usd"] >= VOLUME_MINIMO].copy()

print(f"Países após filtro de volume mínimo (>= US$ {VOLUME_MINIMO}): {len(indicadores)}")
print("\n=== Conferindo os valores brutos de crescimento (sem normalizar) ===")
print(indicadores[["NO_PAIS", "crescimento_pct"]].sort_values("crescimento_pct", ascending=False).head(10))

# Função de normalização min-max (0 a 100)
def normalizar(coluna, inverter=False):
    minimo = coluna.min()
    maximo = coluna.max()
    normalizado = (coluna - minimo) / (maximo - minimo) * 100
    if inverter:
        # Pra estabilidade, MENOR coef_variacao = MELHOR, então invertemos a escala
        normalizado = 100 - normalizado
    return normalizado

# Alguns países não têm crescimento_pct calculado (só 1 ano de dados) - removemos
indicadores = indicadores.dropna(subset=["crescimento_pct", "coef_variacao"]).copy()
# Tratamento de outliers: limita o crescimento_pct a um teto (percentil 90)
# Isso evita que um caso isolado (ex: país com base de comparação muito pequena)
# distorça toda a escala de normalização
teto_crescimento = indicadores["crescimento_pct"].quantile(0.90)
print(f"\nTeto de crescimento aplicado (percentil 90): {teto_crescimento:.2f}%")

indicadores["crescimento_pct_ajustado"] = indicadores["crescimento_pct"].clip(upper=teto_crescimento)

indicadores["score_crescimento"] = normalizar(indicadores["crescimento_pct_ajustado"])
indicadores["score_volume"] = normalizar(indicadores["volume_medio_usd"])
indicadores["score_estabilidade"] = normalizar(indicadores["coef_variacao"], inverter=True)

# Pesos: crescimento e volume têm peso maior, estabilidade menor
# (essa distribuição pode - e deve - ser justificada no TCC com base na literatura)
PESO_CRESCIMENTO = 0.15
PESO_VOLUME = 0.65
PESO_ESTABILIDADE = 0.20

indicadores["IPM"] = (
    indicadores["score_crescimento"] * PESO_CRESCIMENTO +
    indicadores["score_volume"] * PESO_VOLUME +
    indicadores["score_estabilidade"] * PESO_ESTABILIDADE
)

# Ranking final, do maior IPM pro menor
ranking = indicadores.sort_values("IPM", ascending=False)

print("\n=== Top 15 países por IPM ===")
print(ranking[["NO_PAIS", "score_crescimento", "score_volume", "score_estabilidade", "IPM"]].head(15))

ranking.to_csv("dados_brutos/ranking_ipm.csv", index=False, sep=";")
print("\nArquivo 'ranking_ipm.csv' salvo com sucesso!")