import pandas as pd

exp_2025 = pd.read_csv("dados_brutos/EXP_2025.csv", sep=";", nrows=5)
print("=== Colunas do arquivo de Exportação ===")
print(exp_2025.columns.tolist())
print(exp_2025)

ncm = pd.read_csv("dados_brutos/NCM.csv", sep=";", nrows=5, encoding="latin1")
print("\n=== Colunas da tabela NCM ===")
print(ncm.columns.tolist())
print(ncm)

pais = pd.read_csv("dados_brutos/PAIS.csv", sep=";", nrows=5, encoding="latin1")
print("\n=== Colunas da tabela PAIS ===")
print(pais.columns.tolist())
print(pais)