# O que é o Issuer?

O Issuer (emissor) é a entidade responsável por emitir credenciais verificáveis (VCs – Verifiable Credentials) para um indivíduo ou organização (Holder). Essas credenciais representam algum tipo de informação confiável, como:

    - Um diploma (universidade → aluno)
    - Uma CNH (governo → cidadão)
    - Um certificado de curso (instituição → participante)
    - Um crachá digital (empresa → funcionário)


🔹 Criação do Schema

O Issuer define um schema (modelo de dados) que descreve os atributos da credencial.

Exemplo: Diploma → {nome, curso, instituição, data de conclusão}.

Publicação na Blockchain / Ledger

O Issuer publica o schema e a credential definition (cred def) em uma blockchain ou rede de confiança (ex: Hyperledger Indy, Sovrin).

Isso não significa que os dados pessoais vão para a blockchain, mas sim a referência da credencial (metadados e regras de emissão).

Emissão de Credenciais para Holders

Após ter uma conexão segura com o Holder (via DIDComm, por exemplo), o Issuer gera uma Verifiable Credential baseada no schema e cred def.

Essa credencial é então assinada criptograficamente pelo Issuer e entregue ao Holder.

Garantia de Confiabilidade

O Issuer é a raiz de confiança: só porque a credencial foi emitida por ele, terceiros (Verifiers) podem confiar nas informações, desde que reconheçam a autoridade desse Issuer.

🔹 Papel no fluxo SSI

1. O Issuer cria o schema + cred def → publica na ledger.
2. O Holder se conecta ao Issuer (normalmente via convite DIDComm).
3. O Issuer emite a credencial para o Holder.
4. O Verifier, ao receber uma prova do Holder, consulta a ledger para verificar se:
5. O Issuer existe e é confiável.
6. O schema e a cred def são válidos.
7. A assinatura da credencial realmente vem daquele Issuer.

🔹 Pontos importantes

O Issuer não guarda os dados do Holder na blockchain. Ele apenas emite e assina credenciais.

A autoridade do Issuer depende de governança e reputação: se a rede/confederação reconhece aquela entidade como legítima.

O Issuer pode ser qualquer entidade, mas sua credibilidade é o que faz as credenciais terem valor.
---

# Pendências

## Funcionalidades

 - Cadastro/Login

 - Endpoint que retorna os credenciais disponíveis (resumo)
 - Endpoint que retorna os detalhes de uma credencial

 - Criar conexões para Holders
 - Criar credencial e publicar na ledger
 - Criar offer de credencial
 - Mostrar offers de credenciais
 - Emitir a credencial
 - Revogação de credencial

#### Cadastro/login

1. Cadastro e login de usuário
2. Ao cadastrar um usuário, deve ser criado um DID para ele
3. DID deve ser publicado na ledger (blockchain - von-network)
4. Dados do usuário com alguns metadados para facilitar buscas na ledger devem ficar salvos no sqlite

#### Criar conexões para Holders

1. Criar invitations de conexão
2. Disponibilizar a URL para colar na tela de Holder (se sobrar tempo da pra fazer qr code)

#### Mostrar offers de credenciais

1. Mostrar as solicitações de envio de credencial que estão pendentes (/send-offer)
2. Ideia é o Issuer saber para quem ele enviou solicitações de envio


#### Criar credencial e publicar na ledger

1. Criar credencial
2. Criar cred def
3. Postar Cred def na ledger
4. Salvar metadados no sqlite

#### Emitir a credencial

1. Emite credencial para usuários que tenham aceitado a offer

#### Revogação de credencial

---- NÃO AFETAM O FRONTEND ----

#### Endpoint que retorna os certificados disponíveis (resumo)

1. Endpoint para que os Holders ou Verifiers consigam saber as credenciais disponíveis do Issuer
2. Deve retornar apenas as informações principais - nome da credencial, versão (acho que tinha mais um campo)

#### Endpoint que retorna os detalhes de uma credencial

1. Endpoint para que os Holders ou Verifiers consigam os detalhes de uma credencial
2. Deve retornar detalhes como os campos disponíveis da credencial, ID da credencial e cred def

## Detalhes

1. Arrumar espaçamentos no frontend
2. Testar os Dockerfiles (e arrumar se não estiverem funcionando)
3. Colocar os testes do python em uma pasta 'tests'
4. Testar se os testes estão funcionando (não é relevante pra apresentação, mas pelo menos os principais era bom ter pra saber se tá funcionando certinho até finalizar)
5. Fazer um makefile para inicializar o ambiente dev mais fácil
6. Os Dockerfiles são para usar no docker-compose que vai subir todos os container juntos
7. Remover as funcionalidades que não forem relevantes para o Issuer     (Só copiei e colei o projeto do Holder pra reaproveitar código, então pode ter umas coisas desnecessárias)