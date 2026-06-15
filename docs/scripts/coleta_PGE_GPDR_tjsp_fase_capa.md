# Coleta de Dados de Capa - TJSP (PGE GPDR)

# `scripts/coleta_PGE_GPDR_tjsp_fase_capa.py`

| Metadado            | Valor                                      |
|---------------------|--------------------------------------------|
| Data de criação     | 2026-04-15                                 |
| Data de atualização | 2026-04-29                                 |
| Responsável(is)     | @alexandrehiero                            |
| Dependências principais | `pandas`, `curl_cffi` (via módulo em src)  |

## Contexto e Motivação

*Qual pipeline esse script executa? Por que ele é necessário?*
O projeto possui uma base de dados interna (PGE GPDR) contendo 273.327 processos. Ele foi necessário para se coletar dos metadados de capa desses processos no site público do e-SAJ para posterior enriquecimento da base interna pré-existente. 

Esse script pega o número de todos esses processos da base enviada pela PGE (PGE GPDR), compara com a lista "df_existente" chamada pela função "carregar_ja_coletados" que contêm os números dos processos já coletados e, a partir disso, faz-se a coleta dos que ainda não foram coletados buscando esses processos no site do e-SAJ, e os direcionando para a base já existente em "coleta_tjsp_resultados.csv".

## Decisões de Pipeline

- **Fonte de dados:** `data/PGE.GPDR.json` (gerado pelo time da PGE)
- **Destino:** `data/coleta_tjsp_resultados.csv` (incremental, com checkpoint)
- **Controle de repetição:** carrega processos já salvos a partir do CSV de saída – evita refazer coletas.
- **Delay entre requisições:** `random.uniform(3.5, 7.2)` para não sobrecarregar o TJSP.
- **Tratamento de múltiplos resultados:** utiliza método `resolve_multiple_results` do scraper.

## Como Executar

```bash
# A partir da raiz do projeto
python scripts/coleta_PGE_GPDR_tjsp_fase_capa.py
```

## Principais Parâmetros (constantes no código)

| Constante | Valor | Descrição |
|-----------|-------|-------------|
| `INPUT_FILE` | `data/PGE.GPDR.json` | Arquivo com a lista de processos |
| `OUTPUT_FILE` | `data/coleta_tjsp_resultados.csv` | Resultados incrementais |
| `SLEEP_RANGE` | `3.5, 7.2` | Intervalo aleatório entre chamadas |

## Logs e Monitoramento

- Logs são escritos no console e em `logs/coleta.log` (configurar `logging.basicConfig`).
- Em caso de interrupção (`Ctrl+C`), o script finaliza graciosamente e os processos já coletados permanecem no CSV.

## Falhas Conhecidas e Workarounds

- **Problema:** Processos com número muito antigo ou processos de outros tribunais retornam página vazia no e-SAJ.  
  **Workaround:** O script registra `[FALHA]`, e registra o processo com os metadados como "NÃO HÁ REGISTRO" e continua.
- **Problema:** O TJSP pode devolver captcha após muitas requisições.  
  **Workaround:** Não implementado – é necessário reiniciar manualmente após pausa.

## Decisões Futuras

- [ ] Implementar retry com backoff exponencial (biblioteca `tenacity`).
- [ ] Enviar notificação ao Telegram ao final da coleta.
- [ ] Paralelizar com `asyncio` para ganho de performance (cuidado com bloqueio).

## Relação com Outros Artefatos

- Depende do módulo `src/scrapers/scraper_tjsp_capa_request.py`.
- Alimenta a base normalizada ("coleta_tjsp_resultados.csv").

## Lições Aprendidas

- O checkpoint por CSV é simples e eficaz; evita reprocessar centenas de itens após falha.
- O uso de `pathlib` tornou o script portável entre Windows e Linux.
- O uso da função `time.sleep` e a sua configuração como um valor `random` permite a coleta contínua dos dados durante um longo período de tempo sem erros de coleta e sem bloqueios.
