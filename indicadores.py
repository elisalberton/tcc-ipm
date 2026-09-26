import pandas as pd

resumo = pd.read_csv("dados_brutos/resumo_pais_ano.csv", sep=";")

# Pra cada país, vamos pegar o primeiro e o último ano em que ele aparece
# (nem todo país tem os 5 anos completos, então usamos o que existir)
primeiro_ano = resumo.groupby("NO_PAIS")["CO_ANO"].min().rename("ano_inicial")
ultimo_ano = resumo.groupby("NO_PAIS")["CO_ANO"].max().rename("ano_final")

# Junta essas informações numa tabela auxiliar, por país
info_anos = pd.concat([primeiro_ano, ultimo_ano], axis=1).reset_index()

# Agora buscamos o valor exportado no ano inicial e no ano final, pra cada país
valor_inicial = resumo.merge(
    info_anos[["NO_PAIS", "ano_inicial"]],
    left_on=["NO_PAIS", "CO_ANO"],
    right_on=["NO_PAIS", "ano_inicial"]
)[["NO_PAIS", "valor_exportado_usd"]].rename(columns={"valor_exportado_usd": "valor_inicial"})

valor_final = resumo.merge(
    info_anos[["NO_PAIS", "ano_final"]],
    left_on=["NO_PAIS", "CO_ANO"],
    right_on=["NO_PAIS", "ano_final"]
)[["NO_PAIS", "valor_exportado_usd"]].rename(columns={"valor_exportado_usd": "valor_final"})

# Junta tudo numa tabela só
indicadores = valor_inicial.merge(valor_final, on="NO_PAIS")
indicadores = indicadores.merge(info_anos, on="NO_PAIS")

# Indicador de VOLUME: média do valor exportado nos anos disponíveis, por país
volume_medio = resumo.groupby("NO_PAIS")["valor_exportado_usd"].mean().rename("volume_medio_usd")
indicadores = indicadores.merge(volume_medio, on="NO_PAIS")

# Indicador de CRESCIMENTO: variação percentual entre o valor inicial e o final
# Só calculamos crescimento se o país tiver pelo menos 2 anos diferentes (ano_inicial != ano_final)
indicadores["crescimento_pct"] = (
    (indicadores["valor_final"] - indicadores["valor_inicial"]) / indicadores["valor_inicial"]
) * 100

# Países que só aparecem em 1 ano não têm como calcular crescimento (fica em branco/NaN)
indicadores.loc[indicadores["ano_inicial"] == indicadores["ano_final"], "crescimento_pct"] = None

# Indicador de ESTABILIDADE: coeficiente de variação (desvio padrão / média)
# Quanto MENOR o valor, mais estável é o mercado (oscila menos entre os anos)
desvio_padrao = resumo.groupby("NO_PAIS")["valor_exportado_usd"].std().rename("desvio_padrao_usd")
indicadores = indicadores.merge(desvio_padrao, on="NO_PAIS")

indicadores["coef_variacao"] = indicadores["desvio_padrao_usd"] / indicadores["volume_medio_usd"]

# Países com só 1 ano de dados não têm desvio padrão calculável (fica em branco/NaN)

print("=== Indicadores por país ===")
print(indicadores.sort_values("volume_medio_usd", ascending=False).head(15))

print("\n=== Conferindo só as colunas de estabilidade ===")
print(indicadores[["NO_PAIS", "volume_medio_usd", "desvio_padrao_usd", "coef_variacao"]].sort_values("coef_variacao").head(10))

print(f"\nTotal de países com indicadores calculados: {len(indicadores)}")

indicadores.to_csv("dados_brutos/indicadores.csv", index=False, sep=";")
print("\nArquivo 'indicadores.csv' salvo com sucesso!")