import pandas as pd

indicadores_base = pd.read_csv("dados_brutos/indicadores.csv", sep=";")


def normalizar(df, coluna, inverter=False):
    minimo = df.groupby("CO_NCM")[coluna].transform("min")
    maximo = df.groupby("CO_NCM")[coluna].transform("max")
    score = (df[coluna] - minimo) / (maximo - minimo) * 100
    return 100 - score if inverter else score


def calcular_ipm(df, pesos, pct_min=0.10, perc_teto=0.90):
    """Replica a lógica do calcular_ipm.py, com parâmetros ajustáveis."""
    df = df.copy()

    volume_maximo = df.groupby("CO_NCM")["volume_medio_usd"].transform("max")
    df = df[df["volume_medio_usd"] >= volume_maximo * pct_min].copy()


    df = df.dropna(subset=["crescimento_pct", "coef_variacao"]).copy()

    # Teto de crescimento por NCM
    df["teto"] = df.groupby("CO_NCM")["crescimento_pct"].transform(
        lambda x: x.quantile(perc_teto)
    )
    df["crescimento_ajustado"] = df[["crescimento_pct", "teto"]].min(axis=1)

    # Normalização de cada NCM
    df["score_c"] = normalizar(df, "crescimento_ajustado")
    df["score_v"] = normalizar(df, "volume_medio_usd")
    df["score_e"] = normalizar(df, "coef_variacao", inverter=True)

    # 5. Ponderação crescimento, volume, estabilidade
    p_c, p_v, p_e = pesos
    df["IPM"] = p_c * df["score_c"] + p_v * df["score_v"] + p_e * df["score_e"]
    return df


cenarios = [
    {"nome": "BASE (0,15/0,65/0,20)", "pesos": (0.15, 0.65, 0.20), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Pesos 0,10/0,65/0,25", "pesos": (0.10, 0.65, 0.25), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Pesos 0,20/0,65/0,15", "pesos": (0.20, 0.65, 0.15), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Pesos 0,15/0,55/0,30", "pesos": (0.15, 0.55, 0.30), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Pesos 0,15/0,75/0,10", "pesos": (0.15, 0.75, 0.10), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Pesos 0,25/0,60/0,15", "pesos": (0.25, 0.60, 0.15), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Pesos 0,45/0,45/0,10", "pesos": (0.45, 0.45, 0.10), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Pesos iguais (1/3 cada)", "pesos": (1/3, 1/3, 1/3), "pct_min": 0.10, "perc_teto": 0.90},
    {"nome": "Filtro 5%", "pesos": (0.15, 0.65, 0.20), "pct_min": 0.05, "perc_teto": 0.90},
    {"nome": "Filtro 20%", "pesos": (0.15, 0.65, 0.20), "pct_min": 0.20, "perc_teto": 0.90},
    {"nome": "Teto P80", "pesos": (0.15, 0.65, 0.20), "pct_min": 0.10, "perc_teto": 0.80},
    {"nome": "Teto P95", "pesos": (0.15, 0.65, 0.20), "pct_min": 0.10, "perc_teto": 0.95},
    {"nome": "Sem teto", "pesos": (0.15, 0.65, 0.20), "pct_min": 0.10, "perc_teto": 1.00},
]

c0 = cenarios[0]
base = calcular_ipm(indicadores_base, c0["pesos"], c0["pct_min"], c0["perc_teto"])

oficial = pd.read_csv("dados_processados/ranking_ipm.csv", sep=";")
comp = base.merge(oficial[["CO_NCM", "NO_PAIS", "IPM"]], on=["CO_NCM", "NO_PAIS"],
                  suffixes=("_replica", "_oficial"))
print("=== Checagem da réplica do cenário base ===")
print(f"Linhas na réplica: {len(base)} | linhas no ranking oficial: {len(oficial)}")
print(f"Diferença máxima de IPM: {(comp['IPM_replica'] - comp['IPM_oficial']).abs().max():.6f}\n")

linhas = []
for c in cenarios:
    res = calcular_ipm(indicadores_base, c["pesos"], c["pct_min"], c["perc_teto"])
    for ncm in sorted(base["CO_NCM"].unique()):
        r = res[res["CO_NCM"] == ncm].set_index("NO_PAIS")["IPM"]
        b = base[base["CO_NCM"] == ncm].set_index("NO_PAIS")["IPM"]
        comuns = r.index.intersection(b.index)

        rho = b[comuns].rank().corr(r[comuns].rank()) if len(comuns) > 2 else float("nan")
        top3_r = r.sort_values(ascending=False).head(3).index.tolist()
        top3_b = b.sort_values(ascending=False).head(3).index.tolist()

        linhas.append({
            "cenario": c["nome"],
            "NCM": ncm,
            "n_paises": len(r),
            "primeiro": top3_r[0],
            "primeiro_igual_base": top3_r[0] == top3_b[0],
            "top3_em_comum": len(set(top3_r) & set(top3_b)),
            "spearman": round(rho, 3),
        })

resultado = pd.DataFrame(linhas)
for ncm in sorted(resultado["NCM"].unique()):
    print(f"=== NCM {ncm} ===")
    print(resultado[resultado["NCM"] == ncm].drop(columns="NCM").to_string(index=False))
    print()

resultado.to_csv("dados_processados/sensibilidade.csv", index=False, sep=";")
print("Arquivo 'sensibilidade.csv' salvo em dados_processados/")