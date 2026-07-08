# Transformer Erros Dados Capa Bronze – `src/transformers/transformer_erros_dados_capa_bronze.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-01           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `pandas`, `json`, `re`, `pathlib`  |

## Contexto e Motivação

Durante a fase de *repescagem* (retry) de processos que falharam na coleta inicial, é necessário integrar os novos sucessos à base Master sem gerar duplicidade, além de retroalimentar a fila de pendências com as tentativas que voltaram a falhar. Este módulo atua como um consolidador (Merge & Update) seguro para a camada Bronze. Ele lê o lote de repescagem, separa os sucessos das falhas, atualiza a fila JSON e injeta os novos registros no arquivo principal de forma otimizada.

## Decisões de Arquitetura

- **Classe principal:** `TransformerErrosDadosCapaBronze` – isola a lógica de roteamento de dados (Falhas -> Fila JSON; Sucessos -> Master CSV / Duplicados CSV).
- **Anti-Join de Alta Performance (`O(1)`):** Para descobrir se um processo da repescagem já existe na base Master, o código carrega estritamente a coluna `"Processo"` da Master e a converte em um `set()` (`set_master`). A filtragem ocorre via `isin()` do Pandas contra esse Set, garantindo validação ultrarrápida sem onerar a CPU.
- **I/O Eficiente (Estratégia Append-Only):** Em vez de ler o arquivo Master inteiro para a memória, concatenar os novos dados e reescrever o arquivo (o que geraria alto consumo de RAM e risco de corrupção I/O), o módulo utiliza a escrita incremental direta no disco (`mode='a'` no `to_csv`).
- **Idempotência Garantida:** Devido ao isolamento de duplicatas (arquivadas em `csv_duplicados`) e à normalização das chaves (`_padronizar_processo`), o pipeline de repescagem pode ser interrompido e reexecutado múltiplas vezes sobre o mesmo lote sem risco de poluir a base Master.
- **Gestão de Estado de Cabeçalhos:** A lógica `precisa_cab_master = not self.csv_master.exists()` assegura que, se o pipeline estiver rodando pela primeira vez e o arquivo não existir, o cabeçalho (header) será inserido corretamente, adaptando-se automaticamente a inicializações limpas.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|-------------|--------------------|
| `pd.concat([df_master, df_novo]).drop_duplicates()` | Rejeitada. Carregar a base Master inteira (todas as colunas) na memória para fazer um merge global causaria um pico massivo de uso de RAM, inviabilizando a escalabilidade conforme a base ultrapassa as centenas de milhares de linhas. |
| Remoção de falhas no JSON original da fila | Rejeitada. Modificar a lista iterando sobre ela enquanto sofre remoções pode gerar comportamentos inesperados. O código adota a criação de uma `nova_fila` (imutabilidade funcional), que é mais segura antes do *dump* final. |

## Limitações Conhecidas

- **Gargalo de Memória da Master Key:** Embora carregue apenas uma coluna (`usecols=["Processo"]`), carregar milhões de chaves de processo para a memória no formato String pode se tornar um gargalo futuro. Caso o dataset passe de alguns milhões, a verificação de duplicidade precisará ser migrada para um banco de dados leve (como SQLite ou DuckDB).
- **Acoplamento de Colunas:** A lógica de identificação de falha depende estritamente das strings `"NÃO HÁ REGISTRO"` nas colunas `"Classe"` e `"Foro"`. Mudanças no Scraper exigem atualização neste módulo.

## Exemplo de Uso

```python
from src.transformers.transformer_erros_dados_capa_bronze import TransformerErrosDadosCapaBronze

# Inicializa o injetor/consolidador
transformer = TransformerErrosDadosCapaBronze(
    csv_repescagem="caminho/para/sandbox_repescagem.csv",
    csv_master="caminho/para/bronze_master.csv",
    csv_duplicados="caminho/para/bronze_duplicados.csv",
    json_leitura="caminho/para/fila_pendentes_atual.json",
    json_saida="caminho/para/fila_pendentes_atualizada.json"
)

# Executa o roteamento e consolidação
metricas = transformer.processar_merge_e_fila()

print(f"Novos injetados na Master: {metricas['injetados']}")
print(f"Duplicados isolados: {metricas['duplicados']}")
print(f"Falhas persistentes (Fila atualizada): {metricas['restantes_fila']}")
```

## Testes e Validação

- Validação implícita de formatação de CNJs: O uso do _padronizar_processo em ambas as pontas (dados novos e chaves da master) garante que variações como 1234567-89 e 123456789 colidam corretamente no momento do Anti-Join, evitando falsos negativos.

## Histórico de Modificações

| Data | Usuário | Alteração |
|------|---------|------------|
| 2026-07-01 | @alexandrehiero | Criação e integração da lógica de expurgo, fila e consolidação de duplicatas. |
| 2026-07-01 | @alexandrehiero | Padronização dos números de processo nas auditorias e reescrita de rotas lógicas. |
