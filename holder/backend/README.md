# SSI Holder Backend API

Flask backend API simplificado para SSI Holder com integração ACA-Py.

## Setup Rápido

1. **Instalar dependências:**
   ```bash
   pip install -r ../config/requirements.txt
   ```

2. **Configurar ambiente:**
   ```bash
   cp .env.example .env
   # Edite o .env conforme necessário
   ```

3. **Executar aplicação:**
   ```bash
   python run.py
   ```

   A API estará disponível em `http://localhost:8000`

## Script de Setup Automático

```bash
chmod +x setup.sh
./setup.sh
```

## Endpoints da API

### Autenticação

- `POST /api/auth/login` - Login do usuário
- `POST /api/auth/register` - Registro do usuário (cria DID automaticamente)
- `GET /api/auth/me` - Perfil do usuário atual
- `GET /api/auth/ssi-status` - Status do serviço SSI e informações do DID

### Health Check

- `GET /api/health` - Verificação de saúde da API

## Integração SSI

A aplicação integra com ACA-Py para funcionalidades SSI:

- **Criação automática de DID**: Quando um usuário se registra, um DID é criado automaticamente
- **Integração com von-network**: DIDs podem ser registrados na ledger
- **Serviço SSI**: Encapsula todas as operações ACA-Py

### Pré-requisitos

- ACA-Py rodando na porta 8031
- von-network rodando (para operações de ledger)

## Variáveis de Ambiente

- `FLASK_ENV` - Ambiente (development/production)
- `SECRET_KEY` - Chave secreta do Flask
- `JWT_SECRET_KEY` - Chave secreta do JWT
- `DATABASE_URL` - String de conexão do banco (SQLite por padrão)
- `PORT` - Porta do servidor (padrão: 8000)
- `ACAPY_ADMIN_URL` - URL admin do ACA-Py (padrão: http://localhost:8031)
- `ACAPY_ADMIN_API_KEY` - Chave da API admin do ACA-Py (opcional)

## Banco de Dados

A aplicação usa SQLite por padrão para simplicidade do MVP:

- **Arquivo**: `holder.db` (criado automaticamente)
- **Tabela**: `users` com campos SSI integrados

### Modelo User

O modelo User inclui campos específicos para SSI:
- `did` - Identificador Descentralizado do usuário
- `verkey` - Chave de verificação
- `did_metadata` - Metadados adicionais do DID (JSON)

## Desenvolvimento

Para executar em modo desenvolvimento:
```bash
export FLASK_ENV=development
python run.py
```

O servidor recarregará automaticamente com mudanças no código.

## Fluxo SSI

1. **Registro do Usuário**: Usuário fornece email/senha → Sistema cria conta + DID
2. **Criação do DID**: ACA-Py cria novo DID e chave de verificação
3. **Registro na Ledger**: DID é opcionalmente registrado na von-network
4. **Perfil do Usuário**: Usuário pode visualizar informações do DID via `/api/auth/ssi-status`

## Características do MVP

- **Simplificado**: Apenas bibliotecas essenciais
- **Robusto**: Funciona mesmo se ACA-Py estiver indisponível
- **Leve**: SQLite para persistência simples
- **Testável**: Endpoints para verificar conectividade SSI