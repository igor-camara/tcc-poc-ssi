# O que é o Holder?

O Holder (portador) é a entidade (pessoa, organização ou dispositivo) que recebe, armazena e gerencia credenciais verificáveis (VCs) emitidas por Issuers. Ele é o "dono" da identidade, controlando quais credenciais compartilhar e com quem.

🔹 Funções principais do Holder

Receber credenciais

Aceita as VCs emitidas por um Issuer.

Armazena-as em uma carteira digital (digital wallet).

Gerenciar credenciais

Decide quando, como e com quem compartilhar suas credenciais.

Mantém chaves privadas para assinar e proteger provas.

Criar provas verificáveis (VP – Verifiable Presentation)

O Holder não entrega a credencial inteira; ele gera uma apresentação assinada, contendo apenas os dados solicitados pelo Verifier.

Exemplo: Mostrar apenas que é maior de 18 anos, sem revelar a data de nascimento.

🔹 Papel no fluxo SSI

1. O Holder se conecta a um Issuer → recebe uma credencial.
2. O Holder armazena a credencial na carteira.
3. Quando um Verifier solicita uma prova, o Holder cria e entrega uma apresentação verificável.

🔹 Pontos importantes

O Holder controla totalmente seus dados (self-sovereignty).

Pode escolher compartilhar apenas os atributos necessários (minimização de dados).

Não precisa depender do Issuer novamente para comprovar sua informação.
---

# Pendências

## Funcionalidades

 - Cadastro/Login
 
 - Adicionar Issuer/Aceitar invitation
 - Consultar credenciais disponíveis
 - Solicitar que o Issuer mande uma offer de uma credencial em específico
 - Aceitar ou recusar offer
 - Exibição dos documentos do usuário por Issuer
 - Aceitar ou recusar pedido de prova

 - Endpoint para receber notificações de offers
 - Endpoint para receber notificações de provas

#### Cadastro/Login 

1. Cadastro e login de usuário
2. Ao cadastrar um usuário, deve ser criado um DID para ele
3. DID deve ser publicado na ledger (blockchain - von-network)
4. Dados do usuário com alguns metadados para facilitar buscas na ledger devem ficar salvos no sqlite

#### Adicionar Issuer/Aceitar invitation

1. Consultar todos os Issuers na ledger e o usuário manda um pedido para criar conexão com ele (não obrigatório, fluxo normal é o Issuer iniciar o contato)
2. Campo para inserir a URL gerada pelo Issuer para fazer a conexão

#### Consultar credenciais disponíveis

1. Consultar as credenciais disponíveis do Issuer
2. Poder ver os detalhes de cada credencial

#### Solicitar que o Issuer mande uma offer de uma credencial em específico

1. Solicitar que o Issuer abra um offer (/send-offer) (não obrigatório, fluxo normal é o Issuer iniciar o contato)

#### Aceitar ou recusar offer

1. Retornar um resposta à offer do Issuer

#### Exibição dos documentos do usuário por Issuer
#### Aceitar ou recusar pedido de prova - podendo escolher quais dados retornar

---- NÃO AFETAM O FRONT ----

#### Endpoint para receber notificações de offers
#### Endpoint para receber notificações de provas


## Detalhes

1. Arrumar espaçamentos no frontend
2. Testar os Dockerfiles (e arrumar se não estiverem funcionando)
3. Colocar os testes do python em uma pasta 'tests'
4. Testar se os testes estão funcionando (não é relevante pra apresentação, mas pelo menos os principais era bom ter pra saber se tá funcionando certinho até finalizar)
5. Fazer um makefile para inicializar o ambiente dev mais fácil
6. Os Dockerfiles são para usar no docker-compose que vai subir todos os container juntos