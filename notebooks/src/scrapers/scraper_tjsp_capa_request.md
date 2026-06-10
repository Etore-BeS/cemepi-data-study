# Scraper TJSP - Capa

Componente que **baixa a página de um processo no e-SAJ e transforma o HTML em
dados** (capa, partes, advogados, movimentações e sentenças). É o motor usado
pelo orquestrador de coleta (`coleta_PGE_GPDR_tjsp_fase_capa.py`), que cuida da
fila de processos e da gravação; aqui só acontece o *requisitar + interpretar*.

## Para que serve

A coleta de capa precisa, processo a processo, acessar o e-SAJ e ler os dados.
Dois pontos tornam isso difícil e justificam este motor existir separado:

- O e-SAJ fica atrás de uma proteção que **bloqueia clientes que parecem robôs**.
- O HTML do tribunal **varia** conforme o tipo de ação e usa muitos rótulos
  diferentes para autores, réus e sentenças.

Este arquivo resolve esses dois pontos e devolve os dados já organizados.

## Como usar

A classe expõe três métodos. O uso básico é: criar o scraper, baixar o HTML e
interpretar.

```python
from scraper_tjsp_capa_request import FaceTJSPScraper

scraper = FaceTJSPScraper()

html = scraper.get_html(url)          # baixa a página do processo
dados = scraper.parse_process(html)   # devolve um dicionário com os dados
```

Quando a URL é uma **busca** (e não a página direta do processo), o e-SAJ pode
retornar uma lista de resultados. Nesse caso, antes de interpretar, use:

```python
link = scraper.resolve_multiple_results(html, numero_do_processo)
```

para achar o link exato do processo e então baixar a página certa.

## Como funciona (passo a passo)

1. `get_html()` baixa o HTML da página, fingindo ser um navegador real para
   passar pela proteção do site.
2. Se a página for uma lista, `resolve_multiple_results()` acha o link do
   processo exato.
3. `parse_process()` lê o HTML e extrai os dados em três blocos:
   - **Cabeçalho** — número, classe, assunto, foro, vara, valor, etc.
   - **Partes** — separa autores e réus (e os advogados de cada lado).
   - **Movimentações** — lista todas e marca quais são sentenças.

## O que você recebe

`parse_process()` devolve um **dicionário**. Campos que não existem no processo
vêm como `NÃO HÁ REGISTRO`; quando não há sentença, vem `[None]`.

```python
{
    "numero": "0000000-00.0000.0.00.0000",
    "classe": "Procedimento Comum Cível",
    "assunto": "Indenização por Dano Material",
    "foro": "Foro de ...",
    "vara": "0ª Vara Cível",
    "distribuicao": "00/00/0000 às 00:00 ...",
    "valor": "R$ 00.000,00",
    "autores": "Fulano de Tal",
    "advogados_autores": "Advogado X",
    "reus": "Empresa Y",
    "advogados_reus": "Advogado Z",
    "tipo_sentença": ["Julgada Procedente a Ação"],
    "data_sentença": ["00/00/0000"],
    "movimentações": [{"data": "00/00/0000", "tipo": "..."}, ...]
}
```

## Decisões técnicas e observações

- **Usa `curl_cffi`, não `httpx`.** Mesmo o `httpx` sendo mais rápido, o e-SAJ
  verifica a "impressão digital" da conexão (TLS) e bloqueia clientes comuns. O
  `curl_cffi` se passa por um navegador real (`impersonate="chrome120"`) e por
  isso passa. **Trocar por `httpx` quebra a coleta** — o problema aqui é o
  acesso, não a velocidade.
- **Padrões para identificar as partes.** O e-SAJ usa vários nomes para o mesmo
  papel (Requerente, Autor, Exequente, Reclamante...). Por isso a classificação
  de autor/réu é feita por listas de padrões, e não por posição fixa.
- **Reservas de layout.** O parsing tenta um `id` principal e cai numa
  alternativa quando ele não existe (ex.: tabela de partes e o campo de classe),
  porque o tribunal tem layouts diferentes entre processos.
- **Sentença por lista de padrões.** Um tipo de sentença novo, ainda não
  previsto na lista, não será marcado como sentença — só registrado como
  movimentação. Atualizar a lista quando aparecer um caso novo.
