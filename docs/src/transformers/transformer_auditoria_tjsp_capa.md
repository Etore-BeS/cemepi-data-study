# Transformer Auditoria TJSP Capa – `src/transformers/transformer_auditoria_tjsp_capa.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-01           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `pandas`, `json`, `re`, `pathlib`  |

## Contexto e Motivação

Em processos de web scraping de alto volume (como a coleta dos 273327 mil capas processuais do TJSP), falhas de rede, bloqueios temporários e timeouts são inevitáveis. Este módulo atua como a malha de controle de qualidade (Quality Assurance) do pipeline de dados. Ele é responsável por varrer a base coletada (CSV), expurgar tentativas falhas ou duplicadas, e cruzar os sucessos com a base original esperada (JSON) para gerar dinamicamente uma "fila de repescagem" (pendências) para os processos que ainda precisam ser coletados.

## Decisões de Arquitetura

- **Classe principal:** `FaceAuditoriaTJSP` – centraliza a lógica de higienização de arquivos (Bronze) e o gerenciamento de filas de reprocessamento.
- **Estrutura de Dados de Alta Performance (`O(1)`):** No método `auditar_e_gerar_pendencias`, os processos já coletados com sucesso são armazenados em um `set()` (`set_coletados`). Isso transforma a verificação de existência (cruzamento de dados) de uma operação linear `O(N)` para uma operação constante `O(1)`, garantindo altíssima performance estrutural mesmo em volumes massivos de dados.
- **Normalização de Chaves Primárias:** O método privado `_padronizar_processo` utiliza expressões regulares (Regex) para garantir que o número do processo (padrão CNJ) esteja perfeitamente formatado com as máscaras corretas e trate sufixos, evitando que divergências sutis de formatação gerem falsos positivos na fila de pendências.
- **Isolamento de Estado (Sandbox):** O método `auditar_sandbox_repescagem` permite tratar um lote de tentativas falhas em um ambiente isolado (`sandbox_csv_path`). Ele atualiza a fila de pendências extraindo apenas os sucessos dessa nova rodada, evitando corrupção do arquivo CSV principal durante os retries automáticos.
- **Critério Rígido de Falha:** A exclusão de linhas inválidas baseia-se na verificação explícita `(df["Classe"] == "NÃO HÁ REGISTRO") & (df["Foro"] == "NÃO HÁ REGISTRO")`, garantindo que apenas acessos realmente frustrados sejam descartados e reenfileirados.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|-------------|--------------------|
| Left Join com `pd.merge` | Rejeitada. Carregar o JSON original completo e o CSV coletado na memória simultaneamente apenas para achar a diferença ("anti-join") consumiria muita memória RAM. A abordagem iterativa com `set` é muito mais leve e robusta. |
| Apagar falhas durante a coleta | Rejeitada. O módulo orquestrador deve focar apenas em baixar dados, registrando até mesmo os erros. A responsabilidade de limpar falhas deve ficar isolada neste Transformer (princípio da Separação de Responsabilidades / Clean Code). |

## Limitações Conhecidas

- **Falsos Positivos de Sucesso:** Se uma página do e-SAJ carregar parcialmente contendo a "Classe", mas falhar no "Foro", a regra atual pode não sinalizar a linha como falha, não enviando o processo para a repescagem.
- **Tamanho Fixo do CNJ:** A lógica de padronização assume fortemente o formato CNJ de 20 dígitos para aplicação da máscara. Formatos históricos muito anômalos podem não ser mascarados corretamente, impactando o cruzamento.

## Exemplo de Uso

```python
from src.transformers.transformer_auditoria_tjsp_capa import FaceAuditoriaTJSP

# Inicializando a auditoria
auditoria = FaceAuditoriaTJSP(
    input_json="caminho/para/base_processos_esperados.json",
    output_csv="caminho/para/bronze_coletados.csv",
    pendentes_file="caminho/para/fila_pendentes.json"
)

# 1. Limpa as falhas e duplicatas do CSV de coleta
falhas, duplicatas = auditoria.auditar_limpar_csv()
print(f"Limpou {falhas} falhas e {duplicatas} duplicatas.")

# 2. Cruza as bases e gera a fila do que ainda falta coletar
total_esperado, total_coletado, total_pendente = auditoria.auditar_e_gerar_pendencias()
print(f"Faltam {total_pendente} processos para finalizar o lote.")
```

## Testes e Validação

- A etapa de deduplicação (drop_duplicates com keep="first") garante segurança idempotente ao pipeline: o scraper pode rodar múltiplas vezes sobre a mesma base e inserir duplicatas no CSV, e o Transformer garantirá o estado íntegro dos dados sem perdas.

## Histórico de Modificações

| Data | Usuário | Alteração |
|------|---------|------------|
| 2026-07-01 | @alexandrehiero | Inicialização da feature de auditoria e mescla de falhas na fila de processamento (feat(auditoria): add error merging and queue processing). |
| 2026-07-01 | @alexandrehiero | Adição da lógica de normalização de números de processos nas auditorias (feat(transformers): normalize process numbers in audits). |
| 2026-07-01 | @alexandrehiero | Correção dos valores de retorno do módulo de auditoria (fix(transformer_auditoria_tjsp_capa): correct return value). |
| 2026-07-01 | @alexandrehiero | Renomeação de classes para clareza e remoção de bibliotecas não utilizadas. |
