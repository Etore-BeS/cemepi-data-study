# Transformer Silver PGE GPDR – `src/transformers/transformer_silver_PGE_GPDR.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-01           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `json`, `re`         |

## Contexto e Motivação

Como parte do fluxo de cruzamento de dados jurídicos, é necessário integrar as bases de controle interno (arquivos JSON brutos originários da PGE - Procuradoria Geral do Estado) ao ecossistema do Data Lake. Este módulo é responsável por promover os dados da PGE para a camada Silver, isolando informações de negócio em um nó de metadados padronizado e aplicando formatação rigorosa na chave primária do processo (padrão CNJ).

## Decisões de Arquitetura

- **Classe principal:** `PGE_GPDRTransformerSilver` – isola as regras de mapeamento e sanitização específicas da origem "PGE GPDR".
- **Padronização de Schema (Data Contract):** O código protege o namespace principal do documento Silver. Em vez de colocar todas as colunas originais na raiz do JSON, atributos específicos da PGE (Pasta, Situação, Matéria, Polo) são encapsulados hierarquicamente dentro do objeto `metadados`. Isso evita colisões de chaves com dados extraídos de outras fontes (como o TJSP).
- **Normalização da Chave Primária (Regex):** O script aplica de forma autônoma a máscara CNJ (20 dígitos) na propriedade `processo_pk`, garantindo que eventuais ausências de pontuação no sistema da PGE não impossibilitem joins futuros com a base do Tribunal.
- **Saída em Streaming (JSON Lines):** O processamento de escrita utiliza iteração linha a linha (`f_out.write(json.dumps(...) + '\n')`). Essa arquitetura converte um array JSON massivo em um arquivo orientado a eventos, facilitando a ingestão por sistemas de Big Data ou bancos NoSQL sem travar a leitura downstream.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|-------------|--------------------|
| Manter as chaves originais na raiz | Rejeitada. Chaves como "Polo PGE" ou "É originário?" são altamente acopladas à regra de negócio da procuradoria. Injetá-las na raiz violaria a padronização do schema estrutural do projeto. |
| Streaming de Leitura (ex: `ijson`) | A biblioteca nativa `json.load` foi escolhida pela simplicidade de implementação, assumindo temporariamente que o arquivo de origem da PGE possui um tamanho que a memória RAM atual suporta confortavelmente. |

## Limitações Conhecidas

- **Gargalo de I/O na Leitura (In-Memory Load):** O uso de `json.load(f)` lê a integridade do arquivo original para a memória de uma única vez. Se o dataset da PGE crescer muito para a casa dos Gigabytes, a aplicação sofrerá um *Out of Memory (OOM)*. A refatoração ideal exigirá a substituição por um parser iterativo (como `ijson`).
- **Acoplamento de Atributos:** O código possui mapeamento hardcoded para extrair campos muito literais (ex: `"É originário?"`). Qualquer alteração no sistema de extração bruto da PGE quebrará a estruturação.

## Exemplo de Uso

```python
from src.transformers.transformer_silver_PGE_GPDR import PGE_GPDRTransformerSilver

# Instancia o transformer configurando as rotas de entrada e saída
transformer_pge = PGE_GPDRTransformerSilver(
    input_ic_json="caminho/para/raw_pge.json",
    output_silver_ic="caminho/para/silver_pge.jsonl"
)

# Aciona a conversão da base
total_processados = transformer_pge.json_pge_para_silver()
print(f"Transformação da base PGE concluída. Processos: {total_processados}")
```

## Testes e Validação

- Validação da máscara CNJ atua com guard clauses seguras: se o processo limpo (\D) não possuir exatamente 20 caracteres, a máscara não é aplicada cegamente, prevenindo a corrupção de números de processos antigos ou processos administrativos (que possuem menos dígitos).

## Histórico de Modificações

| Data | Usuário | Alteração |
|------|---------|------------|
| 2026-07-01 | @alexandrehiero | Criação da feature de transformação e padronização da base PGE. |
| 2026-07-01 | @alexandrehiero | Remoção de bibliotecas não utilizadas para manutenção de Clean Code. |
