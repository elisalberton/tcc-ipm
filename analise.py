import pandas as pd

# Lê arquivo limpo
dados = pd.read_csv("dados_brutos/dados_limpos.csv", sep=";")

# Agrupa por país e ano, somando o valor exportado (VL_FOB) e o peso (KG_LIQUIDO)
resumo_por_pais_ano = dados.groupby(["NO_PAIS", "CO_ANO"]).agg(
    valor_exportado_usd=("VL_FOB", "sum"),
    peso_kg=("KG_LIQUIDO", "sum")
).reset_index()

print("=== Resumo agregado por país e ano ===")
print(resumo_por_pais_ano.head(20))

print(f"\nTotal de combinações país/ano: {len(resumo_por_pais_ano)}")
print(f"Total de países distintos: {resumo_por_pais_ano['NO_PAIS'].nunique()}")

# Salva esse resumo, base pro cálculo do IPM
resumo_por_pais_ano.to_csv("dados_brutos/resumo_pais_ano.csv", index=False, sep=";")
print("\nArquivo 'resumo_pais_ano.csv' salvo com sucesso!")