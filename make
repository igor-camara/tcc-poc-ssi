#!/bin/bash
set -euo pipefail  # Adicionado -u para variáveis não definidas e -o pipefail

# Criado usando gum - https://github.com/charmbracelet/gum

# Para dar permissão de execução
# chmod +x git-helper.sh

GUM=$(command -v gum || true)

install_gum() {
    echo "📦 gum não encontrado, instalando..."

    if ! command -v curl > /dev/null; then
        echo "✘ curl não encontrado. Instale curl primeiro."
        exit 1
    fi

    ARCH=$(uname -m)
    case $ARCH in
        x86_64) ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        *) echo "Arquitetura não suportada: $ARCH"; exit 1 ;;
    esac

    VERSION=$(curl -s https://api.github.com/repos/charmbracelet/gum/releases/latest \
        | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')

    if [[ -z "$VERSION" ]]; then
        echo "✘ Erro ao obter versão do gum"
        exit 1
    fi

    DEB_URL="https://github.com/charmbracelet/gum/releases/download/v${VERSION}/gum_${VERSION}_${ARCH}.deb"
    TMP_DEB="/tmp/gum_${VERSION}_${ARCH}.deb"

    echo "Baixando $DEB_URL..."
    if ! curl -L -o "$TMP_DEB" "$DEB_URL"; then
        echo "✘ Erro ao baixar gum"
        exit 1
    fi

    if ! sudo dpkg -i "$TMP_DEB"; then
        sudo apt-get install -f -y
    fi

    rm -f "$TMP_DEB"
    echo "✔ gum instalado!"
}

