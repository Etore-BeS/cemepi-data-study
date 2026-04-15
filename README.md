# cemepi-data-study

Projeto de estudo e análise de dados do CEMEPI utilizando Python, Jupyter Notebooks e análise de similaridade.

---

## Estrutura do Repositório

```
.
├── data/                      # Dados brutos e processados
│   └── PGE.GPDR.json         # Insira manualmente os dados trabalhados por questão de segurança e armazenamento do git
├── notebooks/                 # Notebooks Jupyter para análises
│   └── estudo-similarididade/ # Diretório para cada Estudo criado
│       └── estudo_similaridade.ipynb
├── scripts/                   # Scripts utilitários e automações
├── src/                       # Código fonte do projeto (módulos Python)
├── recursos/                  # Recursos auxiliares (imagens, documentos)
│   └── tutoria-20260415/
├── pyproject.toml            # Configuração do projeto e dependências
├── .python-version           # Versão do Python (3.13)
└── .gitignore               # Arquivos ignorados pelo Git
```

### Descrição das Pastas

| Pasta          | Descrição                                                                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data/`      | Contém os datasets.**Nota:** Os arquivos em `data/` são ignorados pelo Git (exceto este README) por questões de tamanho e privacidade. |
| `notebooks/` | Notebooks Jupyter com análises exploratórias e experimentos.                                                                                    |
| `scripts/`   | Scripts Python standalone para processamento, ETL, etc.                                                                                           |
| `src/`       | Módulos Python reutilizáveis. Importe como `from src import modulo`.                                                                          |
| `recursos/`  | Materiais de apoio, tutoriais, imagens, documentação.                                                                                           |

---

## Pré-requisitos

- **Python 3.12** 
- **uv** - Gerenciador de pacotes e ambientes virtuais moderno para Python

### Instalando o uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip
pip install uv
```

---

## Como Usar

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd cemepi-data-study
```

### 2. Configure o Ambiente Virtual

O `uv` vai automaticamente criar e gerenciar o ambiente virtual baseado na versão em `.python-version`:

```bash
# O uv detecta a versão do Python e cria o ambiente
uv sync
```

Ou, para criar manualmente:

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate    # Windows
```

### 3. Instale as Dependências

```bash
# Instala todas as dependências do pyproject.toml
uv sync
```

### 4.  Execute Scripts

```bash
# Executa um script com o ambiente do projeto
uv run python scripts/meu_script.py
```

---

## Como Adicionar Pacotes

### Adicionar Dependências Principais

```bash
# Adiciona um pacote às dependências do projeto
uv add pandas
uv add numpy scikit-learn matplotlib

# Com versão específica
uv add "pandas>=2.0.0"
```

### Adicionar Dependências de Desenvolvimento

```bash
# Pacotes apenas para desenvolvimento (testes, lint, etc.)
uv add --dev pytest black ruff mypy
```

### Adicionar Pacotes com Recursos Opcionais

```bash
# Exemplo: Jupyter com suporte a widgets
uv add "jupyterlab[recommended]"
```

### Atualizar Pacotes

```bash
# Atualiza todas as dependências
uv sync --upgrade

# Atualiza pacote específico
uv add --upgrade pandas
```

### Remover Pacotes

```bash
uv remove pandas
```

---

## Desenvolvimento

### Executar Código em Desenvolvimento

```bash
# Executa Python com o ambiente do projeto
uv run python

# Executa um módulo
uv run python -m src.meu_modulo
```

---

## Configuração do Projeto (`pyproject.toml`)

```toml
[project]
name = "cemepi-data-study"
version = "0.1.0"
description = "Projeto de estudo de dados do CEMEPI"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    # Adicione dependências aqui via `uv add`
]

[project.optional-dependencies]
dev = [
    # Dependências de desenvolvimento
]
```

---

## Fluxo de Trabalho Recomendado

1. **Sempre ative o ambiente** ou use `uv run` antes de executar código
2. **Adicione novas dependências** com `uv add` (não instale diretamente com pip)
3. **Salve notebooks** com outputs limpos antes de commitar
4. **Coloque datasets grandes** em `data/` (eles são `.gitignore`d automaticamente)
5. **Adicione código reutilizável** em `src/` como módulos Python
6. **Scripts pontuais** vão em `scripts/`

---

## Convenções

- Use **Python 3.12+** (especificado em `.python-version`)
- Nomeie notebooks descritivamente: `estudo_*.ipynb`, `analise_*.ipynb`
- Documente funções em `src/` com docstrings
- Não commite arquivos de dados grandes (já configurado em `.gitignore`)
- Não commite o ambiente virtual `.venv/` (já configurado em `.gitignore`)

---

## Dúvidas?

Consulte a [documentação do uv](https://docs.astral.sh/uv/) para mais detalhes sobre o gerenciador de pacotes.
