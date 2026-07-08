# Pipeline Silver PGE GPDR – `scripts/silver_PGE_GPDR.py`

| Metadado                | Valor                |
|-------------------------|--------------------- |
| Data de criação         | 2026-07-01           |
| Data de atualização     | 2026-07-03           |
| Responsável(is)         | @alexandrehiero      |
| Dependências principais | `sys`, `pathlib`, `PGE_GPDRTransformerSilver` |

## Contexto e Motivação

Dentro da arquitetura de Data Lake do projeto, os dados não vêm apenas do web scraping, mas também de bases internas já existentes (como o dataset bruto fornecido pela PGE). Este script é o orquestrador responsável por ingerir o arquivo JSON bruto da PGE (Camada Bronze) e promovê-lo para a Camada Silver, acionando as lógicas de padronização (como a aplicação da máscara de CNJ) e encapsulamento de metadados. Ele prepara a base primária para o cruzamento futuro (Join) com os dados do Tribunal.

## Decisões de Pipeline

- **Arquitetura Orientada a Orquestração (Controller):** O script mantém fidelidade absoluta ao princípio da Separação de Responsabilidades (SoC). Ele atua unicamente como um disparador, sem conhecimento interno sobre *como* os dados da PGE estão estruturados.
- **Resolução de Caminhos Agnóstica ao SO:** A utilização de `Path(__file__).resolve().parent.parent` garante que o orquestrador localize a pasta raiz do projeto de forma infalível, seja rodando em instâncias Linux ou no Windows local, eliminando caminhos estáticos ou relativos frágeis.
- **Feedback Síncrono:** Emite logs enxutos e diretos via `print()` para o terminal, indicando o início do processo e a volumetria exata de documentos processados (ex: `[-] 273327 documentos do IC padronizados...`).

## Como Executar

```bash
# A partir da raiz do projeto, utilizando o gerenciador de pacotes uv
uv run python scripts/silver_PGE_GPDR.py
```

## Principais Parâmetros (constantes no código)

| Constante | Valor | Descrição |
|-----------|-------|-------------|
| `PROJECT_ROOT` | Dinâmico (`pathlib`) | Resolve a raiz do repositório para ancorar os diretórios de dados. |
| `input_ic_json` | `data/PGE.GPDR.json` | Arquivo de origem (raw) gerado pelo time da PGE. |
| `output_silver_ic` | `data/silver_dados_PGE_GPDR.json` |  Arquivo de destino padronizado e limpo na camada Silver. |

## Logs e Monitoramento
- A comunicação ocorre estritamente via terminal (CLI).
- O indicador de sucesso baseia-se no retorno da função `json_pge_para_silver()`, que devolve um inteiro (qtd) com o total de registros convertidos, garantindo que o operador valide rapidamente se toda a base foi migrada.

## Falhas Conhecidas e Workarounds
- **Problema:** Ausência de tratamento de exceções (Bloco try-except). Se o arquivo `PGE.GPDR.json` estiver corrompido, bloqueado por permissão de I/O ou ausente, o script crashará e ejetará um stack trace no console.
    **Workaround:** Atualmente, pressupõe-se que a base inicial está estática e íntegra no repositório local.

## Decisões Futuras
- [ ] Implementar bloco `try...except` para captura graciosa de erros de `FileNotFoundError` ou `json.JSONDecodeError`.
- [ ] Integrar configuração global de logs (logging) para rastrear o tempo de execução do pipeline em arquivos .log.
- [ ] Preparar a estrutura do script para ser encapsulada em uma DAG de Airflow ou Prefect, caso o pipeline da Iniciação Científica evolua para uma arquitetura orquestrada em nuvem.

## Relação com Outros Artefatos
- Depende: Da classe de domínio `PGE_GPDRTransformerSilver` localizada em `src/transformers/transformer_silver_PGE_GPDR.py`.
- Alimenta: O arquivo estruturado `silver_dados_PGE_GPDR.json`, que é um dos pré-requisitos fundamentais para o funcionamento do Agregador (Camada Gold).

## Lições Aprendidas
- Manter orquestradores (scripts) curtos e declarativos facilita a leitura e manutenção do projeto por outros pesquisadores no laboratório.
- A nomenclatura semântica das camadas (Bronze, Silver, Gold) refletida diretamente no nome dos scripts (`silver_PGE_GPDR.py`) gera uma topologia de diretórios autoexplicativa.

## Histórico de Movimentações

| Data       | Usuário          | Alteração |
|------------|------------------|-----------|
| 2026-06-20 | @alexandrehiero  | Criação do script orquestrador da camada Silver (Base PGE GPDR) com injeção dinâmica de caminhos via pathlib. |
| 2026-07-03 | @alexandrehiero  | Criação da documentação do script |
