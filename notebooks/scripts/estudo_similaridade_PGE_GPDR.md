# Estudo de Similaridade - PGE GPDR

## 1. Demanda - Causa - Necessidade - Problema
Recebemos uma base de dados do PGE GPDR na qual continha milhares de processos e suas informações. Ao analisar o arquivo notamos uma clara inconsistência na coluna "Assuntos", onde haviam variáveis de termos que tinham o mesmo significado.

A demanda consistiu em identificar esses problemas e desenvolver um processo de normalização capaz de padronizar automaticamente os assuntos.

## 2. Contexto
Os dados utilizados estão armazenados no arquivo 'PGE.GPDR.json', que contém informações processuais. Cada processo possui a coluna "Assuntos", composta por classificações jurídicas listadas em uma única string.

Ao longo da construção da base, diferentes formas de preenchimento foram incorporadas aos dados, resultando em múltiplas representações para assuntos equivalentes. Então uma normalização foi desenvolvida com o objetivo de tornar essas variações em algo padronizado, aumentando a facilidade de análise dos dados.

## 3. Análise
Inicialmente foi realizada uma etapa de limpeza textual, incluindo conversão para minúsculas, remoção de acentos, normalização de espaços e remoção controlada de caracteres especiais.

Depois foi feita uma separação dos itens das listas para proporcionar uma análise mais profunda, para isso foi notado que a base usa " - " e " / " como segmentação.

A identificação de possíveis equivalências foi realizada utilizando a biblioteca 'thefuzz', através do cálculo de similaridade textual. Também foram adicionadas regras específicas para ignorar comparações envolvendo números e casos particulares como "cálculo" e "recálculo".

## 4. Solução
Foi desenvolvido um processo de normalização em Python baseado em 'Fuzzy Matching'. Os assuntos semelhantes identificados foram revisados manualmente e organizados em um dicionário da verdade contendo os termos canônicos e suas respectivas variações.

Após a validação, as variações foram substituídas diretamente na coluna "Assuntos" e o resultado foi exportado para o arquivo 'PGE.GPDR_normalizado.json'.

## 5. Arquitetura

### Natureza e Função
* **Natureza:** Processador de Normalização de Dados Textuais.

* **Função:** Identificar variações de escrita e padronizar os assuntos da base PGE GPDR.

### Bibliotecas e Dependências
* **'json'**: Leitura da base original e geração do arquivo normalizado.

* **'pandas'** (**'pd'**): Manipulação da base de dados e processamento da coluna "Assuntos".

* **'re'**: Limpeza textual, segmentação dos assuntos e aplicação de filtros específicos.

* **'unidecode'**: Remoção de acentos e padronização dos textos.

* **'thefuzz'**: Cálculo de similaridade textual entre os assuntos.



## 6. Funcionamento e Comportamento

### Fluxograma de Execução
**1. Leitura da Base**: Carregamento do arquivo 'PGE.GPDR.json'.

**2. Pré-processamento**: Limpeza e padronização dos textos da coluna "Assuntos".

**3. Segmentação**: Separação dos assuntos em itens individuais.

**4. Comparação de Similaridade**: Identificação de possíveis equivalências utilizando 'Fuzzy Matching'.

**5. Construção do Dicionário Verdade**: Definição dos termos canônicos e suas variações.

**6. Normalização**: Substituição das variações pelos termos padronizados.

**7. Exportação**: Geração do arquivo 'PGE.GPDR_normalizado.json'.

### Exemplo de Estrutura de Dados (Output)
Os dados são exportados em formato JSON preservando a estrutura original dos processos, com a coluna "Assuntos" contendo apenas os termos padronizados.

### Decisões Técnicas e Notas Justificativas

* **Segmentação dos Assuntos**:
*Nota*: A comparação individual dos assuntos reduziu falsos positivos observados na comparação da string completa.

* **Threshold de Similaridade Igual a 95**:
*Nota*: Apresentou melhor equilíbrio entre identificação de variações legítimas e redução de agrupamentos incorretos como leis complementares cuja diferença era apenas um número.

* **Uso de Dicionário Verdade**:
*Nota*: Garantiu controle manual sobre os termos canônicos utilizados na normalização.

* **Substituição Direta da Coluna Original**:
*Nota*: Preservou a estrutura da base sem necessidade de criar campos adicionais.