run_container() {
    if ! command -v git > /dev/null; then
        $GUM style --foreground 196 "✘ git não encontrado. Instale git primeiro." >&2
        return 1
    fi

    if ! command -v docker > /dev/null; then
        $GUM style --foreground 196 "✘ docker não encontrado. Instale docker primeiro." >&2
        return 1
    fi

    if ! command -v curl > /dev/null; then
        $GUM style --foreground 196 "✘ curl não encontrado. Instale curl primeiro." >&2
        return 1
    fi

    if [ ! -d "von-network" ]; then
        if ! $GUM spin --spinner "points" --title "Clonando repositório von-network..." -- \
            git clone https://github.com/bcgov/von-network.git; then
            $GUM style --foreground 196 "✘ Erro ao clonar repositório von-network" >&2
            return 1
        fi
        $GUM style --foreground 46 "✔ Repositório von-network clonado!" >&2
    else
        $GUM style --foreground 46 "✔ Von network já existe!" >&2
    fi

    if [ ! -d "von-network" ]; then
        $GUM style --foreground 196 "✘ Erro: Diretório von-network não encontrado!" >&2
        return 1
    fi

    if [ -d "docker/files-to-replace" ]; then
        $GUM style --foreground 33 "📁 Copiando arquivos customizados..." >&2

        local files_copied=0
        
        if [ -f "docker/files-to-replace/Dockerfile" ]; then
            if cp docker/files-to-replace/Dockerfile von-network/Dockerfile; then
                $GUM style --foreground 46 "✔ Dockerfile atualizado" >&2
                files_copied=$((files_copied + 1))
            else
                $GUM style --foreground 196 "✘ Erro ao copiar Dockerfile" >&2
            fi
        fi
        
        if [ -f "docker/files-to-replace/docker-compose.yml" ]; then
            if cp docker/files-to-replace/docker-compose.yml von-network/docker-compose.yml; then
                $GUM style --foreground 46 "✔ docker-compose.yml atualizado" >&2
                files_copied=$((files_copied + 1))
            else
                $GUM style --foreground 196 "✘ Erro ao copiar docker-compose.yml" >&2
            fi
        fi
        
        if [ -f "docker/files-to-replace/requirements.txt" ] && [ -d "von-network/server" ]; then
            if cp docker/files-to-replace/requirements.txt von-network/server/requirements.txt; then
                $GUM style --foreground 46 "✔ requirements.txt atualizado" >&2
                files_copied=$((files_copied + 1))
            else
                $GUM style --foreground 196 "✘ Erro ao copiar requirements.txt" >&2
            fi
        fi

        if [ $files_copied -eq 0 ]; then
            $GUM style --foreground 33 "⚠ Nenhum arquivo customizado foi copiado" >&2
        else
            $GUM style --foreground 46 "✔ $files_copied arquivo(s) customizado(s) aplicado(s)!" >&2
        fi
    else
        $GUM style --foreground 33 "⚠ Diretório docker/files-to-replace não encontrado - usando configuração padrão" >&2
    fi

    if ! $GUM spin --spinner "points" --title "Construindo von-network..." -- \
        bash -c "cd von-network && ./manage build"; then
        $GUM style --foreground 196 "✘ Erro ao construir von-network" >&2
        return 1
    fi
    $GUM style --foreground 46 "✔ Build do von-network finalizado!" >&2

    if ! $GUM spin --spinner "points" --title "Iniciando von-network..." -- \
        bash -c "cd von-network && ./manage start"; then
        $GUM style --foreground 196 "✘ Erro ao iniciar von-network" >&2
        return 1
    fi
    $GUM style --foreground 46 "✔ Von-network iniciado!" >&2

    local max_attempts=30
    local attempt=1
    
    $GUM style --foreground 33 "⏳ Verificando se von-network está disponível..." >&2
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:9000/status > /dev/null 2>&1 || curl -s http://localhost:9000/ > /dev/null 2>&1; then
            $GUM style --foreground 46 "✔ von-network detectado e disponível!" >&2
            break
        fi
        $GUM style --foreground 33 "   Tentativa $attempt/$max_attempts - Aguardando von-network..." >&2
        sleep 2
        attempt=$((attempt + 1))
        
        if [ $attempt -gt $max_attempts ]; then
            $GUM style --foreground 196 "✘ von-network não está disponível em localhost:9000" >&2
            $GUM style --foreground 196 "   Timeout após $max_attempts tentativas" >&2
            return 1
        fi
    done

    if [ -f "docker/docker-compose.yml" ]; then
        if ! $GUM spin --spinner "points" --title "Subindo containers SSI..." -- \
            docker compose -f docker/docker-compose.yml up --build -d; then
            $GUM style --foreground 196 "✘ Erro ao iniciar containers SSI" >&2
            return 1
        fi
        
        $GUM style --foreground 33 "⏳ Aguardando containers ficarem prontos..." >&2
        sleep 2
        
        $GUM style --foreground 46 "✔ Containers SSI iniciados!" >&2
    else
        $GUM style --foreground 33 "⚠ Arquivo docker/docker-compose.yml não encontrado - pulando containers SSI" >&2
    fi

    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 46 "✔ Ambiente SSI pronto!" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "URLs dos agentes:" >&2
    $GUM style --foreground 33 "• Holder: http://localhost:8031" >&2
    $GUM style --foreground 33 "• Issuer: http://localhost:8041" >&2
    $GUM style --foreground 33 "• Verifier/Issuer: http://localhost:8051" >&2
    $GUM style --foreground 33 "• von-network: http://localhost:9000" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Para parar: ./make (opção container -> stop)" >&2

    exit 0
}

