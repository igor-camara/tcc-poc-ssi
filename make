#!/bin/bash
set -euo pipefail  # Adicionado -u para variáveis não definidas e -o pipefail

# Criado usando gum - https://github.com/charmbracelet/gum

# Para dar permissão de execução
# chmod +x git-helper.sh

GUM=$(command -v gum || true)

validate_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        $GUM style --foreground 196 "✘ Erro: Este diretório não é um repositório git." >&2
        exit 1
    fi

    local git_root
    git_root=$(git rev-parse --show-toplevel)
    $GUM style --foreground 46 "✔ Diretório válido: $git_root" >&2
}

check_uncommitted_changes() {
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        if ! $GUM confirm "Há mudanças não commitadas. Deseja continuar?"; then
            exit 0
        fi
    fi
}

choose_type() {
    local context="$1"
    $GUM choose "melhoria" "correção" "configuração" "voltar" --header "Selecione o tipo de $context:"
}

get_prefix() {
    case "$1" in
        melhoria) echo "feat" ;;
        correção) echo "fix" ;;
        configuração) echo "chore" ;;
        *) echo "" ;;
    esac
}

install_alias() {
    CMD_NAME="stw"
    local target="$HOME/.local/bin/$CMD_NAME"
    mkdir -p "$HOME/.local/bin"

    ln -sf "$(realpath "$0")" "$target"

    $GUM style --foreground 46 "✔ Alias instalado: agora você pode rodar '$CMD_NAME' de qualquer lugar." >&2

    exit 0
}

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

