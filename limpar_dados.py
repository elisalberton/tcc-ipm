import pandas as pd

ncms_interesse = ["39201099", "39232190", "39232110"]

anos = [2021, 2022, 2023, 2024, 2025]

tabelas_filtradas = []

for ano in anos:
    print(f"Lendo o arquivo do ano {ano}...")
    df_ano = pd.read_csv(f"dados_brutos/EXP_{ano}.csv", sep=";")

    # Filtra só as linhas dos CO_NCM escolhidos
    # Converter p texto pra comparar
    df_ano_filtrado = df_ano[df_ano["CO_NCM"].astype(str).isin(ncms_interesse)]

    print(f"  → {len(df_ano_filtrado)} linhas encontradas em {ano}")
    tabelas_filtradas.append(df_ano_filtrado)

# junta os 5 anos na tabela
dados_exportacao = pd.concat(tabelas_filtradas, ignore_index=True)

print(f"\nTotal de linhas após juntar todos os anos: {len(dados_exportacao)}")

ncm_desc = pd.read_csv("dados_brutos/NCM.csv", sep=";", encoding="latin1")
pais_desc = pd.read_csv("dados_brutos/PAIS.csv", sep=";", encoding="latin1")

# merge os dados de exportação com a descrição do NCM
dados_exportacao = dados_exportacao.merge(
    ncm_desc[["CO_NCM", "NO_NCM_POR"]],
    on="CO_NCM",
    how="left"
)

# Cruza com o nome do país
dados_exportacao = dados_exportacao.merge(
    pais_desc[["CO_PAIS", "NO_PAIS"]],
    on="CO_PAIS",
    how="left"
)

print("\nAmostra dos dados finais:")
print(dados_exportacao.head(10))

dados_exportacao.to_csv("dados_brutos/dados_limpos.csv", index=False, sep=";")
print("\nArquivo 'dados_limpos.csv' salvo com sucesso!")