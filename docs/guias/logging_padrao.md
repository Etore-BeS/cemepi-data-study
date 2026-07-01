# Padrão de Logging

Guia normativo para logging em scripts de pipeline do projeto. Scripts existentes podem ainda usar `print()` — ao criar ou refatorar scripts, adote este padrão.

## Objetivos

- Registrar progresso, falhas recuperáveis e erros de forma consistente.
- Persistir logs em arquivo para auditoria de coletas longas.
- Manter compatibilidade visual com os prefixos já usados no projeto: `[OK]`, `[FALHA]`, `[ERRO]`, `[AVISO]`.

## Estrutura recomendada

```python
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "coleta.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)
```

## Convenção de níveis

| Nível | Quando usar | Exemplo |
|-------|-------------|---------|
| `INFO` | Progresso normal, sucesso | `logger.info("[OK] Processo coletado: %s", num)` |
| `WARNING` | Falha recuperável, formato inesperado | `logger.warning("[FALHA] HTML vazio: %s", num)` |
| `ERROR` | Exceção capturada, item ignorado | `logger.error("[ERRO] Processo %s: %s", num, e)` |
| `DEBUG` | Detalhes de parsing (opcional) | URLs, tamanho de HTML |

## Prefixos no mensagem

Mantenha os prefixos entre colchetes no texto da mensagem para facilitar `grep` em arquivos de log:

```python
logger.info("[OK] Processo coletado: %s", numero)
logger.warning("[AVISO] Arquivo CSV com formato antigo detectado")
logger.warning("[FALHA] HTML vazio ou erro de parsing: %s", numero)
logger.error("[ERRO] Processo %s: %s", numero, exc)
```

## Interrupção graciosa

Em scripts com checkpoint (ex.: append em CSV), trate `KeyboardInterrupt`:

```python
try:
    executar_coleta()
except KeyboardInterrupt:
    logger.warning("[AVISO] Coleta interrompida pelo usuário. Dados já salvos permanecem no arquivo de saída.")
```

## Diretório `logs/`

- Logs ficam em `logs/<nome-do-script>.log` na raiz do projeto.
- A pasta `logs/` está no `.gitignore` — não versionar arquivos de log.
- Crie `logs/` automaticamente no script (`mkdir(exist_ok=True)`).

## Migração de `print()` para `logging`

| Antes (`print`) | Depois (`logging`) |
|-----------------|-------------------|
| `print(f"[OK] ...")` | `logger.info("[OK] ...")` |
| `print(f"[FALHA] ...")` | `logger.warning("[FALHA] ...")` |
| `print(f"[ERRO] ...")` | `logger.error("[ERRO] ...")` |
| `print(f"[AVISO] ...")` | `logger.warning("[AVISO] ...")` |

## Referências

- [Documentação logging — Python](https://docs.python.org/3/library/logging.html)
- [Template de script](../scripts/template_script.md) — seção "Logs e Monitoramento"