create_branch() {
    validate_git_repo
    check_uncommitted_changes

    local base_branch
    base_branch=$(git rev-parse --abbrev-ref HEAD)

    local prefix_choice branch_type code branch_name
    prefix_choice=$(choose_type "branch")

    branch_type=$(get_prefix "$prefix_choice")
    [[ "$branch_type" == "" ]] && return

    code=$($GUM input --placeholder "Digite o nome da branch (use branch com escopo pequeno):")

    if [[ -z "$code" ]]; then
        $GUM style --foreground 196 "✘ Nome da branch não pode estar vazio." >&2
        return
    fi

    code=$(echo "$code" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    branch_name="${branch_type}/${code}"

    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        $GUM style --foreground 196 "✘ Branch $branch_name já existe." >&2
        return
    fi

    git checkout -b "$branch_name"
    $GUM style --foreground 46 "✔ Branch $branch_name criada a partir da branch $base_branch" >&2
}

select_files_paginated() {
    local files="$1"
    local all_files=()
    local remaining_files=()
    local selected_files=()
    local current_page=0
    local page_size=6
    
    while IFS= read -r file; do
        [[ -n "$file" ]] && all_files+=("$file")
    done <<< "$files"
    
    remaining_files=("${all_files[@]}")
    local total_files=${#all_files[@]}
    
    while [[ ${#remaining_files[@]} -gt 0 ]]; do
        local total_remaining=${#remaining_files[@]}
        local display_files=()
        
        # Calcular páginas
        local total_pages=$(( (total_remaining + page_size - 1) / page_size ))
        local start_idx=$((current_page * page_size))
        local end_idx=$(( start_idx + page_size - 1 ))
        [[ $end_idx -ge $total_remaining ]] && end_idx=$((total_remaining - 1))
        
        # Pegar arquivos da página atual
        for ((i=start_idx; i<=end_idx && i<total_remaining; i++)); do
            local file="${remaining_files[$i]}"
            # Adicionar indicador se é modificado ou novo
            if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
                display_files+=("* $file (modificado)")
            else
                display_files+=("+ $file (novo)")
            fi
        done
        
        # Adicionar opções de navegação
        local options=("${display_files[@]}")
        [[ $current_page -gt 0 ]] && options+=("< Página Anterior")
        [[ $current_page -lt $((total_pages - 1)) ]] && options+=("Próxima Página >")
        [[ ${#selected_files[@]} -gt 0 ]] && options+=("= Ver Selecionados (${#selected_files[@]})")
        options+=("- Finalizar Seleção")
        options+=("x Cancelar")
        
        local header="Página $((current_page + 1))/$total_pages - Selecione arquivos"
        [[ ${#selected_files[@]} -gt 0 ]] && header="$header | ${#selected_files[@]} selecionados"
        
        local choices
        choices=$(printf '%s\n' "${options[@]}" | $GUM choose --no-limit --header "$header")
        
        [[ -z "$choices" ]] && continue
        
        local should_continue=true
        
        while IFS= read -r choice; do
            case "$choice" in
                "< Página Anterior")
                    ((current_page--))
                    break
                    ;;
                "Próxima Página >")
                    ((current_page++))
                    break
                    ;;
                "= Ver Selecionados"*)
                    $GUM style --foreground 46 "Arquivos já selecionados:" >&2
                    for selected in "${selected_files[@]}"; do
                        $GUM style --foreground 46 "  - $selected" >&2
                    done
                    $GUM style --foreground 33 "Pressione ENTER para continuar..." >&2
                    read -r
                    break
                    ;;
                "- Finalizar Seleção")
                    should_continue=false
                    break
                    ;;
                "x Cancelar")
                    selected_files=()
                    should_continue=false
                    break
                    ;;
                *)
                    # Remover indicadores para obter o nome real do arquivo
                    local real_file
                    real_file=$(echo "$choice" | sed 's/^[*+] //' | sed 's/ (modificado)$//' | sed 's/ (novo)$//')
                    
                    # Arquivo selecionado - adicionar à lista e remover dos restantes
                    selected_files+=("$real_file")
                    $GUM style --foreground 46 "+ $real_file adicionado" >&2
                    
                    # Remover o arquivo da lista de restantes
                    local temp_remaining=()
                    for file in "${remaining_files[@]}"; do
                        [[ "$file" != "$real_file" ]] && temp_remaining+=("$file")
                    done
                    remaining_files=("${temp_remaining[@]}")
                    
                    # Recalcular página se necessário
                    local new_total=${#remaining_files[@]}
                    local new_max_pages=$(( (new_total + page_size - 1) / page_size ))
                    [[ $current_page -ge $new_max_pages && $new_max_pages -gt 0 ]] && current_page=$((new_max_pages - 1))
                    [[ $new_total -eq 0 ]] && current_page=0
                    
                    # Adicionar o arquivo imediatamente ao git
                    git add "$real_file"
                    ;;
            esac
        done <<< "$choices"
        
        [[ "$should_continue" == false ]] && break
    done
    
    # Retornar arquivos selecionados (apenas para compatibilidade)
    for file in "${selected_files[@]}"; do
        echo "$file"
    done
}

commit_changes() {
    validate_git_repo

    local branch_name opt prefix code msg selected
    branch_name=$(git rev-parse --abbrev-ref HEAD)

    if git diff-index --quiet HEAD -- 2>/dev/null && git diff --staged --quiet 2>/dev/null; then
        $GUM style --foreground 196 "✘ Nenhuma mudança para commit." >&2
        return
    fi

    local staged_files
    staged_files=$(git diff --staged --name-only)
    
    if [[ -n "$staged_files" ]]; then
        $GUM style --foreground 33 "⚠ Há arquivos já no staging area:" >&2
        echo "$staged_files" | while read -r file; do
            $GUM style --foreground 33 "  • $file" >&2
        done
        
        if $GUM confirm "Deseja remover estes arquivos do staging e selecionar manualmente?"; then
            git reset HEAD .
            $GUM style --foreground 46 "✔ Staging area limpo!" >&2
        fi
    fi

    opt=$(choose_type "alteração")
    prefix=$(get_prefix "$opt")
    [[ "$prefix" == "" ]] && return

    scope=$($GUM input --placeholder "Digite o escopo do commit")

    if [[ -z "$scope" ]]; then
        $GUM style --foreground 196 "✘ Escopo do commit não pode estar vazio." >&2
        return
    fi

    if $GUM confirm "Deseja adicionar todos os arquivos (modificados e novos)?"; then
        git add .
    else
        local files modified_files untracked_files all_files
        
        modified_files=$(git diff --name-only)
        
        untracked_files=$(git ls-files --others --exclude-standard)
        
        all_files=$(printf "%s\n%s" "$modified_files" "$untracked_files" | grep -v '^$' | sort -u)

        if [[ -z "$all_files" ]]; then
            $GUM style --foreground 196 "✘ Nenhum arquivo encontrado para adicionar." >&2
            return
        fi

        git reset HEAD . 2>/dev/null || true

        selected=$(select_files_paginated "$all_files")
        
        local staged_count
        staged_count=$(git diff --staged --name-only | wc -l)
        
        if [[ $staged_count -eq 0 ]]; then
            $GUM style --foreground 196 "✘ Nenhum arquivo foi selecionado." >&2
            return
        fi
    fi

    local files_to_commit
    files_to_commit=$(git diff --staged --name-only)
    
    if [[ -n "$files_to_commit" ]]; then
        $GUM style --foreground 46 "✔ Arquivos que serão commitados:" >&2
        echo "$files_to_commit" | while read -r file; do
            $GUM style --foreground 46 "  • $file" >&2
        done
    else
        $GUM style --foreground 196 "✘ Nenhum arquivo no staging area para commit." >&2
        return
    fi

    msg=$($GUM input --placeholder "Digite a mensagem do commit")

    if [[ -z "$msg" ]]; then
        $GUM style --foreground 196 "✘ Mensagem do commit não pode estar vazia." >&2
        return
    fi

    git commit -m "${prefix}(${scope}): ${msg}"
    $GUM style --foreground 46 "✔ Commit realizado: ${prefix}(${scope}): ${msg}" >&2

    if $GUM confirm "Deseja fazer push das alterações?"; then
        push_changes
    fi
}

push_changes() {
    validate_git_repo

    local branch_name
    branch_name=$(git rev-parse --abbrev-ref HEAD)
    
    if [[ -z "$branch_name" ]]; then
        $GUM style --foreground 196 "✘ Erro: Não foi possível obter o nome da branch atual" >&2
        return
    fi

    if ! $GUM spin --spinner "points" --title "Fazendo push das alterações..." -- git push -u origin "$branch_name"; then
        $GUM style --foreground 196 "✘ Erro ao fazer push" >&2
        return
    fi

    $GUM style --foreground 46 "✔ Push realizado para $branch_name" >&2

    exit 0
}

deploy() {
    validate_git_repo

    target=$($GUM input --placeholder "Digite a branch de destino da nova versão (ex: dev ou melhorias)")
    [[ -z "$target" ]] && { $GUM style --foreground 196 "✘ Branch de destino é obrigatória." >&2; return; }

    if ! $GUM spin --spinner "points" --title "Indo para branch da release..." -- bash -c "
        git checkout '$target' &&
        git pull origin '$target' &&
        git fetch --prune
    "; then
        $GUM style --foreground 196 "✘ Erro ao preparar branch para release" >&2
        exit 0
    fi

    current=$(jq -r '.version' package.json)
    new_version=$(bump_version "$current")

    jq --arg v "$new_version" '.version = $v' package.json > package.tmp && mv package.tmp package.json

    $GUM style --foreground 46 "✔ Versão atualizada no package.json: $current → $new_version" >&2

    #git add $(ls pom.xml package.json 2>/dev/null) || true
    git add $(ls pom.xml package.json)
    if git commit -m "release: v$new_version - date: $(date +%Y-%m-%d)"; then
        $GUM spin --spinner "points" --title "Enviando release para o repositório remoto..." -- git push origin "$target"
        $GUM style --foreground 46 "✔ Release v$new_version criada e enviada para $target" >&2
        exit 0
    else
        $GUM style --foreground 196 "✘ Erro ao criar commit de release" >&2
        exit 0
    fi
}

bump_version() {
    current=$1

    part=$($GUM choose "major" "minor" "patch" --header "Qual parte da versão deseja incrementar?")
    IFS='.' read -r major minor patch <<< "$current"

    case $part in
        major) ((major++)); minor=0; patch=0 ;;
        minor) ((minor++)); patch=0 ;;
        patch) ((patch++)) ;;
    esac

    echo "${major}.${minor}.${patch}"
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

show_help_git() {
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 46 "Uso: Operações Git" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Comandos disponíveis:" >&2
    $GUM style --foreground 33 "  branch       - Criar nova branch usando convenção de commits" >&2
    $GUM style --foreground 33 "  commit       - Fazer commit com mensagem padronizada" >&2
    $GUM style --foreground 33 "  push         - Enviar branch atual para o remoto" >&2
    $GUM style --foreground 33 "  deploy       - Atualizar versão do projeto" >&2
    $GUM style --foreground 33 "  help         - Mostrar esta ajuda" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Convenções de commit:" >&2
    $GUM style --foreground 33 "  • feat: Nova funcionalidade ou melhoria" >&2
    $GUM style --foreground 33 "  • fix: Correção de bug" >&2
    $GUM style --foreground 33 "  • chore: Configuração, build, dependências" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Pressione ESC a qualquer momento para sair" >&2
    $GUM style --foreground 46 "" >&2
}

git_menu() {
    local action
    action=$($GUM choose "branch" "commit" "push" "deploy" "help" "voltar" --header "O que deseja fazer?")
    case $action in
        "branch")   create_branch ;;
        "commit")   commit_changes ;;
        "push")     push_changes ;;
        "deploy")   deploy ;;
        "help")     show_help_git ;;
        "voltar")     return ;;
    esac
}

