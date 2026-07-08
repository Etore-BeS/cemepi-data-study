# Merge de Erros da Bronze (Repescagem) – `scripts/auditoria_merge_erros_dados_capa_bronze.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-03           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `sys`, `pathlib`, `TransformerErrosDadosCapaBronze`|

## Contexto e Motivação

Durante o web scraping de retentativa (repescagem) dos processos que falharam na primeira rodada, o orquestrador de coleta gera um novo lote de dados (`coleta_tjsp_resultados.csv`). Se esses dados fossem simplesmente "colados" na base mestre, falhas persistentes corromperiam o dataset original e duplicatas iriam inflacionar o volume da base. Este orquestrador resolve esse problema atuando como um *Gatekeeper* de Merge: ele expurga falhas, direciona-as para uma nova fila JSON de pendentes e cruza os dados limpos com a base mestre em modo Anti-Join, garantindo que apenas registros inéditos entrem no arquivo definitivo (Master Backup).

## Decisões de Pipeline

- **Arquitetura de Isolamento (Sandbox):** O script nunca altera os arquivos mestres até ter certeza matemática do resultado. Ele trata `coleta_tjsp_resultados.csv` como um ambiente temporário, avalia o que é duplicata e desvia esse tráfego I/O para um arquivo isolado (`duplicado_dados_capa.csv`), preservando a integridade da base `coleta_tjsp_resultados_BKP.csv`.
- **Evolução de Fila (Versioning):** O orquestrador gerencia de forma imutável os arquivos JSON. Ele não sobrescreve a fila de leitura original (`processos_pendentes_final.json`), mas gera um *novo* arquivo de saída (`processos_pendentes_restantes.json`), permitindo ao operador auditar exatamente o que restou de pendente naquela "fotografia" temporal do pipeline.
- **Visualização de Métricas em Tempo Real:** O bloco `try...except` não apenas captura erros, mas desempacota um dicionário de métricas vitais de negócio gerado pelo Transformer, expondo diretamente no terminal (CLI) a distribuição exata do roteamento (Inéditos, Duplicatas, Falhas e Pendentes restantes).

## Como Executar

```bash
# A partir da raiz do projeto, utilizando o gerenciador de pacotes uv
uv run python scripts/auditoria_merge_erros_dados_capa_bronze.py
```

## Principais Parâmetros (constantes no código)

| Constante | Valor | Descrição |
|-----------|-------|-------------|
| `csv_repescagem` | `data/coleta_tjsp_resultados.csv` | Lote recém-coletado a ser avaliado. |
| `csv_master_bkp` | `data/coleta_tjsp_resultados_BKP.csv` | A base Bronze mestre e definitiva. |
| `csv_duplicados` | `data/duplicado_dados_capa.csv` |  Cofre para processos que já existiam na master. |
| `json_pendentes_leitura` | `data/processos_pendentes_final.json` | Fila de repescagem original (Input). |
| `json_pendentes_saida` | `data/processos_pendentes_restantes.json` |  Fila atualizada apenas com os persistentes (Output). |

## Logs e Monitoramento
- A interface CLI foi desenhada para "Developer Experience" (DX). Utiliza painéis de delimitadores (===) e emojis semânticos (🛠️, 🏁, ❌) para fornecer feedback imediato.
- O monitoramento exibe quatro métricas explícitas: Injetados, Duplicatas, Falhas Expurgadas e Restantes na Fila.

## Falhas Conhecidas e Workarounds
- **Problema:** Erro de Sequência de Pipeline. Se o pesquisador rodar este script antes de rodar o Scraper, os arquivos de repescagem não existirão.
    **Workaround:** O script captura especificamente `FileNotFoundError` e emite uma mensagem corretiva amigável (Rode o scraper primeiro para gerar novos dados), abortando a operação sem poluir o log com rastros de pilha complexos.

## Decisões Futuras
- [ ] Implementar uma função que, após validação bem-sucedida, mova o arquivo coleta_tjsp_resultados.csv para uma pasta archive/, evitando que lotes antigos sejam reprocessados acidentalmente.
- [ ] Adicionar suporte nativo à geração de relatórios tabulares breves (ex: Markdown ou HTML) detalhando as amostras de falha persistente.

## Relação com Outros Artefatos
- Depende: Da geração de dados pelo script `coleta_PGE_GPDR_tjsp_fase_capa.py` e da lógica algorítmica exposta em `src/transformers/transformer_erros_dados_capa_bronze.py`.
- Alimenta: O ciclo infinito de repescagem. O JSON de saída gerado por este script ditará o ritmo da próxima rodada do orquestrador de scraper.

## Lições Aprendidas
- O uso de uma topologia de arquivos clara (separando master, leitura e saída) eliminou a necessidade de locks de banco de dados ou tratativas de concorrência.
- Tratar dados duplicados como "efeito colateral esperado" e direcioná-los para um arquivo segregado é muito mais seguro do que fazer drop invisível na memória.


## Histórico de Movimentações

| Data       | Usuário          | Alteração |
|------------|------------------|-----------|
| 2026-06-20 | @alexandrehiero  | Inicialização do script orquestrador de auditoria de retentativas. |
| 2026-07-03 | @alexandrehiero  | Correção de docstrings (mudança para blocos explícitos de terminal) e exclusão de importações ociosas. |
| 2026-07-03 | @alexandrehiero  | Criação da documentação do script |
