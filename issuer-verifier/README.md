# O que é o Verifier?

O Verifier (verificador) é a entidade que recebe provas do Holder e as valida, garantindo que a informação é autêntica e confiável, sem precisar consultar diretamente o Issuer.

🔹 Funções principais do Verifier

Solicitar informações

Envia ao Holder um proof request especificando quais atributos ou credenciais precisa validar.

Receber prova verificável (VP)

Recebe do Holder uma apresentação assinada (com os dados requeridos).

Verificar validade da credencial

Consulta a blockchain/ledger para checar:

Se o Issuer é legítimo e confiável.

Se o schema e a cred def existem e estão válidos.

Se a assinatura da credencial corresponde ao Issuer.

Se a credencial não foi revogada.

🔹 Papel no fluxo SSI

1. O Verifier solicita uma prova ao Holder.
2. O Holder gera e envia a apresentação.
3. O Verifier valida a prova consultando a ledger.

🔹 Pontos importantes

O Verifier não precisa falar com o Issuer diretamente → confiança vem da rede.

Garante autenticidade, integridade e validade das informações recebidas.

Pode rejeitar provas inválidas ou incompletas.
---

# Pendências

 - Cadastro/Login

 - Enviar pedido de prova
 - Validar prova com base na ledger

## Funcionalidades

#### Cadastro/Login
#### Enviar pedido de prova
#### Validar prova com base na ledger

## Detalhes