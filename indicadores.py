import pandas as pd

resumo = pd.read_csv("dados_processados/resumo_pais_ano.csv", sep=";")

# Pra cada país e NCM, pega o primeiro e o último ano q tem registro
primeiro_ano = resumo.groupby(["CO_NCM", "NO_PAIS"])["CO_ANO"].min().rename("ano_inicial")
ultimo_ano = resumo.groupby(["CO_NCM", "NO_PAIS"])["CO_ANO"].max().rename("ano_final")

info_anos = pd.concat([primeiro_ano, ultimo_ano], axis=1).reset_index()

# Busca o valor exportado no ano inicial e no ano final de cada país/NCM
valor_inicial = resumo.merge(
    info_anos[["CO_NCM", "NO_PAIS", "ano_inicial"]],
    left_on=["CO_NCM", "NO_PAIS", "CO_ANO"],
    right_on=["CO_NCM", "NO_PAIS", "ano_inicial"]
)[["CO_NCM", "NO_PAIS", "valor_exportado_usd"]].rename(columns={"valor_exportado_usd": "valor_inicial"})

valor_final = resumo.merge(
    info_anos[["CO_NCM", "NO_PAIS", "ano_final"]],
    left_on=["CO_NCM", "NO_PAIS", "CO_ANO"],
    right_on=["CO_NCM", "NO_PAIS", "ano_final"]
)[["CO_NCM", "NO_PAIS", "valor_exportado_usd"]].rename(columns={"valor_exportado_usd": "valor_final"})

# uma tabela só
indicadores = valor_inicial.merge(valor_final, on=["CO_NCM", "NO_PAIS"])
indicadores = indicadores.merge(info_anos, on=["CO_NCM", "NO_PAIS"])

# Indicador de VOLUME: média do valor exportado por NCM/país
volume_medio = resumo.groupby(["CO_NCM", "NO_PAIS"])["valor_exportado_usd"].mean().rename("volume_medio_usd")
indicadores = indicadores.merge(volume_medio, on=["CO_NCM", "NO_PAIS"])

# Indicador de CRESCIMENTO: variação % entre valor inicial e final
indicadores["crescimento_pct"] = (
    (indicadores["valor_final"] - indicadores["valor_inicial"]) / indicadores["valor_inicial"]
) * 100
indicadores.loc[indicadores["ano_inicial"] == indicadores["ano_final"], "crescimento_pct"] = None

# Indicador de ESTABILIDADE: coeficiente de variação (desvio padrão / média)
desvio_padrao = resumo.groupby(["CO_NCM", "NO_PAIS"])["valor_exportado_usd"].std().rename("desvio_padrao_usd")
indicadores = indicadores.merge(desvio_padrao, on=["CO_NCM", "NO_PAIS"])
indicadores["coef_variacao"] = indicadores["desvio_padrao_usd"] / indicadores["volume_medio_usd"]

# traz de volta a descrição do ncm
descricao_ncm = resumo[["CO_NCM", "NO_NCM_POR"]].drop_duplicates()
indicadores = indicadores.merge(descricao_ncm, on="CO_NCM")

print("=== Indicadores por NCM e país ===")
print(indicadores.sort_values("volume_medio_usd", ascending=False).head(15))

print(f"\nTotal de combinações NCM/país com indicadores calculados: {len(indicadores)}")

# Base do calcular_ipm.py
indicadores.to_csv("dados_processados/indicadores.csv", index=False, sep=";")
print("\nArquivo 'indicadores.csv' salvo com sucesso!")