stop_container() {
    local containers_stopped=0

    if [ -f "docker/docker-compose.yml" ]; then
        if $GUM spin --spinner "points" --title "Parando containers SSI..." -- \
            docker compose -f docker/docker-compose.yml down; then
            $GUM style --foreground 46 "✔ Containers SSI parados!" >&2
            containers_stopped=$((containers_stopped + 1))
        else
            $GUM style --foreground 196 "✘ Erro ao parar containers SSI" >&2
        fi
    fi

    if [ -d "von-network" ]; then
        if $GUM spin --spinner "points" --title "Parando von-network..." -- \
            bash -c "cd von-network && ./manage stop"; then
            $GUM style --foreground 46 "✔ Von-network parado!" >&2
            containers_stopped=$((containers_stopped + 1))
        else
            $GUM style --foreground 196 "✘ Erro ao parar von-network" >&2
        fi
    fi

    if [ $containers_stopped -eq 0 ]; then
        $GUM style --foreground 33 "⚠ Nenhum container foi encontrado para parar" >&2
    else
        $GUM style --foreground 46 "✔ $containers_stopped serviço(s) parado(s) com sucesso!" >&2
    fi
}

clear_containers() {
    if ! $GUM confirm "Isso vai remover todos os containers, volumes e redes. Deseja continuar?"; then
        return 0
    fi

    local items_removed=0

    if [ -f "docker/docker-compose.yml" ]; then
        if $GUM spin --spinner "points" --title "Removendo containers SSI..." -- \
            docker compose -f docker/docker-compose.yml down --volumes --remove-orphans; then
            $GUM style --foreground 46 "✔ Containers SSI removidos!" >&2
            items_removed=$((items_removed + 1))
        else
            $GUM style --foreground 196 "✘ Erro ao remover containers SSI" >&2
        fi
    fi

    if [ -d "von-network" ]; then
        if $GUM confirm "Deseja remover completamente o diretório von-network?"; then
            if $GUM spin --spinner "points" --title "Removendo von-network..." -- \
                rm -rf von-network; then
                $GUM style --foreground 46 "✔ Diretório von-network removido!" >&2
                items_removed=$((items_removed + 1))
            else
                $GUM style --foreground 196 "✘ Erro ao remover von-network" >&2
            fi
        fi
    fi

    if $GUM confirm "Deseja remover imagens Docker não utilizadas?"; then
        if $GUM spin --spinner "points" --title "Limpando imagens Docker..." -- \
            docker system prune -f; then
            $GUM style --foreground 46 "✔ Imagens Docker limpas!" >&2
            items_removed=$((items_removed + 1))
        else
            $GUM style --foreground 196 "✘ Erro na limpeza de imagens Docker" >&2
        fi
    fi

    if [ $items_removed -eq 0 ]; then
        $GUM style --foreground 33 "⚠ Nenhum item foi removido" >&2
    else
        $GUM style --foreground 46 "✔ Limpeza concluída! $items_removed operação(ões) realizadas." >&2
    fi
}

show_help_container() {
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 46 "Uso: Gerenciamento de Containers SSI" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Comandos disponíveis:" >&2
    $GUM style --foreground 33 "  run          - Iniciar ambiente SSI completo (von-network + containers)" >&2
    $GUM style --foreground 33 "  stop         - Parar todos os containers em execução" >&2
    $GUM style --foreground 33 "  clear        - Remover containers, volumes e opcionalmente imagens" >&2
    $GUM style --foreground 33 "  help         - Mostrar esta ajuda" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Componentes do ambiente:" >&2
    $GUM style --foreground 33 "  • von-network: Rede Hyperledger Indy (porta 9000)" >&2
    $GUM style --foreground 33 "  • Holder: Agente portador de credenciais (porta 8031)" >&2
    $GUM style --foreground 33 "  • Issuer: Agente emissor de credenciais (porta 8041)" >&2
    $GUM style --foreground 33 "  • Verifier/Issuer: Agente verificador (porta 8051)" >&2
    $GUM style --foreground 46 "" >&2
}

main() {
    if [ -z "$GUM" ]; then
        install_gum
        GUM=$(command -v gum)
    fi

    while true; do
        local action
        action=$($GUM choose "run" "stop" "clear" "help" "sair" --header "O que deseja fazer?")
        case $action in
            "run")   run_container ;;
            "stop")  stop_container ;;
            "clear") clear_containers ;;
            "help")  show_help_container ;;
            "sair")  break ;;
        esac
    done
}

main
