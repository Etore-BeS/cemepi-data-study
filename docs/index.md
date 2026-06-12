# Documentação CEMEPI — Dados

Projeto de estudo e análise de dados do CEMEPI. Esta documentação registra decisões técnicas, contexto e aprendizados ao lado do código — no formato de **ADRs (Architecture Decision Records)**.

## Estrutura

```
docs/
├── index.md                 # Esta página
├── notebooks/               # ADRs de notebooks de estudo
│   ├── template_notebook.md
│   └── estudo-similaridade.md
├── src/                     # ADRs de módulos reutilizáveis
│   └── template_src.md
├── scripts/                 # ADRs de scripts de pipeline
│   └── template_script.md
└── guias/                   # Guias complementares
    ├── configuracao_ambiente.md
    └── logging_padrao.md
```

## Como documentar

1. **Notebook** — ao criar um estudo em `notebooks/`, copie [`notebooks/template_notebook.md`](notebooks/template_notebook.md) para `docs/notebooks/<nome>.md` e preencha.
2. **Módulo `src/`** — copie [`src/template_src.md`](src/template_src.md) para `docs/src/<nome>.md`.
3. **Script** — copie [`scripts/template_script.md`](scripts/template_script.md) para `docs/scripts/<nome>.md`.

Em cada ADR, registre:

- Por que a decisão foi tomada
- Alternativas consideradas e rejeitadas
- Limitações e aprendizados
- Como reproduzir ou executar

Adicione a nova página em `mkdocs.yml` (raiz do repositório) e abra PR com código + documentação juntos.

## Templates e exemplos

| Tipo | Template | Exemplo preenchido |
|------|----------|-------------------|
| Notebook | [template_notebook.md](notebooks/template_notebook.md) | [estudo-similaridade.md](notebooks/estudo-similaridade.md) |
| Módulo `src/` | [template_src.md](src/template_src.md) | — |
| Script | [template_script.md](scripts/template_script.md) | — |

## Guias

- [Configuração do ambiente](guias/configuracao_ambiente.md) — `uv`, dependências, dados locais
- [Padrão de logging](guias/logging_padrao.md) — convenções para scripts de pipeline

## Visualizar localmente

```bash
uv run mkdocs serve
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000) no navegador.
