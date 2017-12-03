Demo.cratica: Página dos dados
==============================

O Demo.cratica existe desde 2011, com o objetivo de tornar os debates
parlamentares mais compreensíveis e transparentes. Queríamos conseguir ler o
que se discute no Parlamento sem ter de chafurdar por entre PDF's e documentos
soltos.

O esforço de processamento dos dados tem sido extenso e complexo, pelo que
documentamos nesta página alguns dos pormenores técnicos sobre a extração e
utilização dos dados das sessões.

## Dados

### Deputados

Fazemos a extração da informação dos deputados a partir do site do Parlamento,
usando um scraper que os afixa no GitHub. São extraídas várias informações
biográficas sobre os deputados, que integramos no Demo.cratica. Ainda não é
feito o processamento dos registos de interesse e páginas de atividade pela
complexidade dessas tarefas, mas providenciamos links para essas páginas no
dataset extraído.

### Transcrições

As transcrições mais recentes que disponibilizamos, caracterizadas por estarem
catalogadas e possuírem meta-informação como o link para o orador, são
extraídas dos ficheiros DOC e DOCX disponíveis na rede interna do
Parlamento. 

Criámos um conjunto complexo de programas que analisam, catalogam e limpam a informação nas transcrições, tratando entre outras coisas de:

* corrigir gralhas comuns
* identificar os oradores e providenciar os links para as suas páginas
* identificar tipos de intervenção (apartes, aplausos, etc) para que possam ser catalogados

O conteúdo das transcrições não é modificado -- o seu conteúdo é que é disponibilizado noutro formato, muito mais fácil de processar e reutilizar do que os originais.


## Datasets

* Transcrições em JSON
* Transcrições em Markdown
* [Lista de deputados](https://github.com/centraldedados/parlamento-deputados)

## Licença de utilização

Os datasets aqui presentes são disponibilizados segundo os termos da Open Database License (ODbL).
