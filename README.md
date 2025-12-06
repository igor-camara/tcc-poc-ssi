# 🔐 Prova de Conceito - Sistema de Identidade Soberana (SSI)

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![Hyperledger Indy](https://img.shields.io/badge/Hyperledger-Indy-orange)](https://www.hyperledger.org/use/hyperledger-indy)
[![ACA-Py](https://img.shields.io/badge/Aries-Cloud%20Agent-green)](https://github.com/hyperledger/aries-cloudagent-python)

## 📋 Sobre o Projeto

Este projeto demonstra o funcionamento completo de um fluxo **Self-Sovereign Identity (SSI)** utilizando as tecnologias Hyperledger Indy e Aries Cloud Agent Python (ACA-Py). A implementação apresenta um ecossistema com quatro agentes principais que simulam cenários reais de emissão, armazenamento e verificação de credenciais digitais.

### 🎯 Objetivo

Demonstrar na prática como funciona um sistema de identidade soberana, onde os usuários têm controle total sobre suas credenciais digitais, podendo provar informações específicas sem revelar dados desnecessários.

### 🌟 Exemplo Prático

**Cenário**: Validação de maioridade para ingresso universitário

1. **Governo** (Issuer) emite uma credencial de RG digital
2. **Pessoa** (Holder) recebe e armazena a credencial em sua carteira digital
3. **Faculdade** (Verifier/Issuer) solicita prova de maioridade
4. **Pessoa** prova apenas que é maior de idade, **sem revelar a data de nascimento**
5. **Faculdade**, com base na prova validada, emite uma credencial de matrícula

## 🏗️ Arquitetura do Sistema

```mermaid
graph TB
    subgraph "Rede Blockchain"
        VN[von-network<br/>Hyperledger Indy<br/>:9000]
    end
    
    subgraph "Agentes SSI"
        G[Governance Endorser<br/>:8021]
        H[Holder Agent<br/>:8031]
        I[Issuer Agent<br/>:8041]
        IV[Issuer-Verifier Agent<br/>:8051]
    end
    
    subgraph "Aplicações Web"
        GP[Governance Panel<br/>Vue.js]
        HP[Holder Panel<br/>Vue.js]
        IP[Issuer Panel<br/>Vue.js]
        IVP[Verifier Panel<br/>Vue.js]
    end
    
    G <--> VN
    H <--> VN
    I <--> VN
    IV <--> VN
    
    GP <--> G
    HP <--> H
    IP <--> I
    IVP <--> IV
```

## 🚀 Tecnologias Utilizadas

### Backend & SSI
- **Python 3.12** - Linguagem principal
- **FastAPI** - Framework web para APIs REST
- **ACA-Py (Aries Cloud Agent Python)** - Agente para protocolos SSI
- **AriesController** - Wrapper Python para simplificar integração com ACA-Py
- **von-network** - Rede de desenvolvimento Hyperledger Indy

### Frontend
- **Vue.js 3** - Framework JavaScript para interfaces web modernas
- **Docker & Docker Compose** - Containerização e orquestração

### Infraestrutura
- **Docker** - Containerização
- **Hyperledger Indy** - Blockchain para identidade descentralizada
- **SQLite** - Armazenamento local dos agentes

## 📁 Estrutura do Projeto

```
tcc-poc-ssi/
├── 📁 clients/                     # Aplicações cliente
│   ├── 📁 governance/              # Agente de governança (Endorser)
│   │   ├── painel/                 # Interface Web (Vue.js)
│   │   └── server/                 # API Backend (FastAPI)
│   ├── 📁 holder/                  # Aplicação do portador
│   │   ├── painel/                 # Interface Web (Vue.js)
│   │   └── server/                 # API Backend (FastAPI)
│   ├── 📁 issuer/                  # Aplicação do emissor
│   │   ├── painel/                 # Interface Web (Vue.js)
│   │   └── server/                 # API Backend (FastAPI)
│   └── 📁 issuer-verifier/         # Aplicação do verificador/emissor
│       ├── painel/                 # Interface Web (Vue.js)
│       └── server/                 # API Backend (FastAPI)
├── 📁 docker/                      # Configurações Docker
│   ├── docker-compose.yml          # Orquestração dos containers SSI
│   ├── Dockerfile.fastapi          # Imagem para servidores FastAPI
│   ├── Dockerfile.vue3             # Imagem para painéis Vue.js
│   ├── Dockerfile.mongodb          # Imagem para MongoDB
│   └── files-to-replace/           # Arquivos customizados para von-network
│       ├── Dockerfile              # Build personalizado
│       ├── docker-compose.yml      # Configuração von-network
│       └── requirements.txt        # Dependências Python
├── 📁 shared/                      # Dependências compartilhadas
│   └── requirements.txt            # Requisitos Python do projeto
├── 📁 von-network/                 # Rede Hyperledger Indy (clonada)
├── Makefile                        # Comandos de automação
├── shikan.sh                       # Script auxiliar de gerenciamento
└── README.md                       # Este arquivo
```

## 🔧 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- **Docker** (versão 20.10+)
- **Docker Compose** (versão 2.0+)
- **Git** (para clonagem de repositórios)
- **curl** (para verificações de saúde)

### Verificação de Instalação

```bash
# Verificar Docker
docker --version && docker compose version

# Verificar Git e curl
git --version && curl --version
```

## 🚀 Como Executar o Projeto

### 1. Inicialização Completa do Ambiente

```bash
# Iniciar todo o ambiente SSI
make run
```

**O que acontece automaticamente:**

1. 📦 Clona o repositório `von-network` (se não existir)
2. 🔧 Aplica configurações customizadas
3. 🏗️ Constrói a rede blockchain Hyperledger Indy
4. 🌐 Inicia a von-network (porta 9000)
5. ⏳ Aguarda confirmação de que a rede está online
6. 🚀 Inicia os agentes ACA-Py (portas 8031, 8041, 8051)
7. ✅ Configura DIDs públicos para emissores

### 2. Acesso às Interfaces

Após a inicialização bem-sucedida, acesse:

| Serviço | URL | Descrição |
|---------|-----|-----------||
| **von-network** | [http://localhost:9000](http://localhost:9000) | Interface da blockchain Indy |
| **Governance Endorser** | [http://localhost:8021](http://localhost:8021) | API Swagger do Endorser |
| **Holder Agent** | [http://localhost:8031](http://localhost:8031) | API Swagger do Portador |
| **Issuer Agent** | [http://localhost:8041](http://localhost:8041) | API Swagger do Emissor |
| **Verifier Agent** | [http://localhost:8051](http://localhost:8051) | API Swagger do Verificador |

### 3. Gerenciamento do Ambiente

```bash
# Parar todos os containers
make stop

# Limpeza completa (containers, volumes, imagens)
make clear

# Ajuda detalhada
make help
```

## 🔄 Fluxo de Demonstração SSI

### Fase 1: Configuração Inicial
1. **Emissor** registra um schema de credencial na blockchain
2. **Emissor** cria uma definição de credencial baseada no schema
3. **Holder** e **Emissor** estabelecem conexão via convite

### Fase 2: Emissão de Credencial
1. **Emissor** oferece credencial (ex: RG digital) para o **Holder**
2. **Holder** aceita a oferta de credencial
3. **Emissor** emite a credencial com atributos (nome, data nascimento, etc.)
4. **Holder** armazena a credencial em sua carteira digital

### Fase 3: Verificação e Prova
1. **Verifier** solicita prova específica (ex: maior de 18 anos)
2. **Holder** gera prova sem revelar dados sensíveis
3. **Verifier** valida a prova matematicamente
4. **Verifier** emite nova credencial baseada na prova (ex: matrícula)

## 🛠️ Funcionalidades do Makefile

O Makefile é a ferramenta principal para gerenciar o projeto:

### Comandos Disponíveis

#### 🐳 Container Management
- **`make run`** - Inicia ambiente SSI completo
- **`make stop`** - Para todos os containers
- **`make clear`** - Remove containers e volumes
- **`make help`** - Documentação detalhada

### Script Auxiliar shikan.sh

O projeto também inclui o script `shikan.sh` para operações avançadas de Git:

#### 🌿 Git Operations
- **`branch`** - Cria branches com convenção de commits
- **`commit`** - Commits padronizados (feat/fix/chore)
- **`push`** - Push para repositório remoto
- **`deploy`** - Versionamento e release

```bash
# Dar permissão de execução
chmod +x shikan.sh

# Executar
./shikan.sh
```

## 🔍 Detalhes Técnicos

### Agentes ACA-Py

Cada agente roda com configurações específicas:

- **Wallet Type**: Askar (moderno e performático)
- **Auto-responses**: Habilitado para demonstração
- **Genesis URL**: Conectado à von-network local
- **Admin API**: Interface REST para interação

### Rede von-network

- **Nodes**: 4 validadores Indy rodando em cluster
- **Consensus**: Algoritmo PBFT (Practical Byzantine Fault Tolerance)
- **Ports**: 9701-9708 para comunicação entre nodes
- **Web Interface**: Porta 9000 para visualização

### Agente de Governança (Endorser)

- **Função**: Trustee com poder de endossar transações na ledger
- **Seed**: `00000000000000GovernanceEndorser`
- **Porta**: 8021
- **Uso**: Gerenciamento de schemas, definições de credenciais e permissões

### Segurança e Desenvolvimento

⚠️ **Aviso de Segurança**: Este ambiente é configurado para **desenvolvimento apenas**:
- Seeds fixas para reprodutibilidade
- Auto-aceitar convites e credenciais

**Nunca use essas configurações em produção!**

### Convenções de Commit

- `feat(escopo): nova funcionalidade`
- `fix(escopo): correção de bug`
- `chore(escopo): manutenção, config, deps`

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Equipe

Desenvolvido como parte do Trabalho de Conclusão de Curso (TCC) em Ciência da Computação.

---

⭐ **Se este projeto foi útil, considere dar uma estrela no repositório!**