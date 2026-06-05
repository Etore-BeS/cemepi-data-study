# Coleta de Dados de Capa - TJSP (PGE GPDR)

## 1. Demanda - Causa - Necessidade - Problema
O projeto possui uma base de dados interna (PGE GPDR) contendo 273.327 processos. A demanda consistiu na coleta dos metadados de capa desses processos no site público do e-SAJ para posterior enriquecimento da base interna pré-existente. 

## 2. Contexto
Os metadados de capa dos processos foram coletados por meio do sistema e-SAJ do Tribunal de Justiça de São Paulo (TJSP). Após a extração, os dados foram tratados para enriquecer e complementar a base PGE GPDR.

## 3. Análise
Para realizar o processo, foi necessário, primeiramente, a construção de uma função de coleta desses metadados de capa, que seguiu um padrão com base na URL de busca do site do e-SAJ e no número único de cada processo. 

Além disso, para que a cada execução da função a coleta não retornasse do ponto inicial, e sim do ponto em que havia parado, foi implementado um mecanismo de controle de estado (*checkpoint*). Isso garante que processos já coletados com sucesso sejam ignorados nas execuções seguintes. 

Por fim, a conversão de DOM (HTML bruto) para dados estruturados exigiu um módulo isolado e tolerante a falhas (*parsing* dinâmico), capaz de extrair autores, réus, movimentações e sentenças, mesmo com variações na estrutura da página do tribunal.

## 4. Solução
Foi desenvolvido um Script Orquestrador de Coleta (*Scraper*) em Python. Ele lê a base de processos a serem coletados, cruza com um arquivo físico de histórico de sucessos (CSV) e seleciona apenas os processos faltantes. Os dados extraídos do TJSP são limpos, formatados e adicionados ao CSV final, garantindo um consumo quase nulo de memória RAM.

----------------

## 5. Arquitetura

### Natureza e Função
* **Natureza:** Processador de Ingestão em Lote (*Batch Scraper*) modularizado e com controle de estado nativo.
* **Função:** Orquestrar o ciclo de extração de dados: Ler fila -> Requisitar HTML -> Delegar Parsing -> Salvar no disco.

### Bibliotecas e Dependências

A arquitetura foi dividida entre o script orquestrador (`coleta_PGE_GPDR_tjsp_fase_capa.py`) e o motor de extração (`scraper_tjsp_capa_request.py`). As principais bibliotecas utilizadas foram:

* **`sys`**: Biblioteca nativa do Python responsável por interagir com o interpretador. Foi utilizada para manipular o `sys.path`, permitindo que o script importe módulos de outras pastas do projeto (como a camada `src`) garantindo a correta execução independentemente de onde o terminal for aberto.

* **`json`**: Leitura da fila de processos originais a partir da base (Camada Bronze).

* **`pandas` (`pd`)**: Ferramenta de manipulação de dados estruturados. Foi utilizada de duas formas:
  1. Para leitura otimizada apenas da chave primária na fase de *checkpoint*.
  2. Para organizar o dicionário de dados extraídos e convertê-lo em uma linha contínua que é anexada ao arquivo CSV de saída.

* **`os` / `pathlib`**: Bibliotecas nativas focadas na manipulação segura de rotas de diretórios e verificação física da existência de arquivos no Sistema Operacional antes de tentar abri-los.

* **`time` / `random`**: Injeção de atrasos assimétricos (*delays*) de forma aleatória para simular o comportamento humano entre as requisições e evitar bloqueios por limites de taxa (*Rate Limit*).

------------------

## 6. Funcionamento e Comportamento

### Fluxograma de Execução
1. **Inicialização:** Definição dos caminhos de entrada (`PGE.GPDR.json`), que é o arquivo com os dados da base de pesquisa, e de saída (`coleta_tjsp_resultados.csv`), que armazenará os metadados extraídos.

2. **Verificação de Estado (*Checkpoint*):** A função `carregar_ja_coletados()` carrega apenas a coluna "Processo" do CSV de saída para economizar RAM e retorna um *Set* (conjunto) contendo os números já processados.

3. **Filtro Anti-Redundância:** A lista do JSON é varrida; os processos cujo número já exista no *Set* de coletados são descartados da fila atual.

4. **Loop de Coleta:** Para cada processo restante:
   * Montagem da URL de busca do TJSP (e-SAJ).
   * Requisição do HTML via módulo customizado `scraper`.
   * Tratamento de redirecionamentos (se a busca retornar uma lista, a função `resolve_multiple_results` encontra o link exato do processo).
   * *Parsing* (extração fina) dos metadados de capa, varredura de tabelas para resgate de autores/réus, formatação do histórico de movimentações e categorização da sentença.

5. **Gravação Incremental (*Append*):** O dicionário resultante é convertido em DataFrame (uma única linha) e salvo imediatamente no disco rígido (`mode='a'`).

6. **Espera Assimétrica:** O script entra em hibernação randômica entre $3.5$ e $7.2$ segundos antes de iterar para a próxima URL.

### Exemplo de Estrutura de Dados (Output)
Os dados são exportados de forma tabular em formato CSV, contendo as seguintes colunas padronizadas:
`Processo, Classe, Assunto Principal, Status/Data Dist., Foro, Vara, Autores, Advogados Autores, Réus, Advogados Réus, Valor Da Ação, Outros Assuntos, Tipo de Sentença, Data Sentença, Movimentações, URL_Consulta`

### Decisões Técnicas e Notas Justificativas

* **Uso de Sets (`set()`) para Checkpoint:**
  * *Nota:* Estruturas do tipo Set em Python possuem complexidade temporal de busca O(1). Comparar a fila de pendentes contra um Set contendo centenas de milhares de registros é um processo instantâneo, superando em muito a performance de listas padrão, cuja busca possui complexidade O(n).

* **Escrita Direta em Disco (I/O Streaming):**
  * *Nota:* O método `df_linha.to_csv(..., mode='a')` salva cada processo individualmente logo após a extração da web. Isso garante que, em caso de queda de energia ou interrupção forçada do terminal, os dados processados até aquele exato milissegundo estejam salvos de forma permanente.

* **Sleep Variável (3.5s a 7.2s):**
  * *Nota:* Requisições automatizadas em intervalos fixos (ex: requisições a cada 5 segundos cravados) são rapidamente detectadas por *firewalls* analíticos. A biblioteca `random` injeta entropia aos *delays*, imitando o comportamento assimétrico da navegação humana.
