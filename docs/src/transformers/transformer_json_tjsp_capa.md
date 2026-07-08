# Transformer JSON TJSP Capa – `src/transformers/transformer_json_tjsp_capa.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-01           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `pandas`, `json`, `re`, `datetime`   |

## Contexto e Motivação

O módulo foi criado para converter os dados brutos extraídos das capas de processos do e-SAJ (armazenados na camada Bronze em formato CSV) para um formato estruturado, limpo e aninhado (camada Silver em formato JSON). Essa transformação é essencial para adequar os dados a um schema padronizado — contendo hierarquia de tribunais, partes estruturadas e datas no padrão ISO 8601 —, preparando o dataset para consumo analítico ou ingestão em bancos de dados orientados a documentos (como MongoDB).

## Decisões de Arquitetura

- **Classe principal:** `FaceTransformerSilverTJSP` – responsável por encapsular a leitura do arquivo tabular e a aplicação das regras de limpeza e estruturação.
- **Processamento em Streaming (JSON Lines):** Em vez de construir uma lista gigante na memória RAM e fazer o dump de uma só vez, o método `transformar_csv_para_silver` utiliza o formato `.jsonl` (JSON Lines). O script itera sobre as linhas do DataFrame e escreve cada objeto diretamente no disco via `f_out.write(json.dumps(...) + '\n')`. Isso confere alta escalabilidade à aplicação, impedindo travamentos por excesso de consumo de memória ao lidar com data lakes volumosos (centenas de milhares de linhas).
- **Tipagem Forte e Padronização:** 
  - Valores monetários são limpos via *Regex* e convertidos explicitamente para `float`.
  - Datas passam de strings regionais (`dd/mm/yyyy`) para o padrão MongoDB Extend JSON (`{"$date": "YYYY-MM-DDT00:00:00.000Z"}`).
- **Sanitização de Nulos:** Verificações explícitas de `pd.isna()` e da string `"NÃO HÁ REGISTRO"`. A lógica ignora blocos de dados vazios em vez de popular o JSON com chaves inúteis.
- **Estruturação Hierárquica:** Separação semântica dos dados do processo nas chaves `processo_pk`, `processo`, `tribunal`, `grau`, `orgaoJulgador`, `datas`, `partes` (divididas em polos ativo/passivo) e `movimentos`.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|-------------|--------------------|
| `json.dump(lista_completa)` | Rejeitada. Montar uma matriz de centenas de milhares de dicionários na memória RAM seria um anti-pattern de engenharia de dados, criando um gargalo computacional e gerando risco elevado de *Out of Memory (OOM)*. |
| Inserção direta no Banco de Dados | Acoplar a transformação do dado diretamente com o serviço de banco de dados violaria o princípio de Responsabilidade Única (SRP). Gravar a camada Silver localmente permite revisões, auditorias e reprocessamentos antes da ingestão final. |

## Limitações Conhecidas

- O transformer possui variáveis estáticas (Hardcoded) referentes ao TJSP (como `sigla: "TJSP"`, `jtr: 826`, e o grau `G1`). Para escalar para outros tribunais ou instâncias superiores, essas variáveis precisarão ser passadas por injeção de dependência na inicialização da classe.
- O código possui um alto acoplamento com o formato exato das colunas do CSV gerado pelo Scraper (ex: chaves como `Status/Data Dist.`, `Assunto Principal`). Qualquer alteração no schema do CSV quebrará o parsing.

## Exemplo de Uso

```python
from src.transformers.transformer_json_tjsp_capa import FaceTransformerSilverTJSP

# Inicializa o transformer apontando as origens e destinos no data lake local
transformer = FaceTransformerSilverTJSP(
    input_csv="caminho/para/bronze_dados_tjsp.csv",
    output_silver="caminho/para/silver_dados_tjsp.jsonl"
)

# Executa a limpeza e estruturação em streaming
total_processados = transformer.transformar_csv_para_silver()
print(f"Transformação finalizada. Total de processos processados: {total_processados}")
```

## Testes e Validação

- Funções internas garantem que caracteres especiais e problemas de digitação em valores financeiros (R$, pontos, vírgulas invertidas) sejam sanitizados sem quebra de execução (ValueError encapsulado no try-except).

## Histórico de Modificações

| Data | Usuário | Alteração |
|------|---------|------------|
| 2026-07-01 | @alexandrehiero | Criação da feature de auditoria e transformação de dados. |
| 2026-07-01 | @alexandrehiero | Renomeação de classes para melhor clareza arquitetural e atualização de docstrings para comentários simples. |
| 2026-07-01 | @alexandrehiero | Remoção de bibliotecas ociosas (unused imports) dos scripts. |
