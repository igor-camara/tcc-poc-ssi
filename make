#!/bin/bash

# Função para converter para minúsculas
toLower() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

COMMAND=$(toLower ${1})

# Função para clonar o projeto da von-network
clone_von_network() {
    if [ ! -d "von-network" ]; then
        echo "Clonando repositório von-network..."
        git clone https://github.com/bcgov/von-network.git
        echo "✓ Repositório clonado!"
    else
        echo "✓ Von network já existe!"
    fi
}

# Copiar arquivos customizados para von-network
update_files() {
    if [ ! -d "von-network" ]; then
        echo "Erro: Diretório von-network não encontrado!"
        exit 1
    fi

    if [ ! -d "files" ]; then
        echo "Aviso: Diretório 'files' não encontrado - usando configuração padrão"
        return 0
    fi

    echo "Copiando arquivos customizados..."

    # Copiar arquivos se existirem
    [ -f "files/Dockerfile" ] && cp files/Dockerfile von-network/Dockerfile && echo "✓ Dockerfile atualizado"
    [ -f "files/docker-compose.yml" ] && cp files/docker-compose.yml von-network/docker-compose.yml && echo "✓ docker-compose atualizado"
    [ -f "files/requirements.txt" ] && cp files/requirements.txt von-network/server/requirements.txt && echo "✓ requirements.txt atualizado"

    echo "✓ Arquivos atualizados!"
}

# Iniciar von-network
start_network() {
    cd von-network
    echo "Iniciando von-network..."
    ./manage build
    echo "✓ Build finalizado!"
    ./manage start
    cd ..
    echo "✓ Von-network iniciada!"
}

# Verificar se von-network está disponível
check_network() {
    echo "⏳ Verificando se von-network está disponível..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:9000/status > /dev/null 2>&1 || curl -s http://localhost:9000/ > /dev/null 2>&1; then
            echo "✅ von-network detectada e disponível!"
            return 0
        fi
        echo "   Tentativa $attempt/$max_attempts - Aguardando von-network..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ von-network não está disponível em localhost:9000"
    echo "   Timeout após $max_attempts tentativas"
    exit 1
}

# Subir containers do projeto SSI
start_ssi_containers() {
    echo "📦 Subindo containers SSI..."
    docker compose up --build -d
    
    echo "⏳ Aguardando containers ficarem prontos..."
    sleep 2
    
    echo "✅ Containers SSI iniciados!"
}

# Parar von-network e limpar volumes
stop_network() {
    echo "Parando containers SSI..."
    docker compose down
    
    echo "Parando von-network e limpando volumes..."
    if [ -d "von-network" ]; then
        cd von-network
        ./manage stop
        ./manage down
        cd ..
        echo "✓ Von-network parada!"
    fi
    
    # Limpar volumes do Docker relacionados ao projeto
    echo "Limpando volumes Docker..."
    docker volume prune -f
    echo "✓ Volumes limpos!"
}

# Executar ambiente completo
run_env() {
    echo "🚀 Iniciando ambiente SSI completo..."
    echo ""
    
    clone_von_network
    update_files
    start_network
    
    # Aguardar 2 segundos após von-network estar pronta
    sleep 2
    
    check_network
    start_ssi_containers
    
    echo ""
    echo "✅ Ambiente SSI pronto!"
    echo ""
    echo "URLs dos agentes:"
    echo "- Holder: http://localhost:8031"
    echo "- Issuer: http://localhost:8041" 
    echo "- Verifier/Issuer: http://localhost:8051"
    echo "- von-network: http://localhost:9000"
    echo ""
    echo "Para parar: ./make stop"
}

case "${COMMAND}" in
    run)
        run_env
        ;;
    stop)
        stop_network
        ;;
    clean)
        stop_network
        if [ -d "von-network" ]; then
            rm -rf von-network
            echo "✓ Repositório von-network removido!"
        fi
        ;;
    help|*)
        echo "Uso: ./make <comando>"
        echo ""
        echo "Comandos principais:"
        echo "  run    - Inicia ambiente SSI completo (von-network + containers)"
        echo "  stop   - Para tudo e limpa volumes Docker"
        echo "  clean  - Para tudo e remove o repositório von-network"
        echo "  help   - Mostra esta ajuda"
        ;;
esac