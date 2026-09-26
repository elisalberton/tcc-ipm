import pandas as pd

# Os NCMs de interesse, sem pontos (formato usado no arquivo original)
ncms_interesse = ["39201099", "39232190", "39232110"]

anos = [2021, 2022, 2023, 2024, 2025]

# Lista vazia pra ir guardando o resultado filtrado de cada ano
tabelas_filtradas = []

for ano in anos:
    print(f"Lendo o arquivo do ano {ano}...")
    df_ano = pd.read_csv(f"dados_brutos/EXP_{ano}.csv", sep=";")

    # Filtra só as linhas cujo CO_NCM está na nossa lista de interesse
    # Precisamos converter CO_NCM pra texto (str) pra comparar com a lista acima
    df_ano_filtrado = df_ano[df_ano["CO_NCM"].astype(str).isin(ncms_interesse)]

    print(f"  → {len(df_ano_filtrado)} linhas encontradas em {ano}")
    tabelas_filtradas.append(df_ano_filtrado)

# Junta todos os anos filtrados em uma única tabela
dados_exportacao = pd.concat(tabelas_filtradas, ignore_index=True)

print(f"\nTotal de linhas após juntar todos os anos: {len(dados_exportacao)}")

# Agora vamos trazer a descrição do produto (NCM) e o nome do país
ncm_desc = pd.read_csv("dados_brutos/NCM.csv", sep=";", encoding="latin1")
pais_desc = pd.read_csv("dados_brutos/PAIS.csv", sep=";", encoding="latin1")

# Cruza (merge) os dados de exportação com a descrição do NCM
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

# Salva o resultado limpo, pra não precisar reprocessar tudo de novo
dados_exportacao.to_csv("dados_brutos/dados_limpos.csv", index=False, sep=";")
print("\nArquivo 'dados_limpos.csv' salvo com sucesso!")