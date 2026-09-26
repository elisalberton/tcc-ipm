import pandas as pd

dados = pd.read_csv("dados_brutos/dados_limpos.csv", sep=";")

paises_investigar = ["Dinamarca", "Rússia"]

for pais in paises_investigar:
    print(f"\n{'='*50}")
    print(f"=== {pais} — todas as transações por ano/mês ===")
    print(f"{'='*50}")

    dados_pais = dados[dados["NO_PAIS"] == pais]

    resumo_mensal = dados_pais.groupby(["CO_ANO", "CO_MES"]).agg(
        valor_usd=("VL_FOB", "sum"),
        peso_kg=("KG_LIQUIDO", "sum"),
        qtd_transacoes=("VL_FOB", "count")
    ).reset_index()

    print(resumo_mensal.to_string(index=False))

    print(f"\nTotal de transações para {pais}: {len(dados_pais)}")