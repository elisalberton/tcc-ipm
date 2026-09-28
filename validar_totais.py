import pandas as pd

print("=== 1. Arquivo oficial de conferência ===")
oficial = pd.read_csv("dados_brutos/EXP_TOTAIS_CONFERENCIA.csv", sep=";", encoding="latin1")
print("Colunas:", oficial.columns.tolist())
print("Linhas:", len(oficial))
print(oficial.head(40).to_string(index=False))

print("\n=== 2. Totais dos arquivos brutos que você baixou ===")
print("Ano | Linhas | VL_FOB total (US$) | KG_LIQUIDO total")
for ano in [2021, 2022, 2023, 2024, 2025]:
    df = pd.read_csv(f"dados_brutos/EXP_{ano}.csv", sep=";", usecols=["VL_FOB", "KG_LIQUIDO"])
    print(f"{ano} | {len(df)} | {df['VL_FOB'].sum()} | {df['KG_LIQUIDO'].sum()}")

print("\n=== 3. Total FOB do recorte (3 NCMs), por ano e NCM ===")
limpos = pd.read_csv("dados_brutos/dados_limpos.csv", sep=";")
print(limpos.groupby(["CO_ANO", "CO_NCM"])["VL_FOB"].sum().unstack())