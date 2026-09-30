# Sistema de Inteligência Comercial para Priorização de Mercados de Exportação De Embalagens Pásticas Por Meio de um índice de Potencial de Mercado

Sistema de apoio à decisão que analisa dados de comércio exterior brasileiro e prioriza mercados internacionais para exportação de produtos relacionados a embalagens plásticas flexíveis, a partir de um índice composto desenvolvido especificamente para este estudo.

Trabalho de Conclusão de Curso em Sistemas de Informação — UNIBAVE, 2026.

**Aplicação publicada:** [tcc-ipm-unibave2026.streamlit.app](https://tcc-ipm-unibave2026.streamlit.app)

## Objetivo

Identificar, entre os países de destino das exportações brasileiras, aqueles com maior potencial relativo para priorização comercial, combinando indicadores de volume, crescimento e estabilidade das exportações em um índice único: o **Índice de Potencial de Mercado (IPM)**.

## Dados

- **Fonte:** Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), base de dados abertos do Comex Stat
- **Período:** 2021 a 2025
- **Produtos (NCM):** 3920.10.99, 3923.21.10, 3923.21.90
- **Escopo:** exclusivamente exportações brasileiras (não inclui dados de importação, participação de mercado ou bases internacionais como Trade Map/UN Comtrade)

Os dados brutos do Comex Stat não estão neste repositório (ver `.gitignore`) e precisam ser baixados separadamente em [gov.br/mdic](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta) para reproduzir o pipeline completo (`limpar_dados.py` em diante). O arquivo `dados_processados/ranking_ipm.csv` já está disponível no repositório para uso direto na interface.

## Indicadores e pesos do IPM

| Indicador | Peso | Descrição |
|---|---|---|
| Volume médio | 65% | Média do valor exportado (US$ FOB) nos anos com dados disponíveis |
| Estabilidade | 20% | Coeficiente de variação dos valores exportados (quanto menor, mais estável) |
| Crescimento | 15% | Variação percentual entre o primeiro e o último ano com registro |

O IPM é calculado separadamente para cada NCM, após um filtro de relevância (volume mínimo de 10% do maior exportador do produto) e tratamento de valores extremos no crescimento (limite no percentil 90).


## Tecnologias

- Python
- Pandas (tratamento e análise de dados)
- Plotly (visualizações interativas)
- Streamlit (interface web)
- Git / GitHub (versionamento)
- Streamlit Community Cloud (hospedagem)


## Limitações

- O sistema utiliza exclusivamente dados de exportação brasileira; não mede demanda do mercado importador nem participação de mercado.
- O indicador de estabilidade reflete a regularidade do fluxo de exportações brasileiras, não da demanda do país importador.
- Os pesos do IPM refletem uma calibração baseada em conhecimento prático do setor, sem validação por painel de especialistas.
- Um dos NCMs analisados (3923.21.10) possui número reduzido de países no ranking, o que limita a robustez estatística de suas medidas.

## Autoria
Desenvolvido por Elisa Alberton como Trabalho de Conclusão de Curso em Sistemas de Informação.