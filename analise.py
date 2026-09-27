import pandas as pd

# Lê o arquivo já limpo
dados = pd.read_csv("dados_brutos/dados_limpos.csv", sep=";")

# Agrupa por NCM, país e ano, somando o valor exportado (VL_FOB) e o peso (KG_LIQUIDO) - deixa os ncms separados
resumo_por_pais_ano = dados.groupby(["CO_NCM", "NO_NCM_POR", "NO_PAIS", "CO_ANO"]).agg(
    valor_exportado_usd=("VL_FOB", "sum"),
    peso_kg=("KG_LIQUIDO", "sum")
).reset_index()

print("=== Resumo agregado por NCM, país e ano ===")
print(resumo_por_pais_ano.head(20))

print(f"\nTotal de combinações NCM/país/ano: {len(resumo_por_pais_ano)}")
print(f"Total de países distintos: {resumo_por_pais_ano['NO_PAIS'].nunique()}")
print(f"NCMs presentes: {resumo_por_pais_ano['CO_NCM'].unique()}")

# base pro cálculo dos indicadores
resumo_por_pais_ano.to_csv("dados_processados/resumo_pais_ano.csv", index=False, sep=";")
print("\nArquivo 'resumo_pais_ano.csv' salvo com sucesso!")