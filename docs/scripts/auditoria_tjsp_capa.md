# Auditoria TJSP Capa – `scripts/auditoria_tjsp_capa.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-03           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `sys`, `pathlib`, `FaceAuditoriaTJSP`   |

## Contexto e Motivação

Este script orquestra a limpeza física da camada Bronze e gera as filas de repescagem. Durante o web scraping massivo da base da PGE (centenas de milhares de processos), interrupções de rede ou falhas no e-SAJ deixam "lixo" no CSV de saída e geram buracos na coleta. A auditoria garante a integridade da base, apagando duplicatas ou falhas (processos que vieram sem dados), e cruza os dados salvos com a lista esperada (JSON Master), gerando um arquivo de pendências (`processos_pendentes.json`) para alimentar a próxima rodada do scraper de forma autônoma.

## Decisões de Pipeline

- **Fonte de dados:** `data/PGE.GPDR.json` (base esperada) e `data/coleta_tjsp_resultados.csv` (resultado parcial da coleta).
- **Destino (Ação Mutável):** Limpa o próprio `coleta_tjsp_resultados.csv` (sobreescrita in-place) e gera o arquivo `data/processos_pendentes.json`.
- **Injeção de Dependência Fixa:** O script inicializa a classe `FaceAuditoriaTJSP` isolando os caminhos dos arquivos com a biblioteca `pathlib`. Isso garante resolução absoluta dos diretórios independentemente de onde o script for chamado no terminal.
- **Isolamento de Lógica:** Nenhuma regra de negócio (como o que define um erro ou duplicata) é declarada aqui. O script atua estritamente como um *Controller/Orquestrador*, delegando o peso computacional para a camada `src/transformers/transformer_auditoria_tjsp_capa.py`.

## Como Executar

```bash
# A partir da raiz do projeto, utilizando o gerenciador de pacotes uv
uv run python scripts/auditoria_tjsp_capa.py
```

## Principais Parâmetros (constantes no código)

| Constante | Valor | Descrição |
|-----------|-------|-------------|
| `PROJECT_ROOT` | Caminho absoluto do projeto | Raiz calculada via `Path(__file__)` |
| `input_json` | `data/PGE.GPDR.json` | Base original esperada. |
| `output_csv` | `data/coleta_tjsp_resultados.csv` | A base Bronze suja e o alvo da limpeza. |
| `pendentes_file` | `data/processos_pendentes.json` | O arquivo gerado de saída com a nova fila. |

## Logs e Monitoramento

- A interface via terminal fornece feedback quantitativo imediato, listando quantas falhas foram expurgadas, quantas duplicatas foram removidas e o saldo de Esperado vs. Coletado vs. Pendente. Esse log numérico é fundamental para checar a "saúde" do lote de coleta.

## Falhas Conhecidas e Workarounds

- **Problema:** A exclusão de duplicatas do CSV de destino (output_csv) atua sobre todo o arquivo carregado em memória. Se a base Bronze ultrapassar o tamanho da RAM disponível na máquina, o script falhará com erro de MemoryError.
  **Workaround:** Atualmente suportado pela memória da máquina. Para escalonamento futuro, a delegação do drop de duplicatas deve ser feita no banco de dados.

## Decisões Futuras

- [ ] Implementar integração com notificação de finalização, enviando as métricas de sanidade (Total Expurgado/Total Pendente) diretamente via API (ex: Slack ou Telegram).

## Relação com Outros Artefatos

- Depende: Da classe FaceAuditoriaTJSP do módulo `src/transformers/transformer_auditoria_tjsp_capa.py`.
- Alimenta: A fila de retentativas consumida pelo script `coleta_PGE_GPDR_tjsp_fase_capa.py`.

## Lições Aprendidas

- Isolar caminhos de arquivos (pathlib) direto no orquestrador facilitou a portabilidade entre ambientes Linux e Windows, blindando a classe Transformer de amarras estruturais.
- O script atua como um "Gatekeeper" de qualidade, garantindo que etapas subsequentes do pipeline (Silver/Gold) não lidem com lixo não mapeado.

## Histórico de Movimentações

| Data       | Usuário          | Alteração |
|------------|------------------|-----------|
| 2026-06-20 | @alexandrehiero  | Inicialização do script orquestrador da feature de auditoria e transformação. |
| 2026-07-03 | @alexandrehiero  | Criação da documentação do script |
