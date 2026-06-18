# Scraper TJSP – Capa – `src/scrapers/scraper_tjsp_capa_request.py`

| Metadado                | Valor                                            |
|-------------------------|--------------------------------------------------|
| Data de criação         | 2026-06-10                                       |
| Data de atualização     | 2026-06-14                                       |
| Responsável(is)         | @nickmalexander (doc) · @alexandrehiero (código) |
| Dependências principais | `curl_cffi`, `beautifulsoup4`, `pandas`          |

## Contexto e Motivação

Componente que baixa a página de um processo no e-SAJ e transforma o HTML em dados estruturados (capa, partes, advogados, movimentações e sentenças). É o motor de coleta usado pelo orquestrador `scripts/coleta_PGE_GPDR_tjsp_fase_capa.py`, que cuida da fila de processos e da gravação. Aqui ocorre apenas o *requisitar + interpretar*.

O módulo existe separado por dois motivos que tornam a coleta difícil:

- O e-SAJ fica atrás de uma proteção que bloqueia clientes que parecem robôs (verificação de fingerprint TLS).
- O HTML do tribunal varia conforme o tipo de ação e usa muitos rótulos diferentes para autores, réus e sentenças.

## Decisões de Arquitetura

- **Classe principal:** `FaceTJSPScraper` – responsável por requisição, resolução de múltiplos resultados e parsing.
- **Interface pública:** três métodos – `get_html(url)` (baixa a página), `resolve_multiple_results(html, numero)` (resolve buscas que retornam lista) e `parse_process(html)` (extrai os dados em dicionário).
- **Cliente HTTP:** uso de `curl_cffi` com `impersonate="chrome120"` para passar pela verificação de fingerprint TLS do e-SAJ.
- **Classificação de partes por padrões:** autor/réu identificados por listas de padrões (`padrão_autores`, `padrão_réus`), e não por posição fixa, porque o e-SAJ usa vários rótulos para o mesmo papel (Requerente, Autor, Exequente, Reclamante...).
- **Reservas de layout (fallback):** o parsing tenta um `id` principal e cai numa alternativa quando ele não existe (ex.: tabela de partes — `tableTodasPartes` ou `tablePartesPrincipais` — e campo de classe), cobrindo os diferentes layouts do tribunal.
- **Identificação de sentenças por lista de padrões:** as movimentações são comparadas contra uma lista de padrões de sentença (`padrão_sentenças`) para marcá-las.
- **Separação de responsabilidades:** estratégia de delay/throttling não fica neste módulo – é responsabilidade do script orquestrador, que aplica uma pausa aleatória entre requisições.
- **Tratamento de campos ausentes:** campos inexistentes retornam `NÃO HÁ REGISTRO`; ausência de sentença retorna `[None]`. Em caso de HTML nulo (falha de acesso), `parse_process` retorna `None`.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|-------------|--------------------|
| `httpx` | Mais rápido, mas o e-SAJ verifica o fingerprint TLS da conexão e bloqueia clientes comuns. O `curl_cffi` se passa por um navegador real e por isso passa. O gargalo aqui é o **acesso**, não a velocidade – trocar quebra a coleta. |
| Posição fixa para identificar partes | O e-SAJ usa rótulos variados (Requerente, Autor, Exequente...) e layouts diferentes; posição fixa quebraria entre processos. Optou-se por listas de padrões. |

## Limitações Conhecidas

- **Escopo de instância (apenas 1º grau):** o scraper acessa somente a consulta de 1º grau (`cpopg`). Processos de 2º grau, Colégio ou Turma Recursal (ex.: numeração com sufixo `.90XX` ou `.0000`) não são encontrados nessa base e retornam todos os campos como `NÃO HÁ REGISTRO`.
- **Processos com restrição de acesso:** processos em segredo de justiça ou sob restrição (Resolução 121 do CNJ) exigem senha/identificação e não expõem dados públicos; o scraper retorna `NÃO HÁ REGISTRO`.
- **Sentenças fora do padrão:** um tipo de sentença novo, ainda não previsto na lista `padrão_sentenças`, não é marcado como sentença – fica registrado apenas como movimentação. A lista precisa ser atualizada quando aparecer um caso novo.
- **Captchas:** não há tratamento de captcha (até o momento não foram encontrados na coleta de capa).
- **Dependência de layout:** mudanças estruturais no HTML do e-SAJ podem exigir ajuste dos `id`s e fallbacks usados no parsing.

## Exemplo de Uso

```python
from src.scrapers.scraper_tjsp_capa_request import FaceTJSPScraper

scraper = FaceTJSPScraper()

# Caso 1: URL direta da página do processo (já com o código interno)
html = scraper.get_html(url)
dados = scraper.parse_process(html)

# Caso 2: a partir do número CNJ, via busca (fluxo do orquestrador)
url_busca = f"https://esaj.tjsp.jus.br/cpopg/search.do?cbPesquisa=NUMPROC&dadosConsulta.valorConsulta={numero_cnj}"
html = scraper.get_html(url_busca)
link = scraper.resolve_multiple_results(html, numero_cnj)
if link:
    html = scraper.get_html(link)
dados = scraper.parse_process(html)
```

Estrutura do dicionário retornado por `parse_process()`:

```python
{
    "numero": "0000000-00.0000.0.00.0000",
    "classe": "Procedimento Comum Cível",
    "assunto": "Inclusão de Dependente",
    "foro": "Foro de ...",
    "vara": "0ª Vara Cível",
    "distribuicao": "00/00/0000 às 00:00 ...",
    "controle": "...",
    "area": "Cível",
    "valor": "R$ 00.000,00",
    "outros_assuntos": "...",
    "autores": "Fulano de Tal",
    "advogados_autores": "Advogado X",
    "reus": "Empresa Y",
    "advogados_reus": "Advogado Z",
    "tipo_sentença": ["Julgada Procedente a Ação"],
    "data_sentença": ["00/00/0000"],
    "movimentações": [{"data": "00/00/0000", "tipo": "..."}, ...]
}
```

## Testes e Validação

Execução do orquestrador sobre a base completa, por @alexandrehiero: **273.327 processos**, dos quais **250 retornaram erro (~0,09%)** — taxa de sucesso de ~99,91%.

## Histórico de Modificações

| Data       | Usuário          | Alteração |
|------------|------------------|-----------|
| 2026-04-29 | @alexandrehiero  | Criação do scraper TJSP capa |
| 2026-06-10 | @nickmalexander  | Criação da documentação do módulo |
| 2026-06-14 | @nickmalexander  | Atualização para formato ADR |