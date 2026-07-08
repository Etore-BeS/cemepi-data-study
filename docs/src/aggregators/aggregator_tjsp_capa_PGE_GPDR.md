# Aggregator TJSP Capa PGE GPDR – `src/aggregators/aggregator_tjsp_capa_PGE_GPDR.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-01           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `json`               |

## Contexto e Motivação

O passo final da esteira de dados consiste em enriquecer a base de metadados internos (PGE) com os dados públicos coletados do tribunal (TJSP), gerando a camada **Gold**. Este Aggregator atua como o motor de *Join* do Data Lake. Além de realizar o cruzamento, ele identifica lacunas (processos esperados pela PGE que não retornaram do TJSP) e gera dinamicamente uma fila de processos pendentes para retroalimentar o pipeline de coleta (repescagem).

## Decisões de Arquitetura

- **Classe principal:** `FacePGEGPDRAggregator` – responsável por cruzar as bases Silver e rotear os resultados (Ricos/Match vs. Pobres/Miss).
- **Algoritmo de Hash Join em Memória:** Para evitar lentidão de buscas `O(N)`, a base do TJSP (Silver Nossos) é lida primeiro e mapeada para um dicionário em memória (`dict_nossos`) utilizando o `processo_pk` como chave (`O(1)` para lookup).
- **Escrita em Fluxo (Simulação de JSON Array):** A base da PGE é lida linha a linha (Streaming). Para a saída, em vez de acumular os resultados numa lista gigante na RAM e usar `json.dump`, o script escreve os caracteres `[\n` no início, intercala os objetos com `,\n` e finaliza com `\n]`. Isso gera um JSON válido no disco mantendo o consumo de memória baixo e estável.
- **Roteamento Condicional (Rich vs. Poor):** 
  - Se houver *Match* (Ricos), o documento do TJSP é enriquecido com os metadados da PGE e injetado na base Gold.
  - Se *Não* houver *Match* (Pobres), um documento *placeholder* (com status `PENDENTE_CAPA`) é enviado para a Gold, e o documento original é enviado para a fila de `pendentes` para ser coletado posteriormente pelo Scraper.
- **Isolamento de PK:** Ao realizar o merge com sucesso, a chave `processo_pk` é excluída do documento final na base Gold, priorizando o `_id` interno do sistema como identificador único de negócio na ponta.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|-------------|--------------------|
| `pd.merge` (Left Join via Pandas) | Rejeitada. Carregar as duas bases Silver (centenas de milhares de linhas) integralmente na memória para o cruzamento geraria um gargalo perigoso (Out of Memory) em máquinas com restrição de RAM. |
| Inserção em Banco Relacional (SQL) | Descartado no momento. Como estamos consolidando documentos dinâmicos para a Iniciação Científica, arquivos no formato NoSQL (JSON) oferecem flexibilidade sem precisar de migrações complexas de schema (DDL) durante a etapa de pesquisa. |

## Limitações Conhecidas

- **Gargalo de Dicionário em Memória:** Embora altamente otimizado para o cenário atual, o carregamento de `dict_nossos` aloca todos os processos do TJSP na RAM de uma só vez. Se o projeto escalar para milhões de processos, essa abordagem esgotará a memória. A solução futura seria usar um motor OLAP local ou processamento distribuído.
- **Formato Final de Saída:** Diferente dos Transformers que usam JSON Lines (`.jsonl`), o Aggregator gera um JSON em formato de Array tradicional. Isso obriga o consumidor final (camada de Machine Learning/Análise) a ler o arquivo inteiro na memória no momento de ingestão. 

## Exemplo de Uso

```python
from src.aggregators.aggregator_tjsp_capa_PGE_GPDR import FacePGEGPDRAggregator

# Inicia o agregador passando as referências das camadas Silver e os destinos Gold/Fila
aggregator = FacePGEGPDRAggregator(
    silver_nossos="caminho/para/silver_tjsp.jsonl",
    silver_ic="caminho/para/silver_pge.jsonl",
    output_gold="caminho/para/gold_processos_enriquecidos.json",
    output_pendentes="caminho/para/fila_repescagem.json"
)

# Executa o cruzamento e coleta as métricas
qtd_gold, qtd_ricos, qtd_pobres = aggregator.realizar_join_gold()

print(f"Total gerado na Gold: {qtd_gold}")
print(f"Sucessos (Enriquecidos): {qtd_ricos}")
print(f"Pendentes (Fila retroalimentada): {qtd_pobres}")
```

## Testes e Validação

- Validação lógica de robustez: A leitura em fluxo ignora linhas em branco (if not line.strip(): continue), prevenindo erros de parsing json.loads gerados por quebras de linha indesejadas no meio dos arquivos .jsonl.

## Histórico de Modificações

| Data | Usuário | Alteração |
|------|---------|------------|
| 2026-07-01 | @alexandrehiero | Inicialização da feature de auditoria e transformação, finalizando a integração na camada Aggregators. |
