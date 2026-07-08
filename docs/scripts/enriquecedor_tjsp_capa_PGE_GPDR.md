# Enriquecedor TJSP Capa PGE GPDR (Camada Gold) – `scripts/enriquecedor_tjsp_capa_PGE_GPDR.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-03           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `sys`, `pathlib`, `FacePGEGPDRAggregator`    |

## Contexto e Motivação

Este script representa a última etapa do pipeline de engenharia de dados do projeto. Ele orquestra a geração da **Camada Gold**, cruzando os dados internos e padronizados da PGE com os dados públicos coletados do TJSP. O objetivo é criar um dataset único, enriquecido e pronto para consumo analítico (Machine Learning, BI ou NLP). Adicionalmente, ele atua como o gerador oficial da fila de retentativas (`processos_pendentes_final.json`), garantindo que o ciclo de coleta possa ser reiniciado apenas para as lacunas remanescentes.

## Decisões de Pipeline

- **Arquitetura de Controller (SoC):** O script blinda-se contra qualquer regra de negócio de junção de dados (Left Join, tratativa de chaves, formatação JSON). Ele delega todo o trabalho pesado de cruzamento e I/O estruturado para a classe `FacePGEGPDRAggregator` (camada `src`).
- **Injeção Dinâmica de Caminhos:** Utiliza `Path(__file__).resolve().parent.parent` para construir quatro caminhos absolutos distintos, protegendo a execução contra falhas de *Working Directory* no terminal.
- **Transparência de Métricas de Negócio:** A interface do terminal imprime categoricamente a divisão entre processos "Ricos" (Match com sucesso) e "Pobres" (Miss/Sem capa). Isso fornece ao pesquisador um indicador instantâneo da eficiência do scraper e do volume pendente de coleta.

## Como Executar

```bash
# A partir da raiz do projeto, utilizando o gerenciador de pacotes uv
uv run python scripts/enriquecedor_tjsp_capa_PGE_GPDR.py
```

## Principais Parâmetros (constantes no código)

| Constante | Valor | Descrição |
|-----------|-------|-------------|
| `PROJECT_ROOT` | Dinâmico (`pathlib`) | Resolve a raiz do repositório para ancorar os diretórios de dados. |
| `silver_nossos` | `data/silver_dados_capa_tjsp.json` | Base limpa do Tribunal (coletada). |
| `silver_ic` | `data/silver_dados_PGE_GPDR.json` |  Base limpa e mascarada da PGE. |
| `output_gold` | `data/gold_tjsp_enriquecido.json` | Produto final consolidado. |
| `output_pendentes` | `data/processos_pendentes_final.json` |  Fila retroalimentadora de repescagem. |

## Logs e Monitoramento
- Emite um log inicial informando o começo da operação de Left Join.
- Retorna um bloco de sucesso contendo a decomposição quantitativa (Total Gerado, Ricos, Pobres), garantindo rastreabilidade do resultado gerado nos arquivos de saída.

## Falhas Conhecidas e Workarounds
- **Problema:** Sensibilidade à Memória Herdada. Como este orquestrador invoca realizar_join_gold() (que aloca o arquivo do TJSP na RAM via dicionário), a execução pode sofrer Out of Memory (OOM) se a base Silver for demasiadamente grande para o hardware atual.
    **Workaround:** Suportado no volume atual do projeto.

## Decisões Futuras
- [ ] Incluir conversão automatizada do arquivo gold_tjsp_enriquecido.json para formato colunar (ex: .parquet), otimizando drasticamente a leitura para algoritmos de Machine Learning e processamento de linguagem natural (NLP).
- [ ] Adicionar um try-except global para capturar erros de integridade de arquivos (ex: se os JSONs da camada Silver ainda não tiverem sido gerados por esquecimento do operador).

## Relação com Outros Artefatos
- Depende: Da classe `FacePGEGPDRAggregator` do módulo `src/aggregators/aggregator_tjsp_capa_PGE_GPDR.py` e da conclusão prévia dos scripts orquestradores da camada Silver.
- Alimenta:
    - A pesquisa final (Machine Learning / Análises).
    - O orquestrador original de coleta (`coleta_PGE_GPDR_tjsp_fase_capa.py`), formando um ciclo fechado (loop) até que a lista de pendentes chegue a zero.

## Lições Aprendidas
- Apresentar a métrica de "Ricos" vs "Pobres" no stdout foi uma boa decisão de Developer Experience (DX), pois elimina a necessidade de abrir arquivos pesados para verificar se o cruzamento funcionou adequadamente.
- A orquestração manteve a premissa de idempotência e imutabilidade dos dados de entrada (Silver), apenas lendo as bases e emitindo novos arquivos na saída.



## Histórico de Movimentações

| Data       | Usuário          | Alteração |
|------------|------------------|-----------|
| 2026-06-20 | @alexandrehiero  | Criação do orquestrador de enriquecimento (Gold) e implementação da lógica de roteamento visual das filas. |
| 2026-07-03 | @alexandrehiero  | Criação da documentação do script |
