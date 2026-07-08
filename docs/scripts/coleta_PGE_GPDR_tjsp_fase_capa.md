# Coleta PGE GPDR TJSP Capa – `scripts/coleta_PGE_GPDR_tjsp_fase_capa.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-04-15           |
| Data de atualização     | 2026-07-03           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `pandas`, `json`, `pathlib`, `FaceTJSPScraper`   |

## Contexto e Motivação

Este script é o **Orquestrador de Coleta** da camada Bronze. O projeto possui uma base de dados da PGE (Procuradoria Geral do Estado) contendo 273327 mil processos. Este script é responsável por varrer uma fila de processos, acionar o *Scraper* `scraper_tjsp_capa_request.py` (módulo `src`) para extrair os metadados da capa de cada processo diretamente do site público do e-SAJ (TJSP) e salvar os resultados de forma contínua e incremental. Ele é vital para o enriquecimento da base interna.

## Decisões de Pipeline

- **Fonte de dados dinâmica (Fila de Repescagem):** O script implementa uma lógica de fallback inteligente. Ele busca primeiro o arquivo `data/processos_pendentes_final.json`. Se não existir, recorre ao arquivo `data/PGE.GPDR.json`. Isso permite que o script seja reexecutado para focar apenas nos processos que falharam em etapas anteriores.
- **Destino Incremental:** O resultado é gravado em `data/coleta_tjsp_resultados.csv` utilizando `mode='a'` (Append). A memória não é sobrecarregada, pois as linhas são injetadas no disco a cada iteração bem-sucedida.
- **Controle de Idempotência (Checkpoint):** A função `carregar_ja_coletados()` lê o CSV de saída, extrai a coluna `"Processo"` e monta um `set()` em memória. Os processos já existentes são filtrados da lista de execução. Se o script for interrompido, ele recomeçará exatamente de onde parou.
- **Delay (Throttling):** Utiliza-se `time.sleep(random.uniform(1.8, 2.7))` para inserir uma pausa randômica entre requisições. Isso simula comportamento humano e evita bloqueios (Rate Limit ou mitigação de DDoS) por parte do firewall do TJSP.
- **Construção de URL Dinâmica:** Para evitar ambiguidades na busca do e-SAJ, o código fatora o número do processo (quando possui 25 caracteres), extraindo `num_digito_ano` e `foro_num` para compor uma URL de consulta parametrizada com precisão.

## Como Executar

```bash
# A partir da raiz do projeto, utilizando o gerenciador de pacotes uv
uv run python scripts/coleta_PGE_GPDR_tjsp_fase_capa.py
```

## Principais Parâmetros (constantes no código)

| Constante | Valor | Descrição |
|-----------|-------|-------------|
| `INPUT_FILE` | `data/PGE.GPDR.json` | Arquivo com a lista de processos |
| `PENDENTES_FILE` | `data/processos_pendentes_final.json` | Fila prioritária de repescagem. |
| `OUTPUT_FILE` | `data/coleta_tjsp_resultados.csv` | Arquivo de destino (incremental). |
| `SLEEP_RANGE` | `1.8, 2.7` | Intervalo aleatório entre chamadas |

## Logs e Monitoramento

- O monitoramento é feito em tempo real via terminal (stdout), emitindo mensagens claras de estado:
  - `[OK]` para coleta bem-sucedida com contagem total.
  - `[FALHA]` caso a página esteja vazia ou o parser falhe.
  - `[ERRO]` capturando exceções (catch Exception) para que o script não crashe.

## Falhas Conhecidas e Workarounds

- **Problema**: Processos com números anômalos/antigos retornam páginas vazias ou falham no parseamento do HTML.
  **Workaround**: O orquestrador loga [FALHA] e usa a instrução continue para seguir para o próximo registro da fila sem escrever lixo estrutural no CSV. Esses processos serão identificados posteriormente pelo Transformer de Auditoria.

- **Problema**: O e-SAJ pode devolver desafios (Captchas) após tráfego anômalo.
  **Workaround**: Não implementado nativamente no script. Requer intervenção manual: parar o script, aguardar o cooldown do IP e reiniciar (o checkpoint evita perda de progresso).

## Decisões Futuras

- [ ] Implementar retry com backoff exponencial (biblioteca `tenacity`).
- [ ] Enviar notificação ao Telegram ao final da coleta.
- [ ] Adicionar rotação de IPs ou proxies caso o tempo de cooldown prejudique o cronograma da pesquisa.

## Relação com Outros Artefatos

- Depende do módulo `src/scrapers/scraper_tjsp_capa_request.py`.
- Alimenta: O arquivo bruto `coleta_tjsp_resultados.csv`, que posteriormente é consumido pelas classes de Transformers (limpeza e estruturação).

## Lições Aprendidas

- O checkpoint por CSV é simples e eficaz; evita reprocessar centenas de itens após falha.
- O uso de `pathlib` tornou o script portável entre Windows e Linux.
- O uso da função time.sleep com valores randômicos permitiu a coleta contínua de um altíssimo volume de dados ao longo do tempo sem engatilhar os sistemas de defesa anti-bot do tribunal.
- A lógica de priorização de fila (arquivo_alvo = PENDENTES_FILE if os.path.exists...) desacoplou a necessidade de criar scripts diferentes para a rodada inicial e para a repescagem.

## Histórico de Modificações

| Data       | Usuário          | Alteração |
|------------|------------------|-----------|
| 2026-04-24 | @alexandrehiero  | Criação do coleta TJSP capa |
| 2026-04-25 | @alexandrehiero  | Criação do método para coletar os dados quando o site e-SAJ retornava mais de um resultado na pesquisa |
| 2026-04-29 | @alexandrehiero  | Definição do time.sleep com a função random para a coleta |
| 2026-06-05 | @alexandrehiero  | Criação da documentação do script |
| 2026-06-15 | @alexandrehiero  | Atualização para formato ADR |
| 2026-06-17 | @alexandrehiero  | Atualizações de erros na documentação |
| 2026-07-03 | @alexandrehiero  | Revisão arquitetural da documentação para refletir fila de repescagem, tempos reais de delay e comportamento de falhas (Code vs. Docs). |
