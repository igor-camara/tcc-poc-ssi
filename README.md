# Ideia do Projeto

A ideia do projeto é mostrar o funcionamento do fluxo de SSI com os seguintes atores:

Um Holder
Um Issuer
Um Issuer que também é verifier

Demonstração:

Issuer emite uma credencial
Holder recebe a credencial
Verifier prova a credencial
Com base na credencial provada ele emite outra credencial

Exemplo real:

Governo emite o RG
Pessoa recebe o RG
Faculdade pede para ver a data de nascimento para saber se ele é maior de idade
Pessoa prova apenas que é maior de idade, mas não envia a data de nascimento

# Estrutura do Projeto

backup -> Caso o clone da von-network não funcione no dia
files -> Arquivos que devem ser alterados na von-network após o clone para ela rodar corretamente

holder, issuer, issuer-verifier -> Agentes que serão usados na demonstração

von-network -> Rede de comunicação (blockchain)

# Como iniciar o projeto (rodar o start.sh já faz tudo isso)

```
./make run-env
```
Vai clonar a von-network, arrumar os arquivos e iniciar ela corretamente

```
docker compose up --build -d
```
Vai iniciar os agentes do aca-py

Os agentes do aca-py são um client de APIs usadas para comunicação com a von-network, a interação com a ledger nunca é direta, sempre passa pelas APIs do aca-py primeiro.

Ao iniciar, nas portas 8031, 8041 e 8051 vai haver um swagger com os endpoints dos agentes

# Frameworks usados

**Agentes**: 
    aca-py
    AriesController (wrapper usado para facilitar o uso do aca-py)

**Ledger**: 
    von-network

**Aplicações**:
    Vue 3
    Python 3.12 -> FastAPI e AriesController são as libs principais

#### Detalhes

Tem que dar uma limpada no makefile
O docker-compose tem que subir os APPs