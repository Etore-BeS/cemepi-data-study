# Configuração do Ambiente

Guia para pesquisadores configurarem o ambiente local do projeto `cemepi-data-study`.

## Pré-requisitos

- **Python 3.12+** (versão em `.python-version`)
- **uv** — gerenciador de pacotes e ambientes virtuais

### Instalando o uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv
```

## Configuração inicial

```bash
git clone <url-do-repositorio>
cd cemepi-data-study
uv sync
```

O `uv sync` cria o ambiente virtual (`.venv/`) e instala as dependências de `pyproject.toml`.

## Executando código

```bash
# Scripts
uv run python scripts/coleta_PGE_GPDR_tjsp_fase_capa.py

# Python interativo
uv run python

# Módulos
uv run python -m src.scrapers.scraper_tjsp_capa_request
```

## Dados locais

Coloque datasets em `data/`. Por padrão, arquivos em `data/` são ignorados pelo Git (privacidade e tamanho).

Exemplos de arquivos esperados:

| Arquivo | Uso |
|---------|-----|
| `data/PGE.GPDR.json` | Base de processos da PGE (entrada de coleta e normalização) |
| `data/coleta_tjsp_resultados.csv` | Saída incremental do script de coleta TJSP |
| `data/PGE.GPDR_normalizado.json` | Saída do estudo de similaridade (não versionar) |

## Adicionando dependências

```bash
# Dependência principal
uv add pandas

# Dependência de desenvolvimento
uv add --dev pytest

# Com versão específica
uv add "thefuzz>=0.22.0"
```

Sempre use `uv add` em vez de `pip install` direto — isso mantém `pyproject.toml` e `uv.lock` sincronizados.

## Documentação (MkDocs)

```bash
# Servidor local com live-reload
uv run mkdocs serve

# Build estático (pasta site/)
uv run mkdocs build
```

A documentação fica em `docs/`. Veja a [página inicial](../index.md) para a estrutura de ADRs.

## Documentando seu trabalho

Ao criar um novo artefato, copie o template ADR correspondente:

| Tipo | Template | Destino |
|------|----------|---------|
| Notebook | [`docs/notebooks/template_notebook.md`](../notebooks/template_notebook.md) | `docs/notebooks/<nome>.md` |
| Módulo `src/` | [`docs/src/template_src.md`](../src/template_src.md) | `docs/src/<nome>.md` |
| Script | [`docs/scripts/template_script.md`](../scripts/template_script.md) | `docs/scripts/<nome>.md` |

Registre a nova página em `mkdocs.yml` (raiz do repositório) e abra PR com código + ADR juntos.

## Referências

- [Documentação do uv](https://docs.astral.sh/uv/)
- `README.md` na raiz do repositório
