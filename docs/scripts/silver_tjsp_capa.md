# Pipeline Silver TJSP Capa – `scripts/silver_tjsp_capa.py`

| Metadado                | Valor                |
|-------------------------|----------------------|
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-03           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `pathlib`, `FaceTransformerSilverTJSP`   |

## Contexto e Motivação

Este script executa a promoção dos dados da camada Bronze (bruta) para a camada Silver (estruturada). Ele é necessário para automatizar a extração dos dados tabulares coletados via web scraping (`coleta_tjsp_resultados.csv`) e convertê-los em um formato hierárquico e tipado (`silver_dados_capa_tjsp.json`), preparando o dataset com um *Schema-on-Read* compatível com bancos de dados orientados a documentos (como MongoDB).

## Decisões de Pipeline

- **Isolamento de Regras de Negócio (Controller Pattern):** O script não contém lógicas de parsing ou regex. Ele atua estritamente como um orquestrador, delegando toda a complexidade de transformação para a classe `FaceTransformerSilverTJSP` instanciada a partir da camada `src`.
- **Injeção de Caminhos Dinâmicos:** O uso robusto da biblioteca `pathlib` (`PROJECT_ROOT = Path(__file__).resolve().parent.parent`) garante que os caminhos absolutos dos arquivos de entrada e saída sejam resolvidos dinamicamente, evitando erros de *File Not Found* dependendo de qual diretório o terminal foi aberto.
- **Tratamento de Exceções Gracioso:** A execução do método principal `transformar_csv_para_silver()` está encapsulada em um bloco `try...except`. Em caso de corrupção I/O ou quebra de memória, o script intercepta o erro fatal e exibe uma mensagem amigável no terminal, impedindo o vazamento do *stack trace* bruto.

## Como Executar

```bash
# A partir da raiz do projeto, utilizando o gerenciador de pacotes uv
uv run python scripts/silver_tjsp_capa.py
```

## Principais Parâmetros (constantes no código)

| Constante | Valor | Descrição |
|-----------|-------|-------------|
| `PROJECT_ROOT` | Caminho raiz dinâmico | Raiz calculada via `Path(__file__)` |
| `arquivo_csv` | `data/coleta_tjsp_resultados.csv` | Arquivo Bronze (input) gerado pelo Scraper. |
| `arquivo_silver` | `data/silver_dados_capa_tjsp.json` |  Arquivo Silver (output) no formato JSON Lines. |


## Logs e Monitoramento
- A interface de linha de comando (CLI) adota recursos visuais (emojis e delimitadores) para facilitar a identificação visual do estágio do pipeline durante execuções em lote.
- O feedback de conclusão fornece o número exato de documentos processados com sucesso, servindo como uma rápida auditoria visual de volumetria.

## Falhas Conhecidas e Workarounds
- **Problema:** Se o arquivo `coleta_tjsp_resultados.csv` não existir ou estiver bloqueado por outro processo (ex: um Excel aberto), o script lançará uma exceção fatal.
    **Workaround:** O bloco except captura a falha e avisa o operador sem travar processos paralelos. O usuário deve garantir que o scraper finalizou antes de iniciar a transformação.


## Decisões Futuras
- [ ] Substituir os `print()` nativos por um logger robusto (como loguru ou logging) para persistir o histórico de execuções em arquivos `.log`.
- [ ] Implementar suporte a passagem de argumentos via CLI (ex: argparse ou click) para permitir que o usuário defina caminhos de arquivos personalizados (ex: `python silver_tjsp_capa.py --input arquivo.csv`).

## Relação com Outros Artefatos
- Depende: Do módulo `src/transformers/transformer_json_tjsp_capa.py` e do arquivo `data/coleta_tjsp_resultados.csv`.
- Alimenta: O pipeline da camada Gold (agregadores), disponibilizando a base limpa do TJSP.

## Lições Aprendidas
- O uso do padrão de Orquestrador deixa o código extremamente limpo (Clean Code) e legível. Modificações na regra de negócio do JSON não exigem nenhuma alteração neste script de disparo.
- Mensagens de terminal bem formatadas são fundamentais para a "Developer Experience" (DX), tornando a monitoria manual do projeto mais agradável e compreensível.

## Histórico de Movimentações

| Data       | Usuário          | Alteração |
|------------|------------------|-----------|
| 2026-06-20 | @alexandrehiero  | Criação do script orquestrador da camada Silver (TJSP Capa) com injeção dinâmica de caminhos via pathlib. |
| 2026-07-03 | @alexandrehiero  | Criação da documentação do script |