container() {
    local action
    action=$($GUM choose "run" "stop" "clear" "help" "voltar" --header "O que deseja fazer?")
    case $action in
        "run")      run_container ;;
        "stop")     stop_container ;;
        "clear")    clear_containers ;;
        "help")     show_help_container ;;
        "voltar")     return ;;
    esac
}

show_help() {
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 46 "Uso: $0" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Módulos disponíveis:" >&2
    $GUM style --foreground 33 "  git          - Operações git (branch, commit, push, deploy)" >&2
    $GUM style --foreground 33 "  container    - Gerenciamento de containers SSI" >&2
    $GUM style --foreground 33 "  alias        - Instalar alias 'stw' (steward) para rodar este script de qualquer lugar" >&2
    $GUM style --foreground 33 "  help         - Mostrar esta ajuda" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Pressione ESC a qualquer momento para sair" >&2
    $GUM style --foreground 46 "" >&2
}

main() {
    if [ -z "$GUM" ]; then
        install_gum
        GUM=$(command -v gum)
    fi

    while true; do
        local action
        action=$($GUM choose "git" "container" "alias" "help" "sair" --header "O que deseja fazer?")
        case $action in
            "git")       git_menu ;;
            "container") container ;;
            "alias")     install_alias ;;
            "help")      show_help ;;
            "sair")      break ;;
        esac
    done
}

main
