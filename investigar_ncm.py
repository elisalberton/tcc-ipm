import pandas as pd

indicadores = pd.read_csv("dados_brutos/indicadores.csv", sep=";")

# Filtra só o NCM 3923.21.10 (sem código de país, sem NCM), olhando TODOS os países,
# antes de qualquer filtro de volume mínimo ou de remoção de NaN
ncm_39232110 = indicadores[indicadores["CO_NCM"] == 39232110]

print("=== Todos os países com dados para o NCM 39232110 (sem filtro) ===")
print(ncm_39232110[["NO_PAIS", "ano_inicial", "ano_final", "volume_medio_usd", "crescimento_pct", "coef_variacao"]].sort_values("volume_medio_usd", ascending=False))