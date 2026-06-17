# Estudo de Similaridade

| Metadado            | Valor                                      |
|---------------------|--------------------------------------------|
| Data de criação     | 2026-05-21                                 |
| Data de atualização | 2026-05-21                                 |
| Autor(es)           | @MauroJunior1         |
| Notebook original   | `notebooks/estudo-similaridade/normalizacao_assuntos.ipynb`    |

## Contexto e Motivação

A base PGE GPDR possui uma coluna chamada Assuntos, responsável por armazenar os assuntos jurídicos associados a cada processo. Durante a análise da base foram identificadas diversas variações textuais e inconsistências de preenchimento, inviabilizando análises agregadas.

## Decisões Técnicas

- **Biblioteca de similaridade escolhida:** `thefuzz` (por leveza e bom custo‑benefício)
- **Threshold utilizado:** 95 (justificativa: capturar apenas variações muito pequenas, como plural e hífen)
- **Pré‑processamento:** remoção de acentos, lower case, eliminação de pontuação (código no notebook)
- **Segmentação dos assuntos**: utilização dos delimitadores " - " e " / " para comparar os assuntos individualmente.
- **Pós‑processamento manual:** dicionário de correções para falsos positivos (códigos de lei e "recalculo" vs "calculo")

## Resultados Alcançados

*Quais foram os principais números ou achados?*  
- Foram criados 10 agrupamentos diferentes para variáveis.
- 47442 processos foram normalizados trocando termos variados por seu valor canônico .
véis no Dicionário da Verdade.

## Aprendizados e Lições

*O que deu certo? O que não deu?*  
- O threshold 95 foi eficaz para evitar agrupamentos incorretos, mas ainda considerava algumas diferenças como equivalentes (ex: "LC 300/00" vs "LC 400/00").  
- Em versões futuras, experimentar `token_sort_ratio` em vez de `ratio`.

## Decisões Pendentes ou Encaminhamentos

- [X] Validar o dicionário final com o time de domínio (Beto/Étore).
- [ ] Automatizar o processo via script.

## Como reproduzir este estudo

```bash
# Comandos para instalar dependências e executar o notebook
uv add thefuzz unidecode pandas
jupyter notebook notebooks/estudo-similaridade/normalizacao_assuntos.ipynb
```

## Referências

- [Documentação do thefuzz](https://github.com/seatgeek/thefuzz)
