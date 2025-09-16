# SSI Issuer Backend

Um MVP backend para um Issuer de credenciais SSI baseado em ACA-Py e Aries Controller.

## Funcionalidades Implementadas

### 🔐 Autenticação
- Registro de usuários
- Login com JWT
- Proteção de endpoints

### 🔗 Gestão de Conexões
- **POST `/api/create-invitation`** - Cria convites de conexão
- **GET `/api/show-users`** - Lista usuários conectados

### 📜 Gestão de Schemas e Certificados
- **POST `/api/create-certificate`** - Cria schema de certificado na ledger
- **GET `/api/show-certificates`** - Lista certificados emitidos

### 🎯 Ofertas de Credenciais
- **POST `/api/send-offer`** - Envia oferta de credencial para usuário conectado
- **GET `/api/show-offers`** - Lista ofertas enviadas

### ✅ Emissão de Credenciais
- **POST `/api/issue-certificate`** - Emite certificado para oferta aceita

### 🔔 Webhooks
- **POST `/api/webhooks/topic/{topic}/`** - Recebe eventos do ACA-Py
- **GET `/api/webhook-status`** - Status do sistema de webhooks

## Estrutura do Banco de Dados

### Tabelas SSI (SQLite)

#### `connections`
- Rastreia conexões com usuários
- Estados: invitation, request, response, active

#### `schemas`
- Armazena schemas de certificados criados
- Metadados de atributos e definições

#### `credential_definitions`
- Definições de credenciais baseadas em schemas
- Suporte para revogação

#### `credential_offers`
- Ofertas de credenciais enviadas
- Estados: offer_sent, request_received, credential_issued

#### `issued_certificates`
- Certificados emitidos com sucesso
- Dados completos da credencial

## Exemplos de Uso

### 1. Criar Schema de Certificado

```bash
POST /api/create-certificate
Authorization: Bearer <token>
Content-Type: application/json

{
    "schema_name": "UniversityDegree",
    "schema_version": "1.0",
    "attributes": ["student_name", "degree", "university", "graduation_date"]
}
```

**Response:**
```json
{
    "schema_id": "WgWxqztrNooG92RXvxSTWv:2:UniversityDegree:1.0",
    "schema": { /* schema completo */ },
    "schema_name": "UniversityDegree",
    "schema_version": "1.0",
    "attributes": ["student_name", "degree", "university", "graduation_date"]
}
```

### 2. Criar Convite de Conexão

```bash
POST /api/create-invitation
Authorization: Bearer <token>
Content-Type: application/json

{
    "alias": "University Portal"
}
```

**Response:**
```json
{
    "connection_id": "12345-abcde-67890",
    "invitation": { /* dados do convite */ },
    "invitation_url": "http://localhost:8041?c_i=eyJ...",
    "alias": "University Portal"
}
```

### 3. Enviar Oferta de Credencial

```bash
POST /api/send-offer
Authorization: Bearer <token>
Content-Type: application/json

{
    "connection_id": "12345-abcde-67890",
    "credential_definition_id": "WgWxqztrNooG92RXvxSTWv:3:CL:1234:default",
    "credential_preview": {
        "attributes": [
            {"name": "student_name", "value": "João Silva"},
            {"name": "degree", "value": "Engenharia da Computação"},
            {"name": "university", "value": "Universidade Federal"},
            {"name": "graduation_date", "value": "2024-12-15"}
        ]
    },
    "comment": "Diploma de graduação"
}
```

### 4. Emitir Certificado

```bash
POST /api/issue-certificate
Authorization: Bearer <token>
Content-Type: application/json

{
    "credential_exchange_id": "abcde-12345-fghij",
    "comment": "Certificado emitido com sucesso"
}
```

### 5. Listar Usuários Conectados

```bash
GET /api/show-users
Authorization: Bearer <token>
```

**Response:**
```json
{
    "total_users": 2,
    "users": [
        {
            "user_id": "uuid-user-1",
            "connection_id": "12345-abcde-67890",
            "their_label": "Mobile Wallet",
            "their_did": "did:sov:BzCbsNYhMrjHiqZDTUASHg",
            "state": "active",
            "created_at": "2024-01-15T10:30:00"
        }
    ]
}
```

## Configuração

### Variáveis de Ambiente

```env
# ACA-Py Configuration
ACAPY_ADMIN_URL=http://localhost:8041
ACAPY_ADMIN_API_KEY=your-api-key

# Database
DATABASE_URL=sqlite:///./issuer.db

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Server
HOST=0.0.0.0
PORT=8001
```

### Executar o Servidor

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python run.py
```

### Executar Testes

```bash
# Testar endpoints
python test_issuer_endpoints.py
```

## Fluxo Completo de Emissão

1. **Issuer**: Cria schema do certificado (`/create-certificate`)
2. **Issuer**: Cria convite de conexão (`/create-invitation`)
3. **Holder**: Aceita convite via wallet/aplicação
4. **Webhook**: ACA-Py notifica estado da conexão
5. **Issuer**: Visualiza usuários conectados (`/show-users`)
6. **Issuer**: Envia oferta de credencial (`/send-offer`)
7. **Holder**: Aceita oferta via wallet
8. **Webhook**: ACA-Py notifica solicitação de credencial
9. **Issuer**: Emite certificado (`/issue-certificate`)
10. **Holder**: Recebe credencial no wallet

## Integrações

### ACA-Py (Aries Cloud Agent Python)
- Comunicação via API REST
- Webhooks para eventos em tempo real
- Gestão de DID, conexões e credenciais

### Hyperledger Indy
- Registro de schemas na ledger
- Provas criptográficas de credenciais
- Verificação de integridade

## Monitoramento

### Logs
- Todas as operações são logadas
- Estados de conexão e credenciais
- Erros e exceções detalhadas

### Health Check
```bash
GET /api/health
```

### Webhook Status
```bash
GET /api/webhook-status
```

## Próximos Passos

- [ ] Interface web para gestão visual
- [ ] Suporte a revogação de credenciais
- [ ] Provas de credenciais (verificação)
- [ ] Templates de schemas
- [ ] Dashboard analítico
- [ ] Notificações em tempo real
- [ ] Backup e restore
- [ ] Logs estruturados
- [ ] Métricas de performance