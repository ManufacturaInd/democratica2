# Demo.cratica

## Pré-requisitos

Há três repositórios que é preciso colocar em diretórios específicos. Um dia
vamos simplificar isto, mas para já é assim.

* `parlamento-deputados`, colocado em `~/datasets`
* `dar-transcricoes-txt`, colocado em `~/datasets-central`
* `parlamento-datas_sessoes`, colocado em `~/datasets-central`

## Instalação

    make install

## Gerar o site

    make html

Para ajudar ao desenvolvimento, também existe um comando `make html-quick` que
só processa as transcrições mais recentes -- assim, a geração do site leva
bastante menos tempo.

## Correr o site localmente

    make serve

O site fica acessível em [http://localhost:8002](http://localhost:8002).

## Colocar o site no staging server (democratica.koizo.org)

    make upload

Antes de fazer o upload, dá jeito correr o `make fakeupload` para rever as mudanças que vão ser feitas e não dar asneira.

## Colocar o site no servidor live (demo.cratica.org)

    make live-upload

Antes de fazer o upload, dá jeito correr o `make live-fakeupload` para rever as mudanças que vão ser feitas e não dar asneira.






