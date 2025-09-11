#!/bin/bash

# Função para converter para minúsculas
toLower() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

COMMAND=$(toLower ${1})

# Função para criar venv se não existir
create_venv_if_not_exists() {
    if [ ! -d "venv" ]; then
        echo "Criando ambiente virtual..."
        python3 -m venv venv
        echo "Ambiente virtual criado com sucesso!"
    fi
}

# Função para ativar o venv
activate_venv() {
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "Ambiente virtual ativado!"
    else
        echo "Erro: Ambiente virtual não encontrado!"
        exit 1
    fi
}

# Função para clonar o projeto da von-network
clone_von_network() {
    if [ ! -d "von-network" ]; then
        echo "Clonando repositório ..."
        git clone https://github.com/bcgov/von-network.git
        echo "Repositório clonado!"
    else
        echo "Von network já clonado!"
    fi
}

# Função para limpar
clean() {
    if [ -d "venv" ]; then
        rm -rf venv
        echo "Ambiente virtual removido!"
    else
        echo "Nenhum ambiente virtual encontrado para remover."
    fi

    if [ -d "von-network" ]; then
        rm -rf von-network
        echo "Repositório removido!"
    else
        echo "Repositório do von-network não encontrado."
    fi
}

# Iniciar von-network
start_network() {
    cd von-network
    echo "Iniciando von-network ..."
    ./manage build
    echo "Build Finalizado!"
    ./manage start
    cd ..
    echo "Nodes iniciados! Acesse em http://localhost:9000/"
}

# Fechar von-network
stop_network() {
    echo "Fechando von-network ..."
    cd von-network && ./manage down
    ./manage stop
    echo "Network fechada"
}

# Copiar arquivos customizados para von-network
update_files() {
    if [ ! -d "von-network" ]; then
        echo "Erro: Diretório von-network não encontrado!"
        echo "Execute primeiro: make clone-network"
        exit 1
    fi

    if [ ! -d "files" ]; then
        echo "Erro: Diretório 'files' não encontrado!"
        exit 1
    fi

    echo "Copiando arquivos customizados para von-network..."

    # Verificar e copiar Dockerfile
    if [ -f "files/Dockerfile" ]; then
        cp files/Dockerfile von-network/Dockerfile
        echo "✓ Dockerfile copiado para von-network/"
    else
        echo "⚠ Dockerfile não encontrado em files/"
    fi

    # Verificar e copiar docker-compose.yml
    if [ -f "files/Dockerfile" ]; then
        cp files/docker-compose.yml von-network/docker-compose.yml
        echo "✓ docker-compose copiado para von-network/"
    else
        echo "⚠ docker-compose não encontrado em files/"
    fi

    # Verificar e copiar requirements.txt
    if [ -f "files/requirements.txt" ]; then
        cp files/requirements.txt von-network/server/requirements.txt
        echo "✓ requirements.txt copiado para von-network/server/"
    else
        echo "⚠ requirements.txt não encontrado em files/"
    fi

    echo "Arquivos atualizados com sucesso!"
}

start_agents() {
    echo "Iniciando agentes (Alice e Faber)..."
    cd agents && docker compose up --build -d
    echo "Agentes iniciados!"
}

case "${COMMAND}" in
    setup|init)
        create_venv_if_not_exists
        activate_venv
        if [ -f "requirements.txt" ]; then
            echo "Instalando dependências..."
            pip install -r requirements.txt
        fi
        ;;
    activate)
        create_venv_if_not_exists
        activate_venv
        ;;
    install)
        create_venv_if_not_exists
        activate_venv
        if [ -z "$2" ]; then
            echo "Uso: make-py install <pacote>"
            exit 1
        fi
        pip install "$2"
        ;;
    requirements)
        create_venv_if_not_exists
        activate_venv
        pip freeze > requirements.txt
        echo "Requirements.txt atualizado!"
        ;;
    clean)
        clean
        ;;
    clone-network)
        clone_von_network
        ;;
    start-network)
        start_network
        ;;
    close-network)
        stop_network
        ;;
    update-files)
        update_files
        ;;
    run-env)
        create_venv_if_not_exists
        activate_venv
        clone_von_network
        update_files
        start_network
        sleep 5
        start_agents
        ;;
    help|*)
        echo "Uso: make-py <comando>"
        echo ""
        echo "Comandos disponíveis:"
        echo "  setup/init    - Cria venv, ativa e instala requirements.txt"
        echo "  activate      - Cria venv se necessário e ativa"
        echo "  install <pkg> - Instala um pacote no venv"
        echo "  requirements  - Gera/atualiza requirements.txt"
        echo "  clean         - Remove o ambiente virtual"
        echo "  clone-network - Clona o repositório von-network"
        echo "  start-network - Inicia a rede von-network"
        echo "  close-network - Para a rede von-network"
        echo "  update-files  - Copia arquivos de files/ para von-network"
        echo "  help          - Mostra esta ajuda"
        ;;
esac