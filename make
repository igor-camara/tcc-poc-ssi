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

    # Verificar se há mudanças (modificados, staging ou não rastreados)
    local has_modified has_staged has_untracked
    has_modified=$(git diff-index --quiet HEAD -- 2>/dev/null; echo $?)
    has_staged=$(git diff --staged --quiet 2>/dev/null; echo $?)
    has_untracked=$(git ls-files --others --exclude-standard | wc -l)
    
    if [[ $has_modified -eq 0 && $has_staged -eq 0 && $has_untracked -eq 0 ]]; then
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
        
        # Combinar ambas as listas de forma mais robusta
        all_files=""
        if [[ -n "$modified_files" ]]; then
            all_files="$modified_files"
        fi
        if [[ -n "$untracked_files" ]]; then
            if [[ -n "$all_files" ]]; then
                all_files="$all_files"$'\n'"$untracked_files"
            else
                all_files="$untracked_files"
            fi
        fi
        
        # Remover linhas vazias e duplicatas
        all_files=$(echo "$all_files" | grep -v '^$' | sort -u)

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

check_dev_dependencies() {
    local missing_deps=()
    local warnings=()

    # Verificar Python
    if ! command -v python3 > /dev/null 2>&1; then
        missing_deps+=("python3")
    fi

    # Verificar Poetry
    if ! command -v poetry > /dev/null 2>&1; then
        missing_deps+=("poetry")
    fi

    # Verificar Node.js - com suporte a NVM
    local node_available=false
    if command -v node > /dev/null 2>&1; then
        node_available=true
    elif [ -f "$HOME/.nvm/nvm.sh" ] || [ -f "/usr/share/nvm/init-nvm.sh" ]; then
        warnings+=("NVM encontrado - Node.js será carregado automaticamente")
        node_available=true
    fi
    
    if [ "$node_available" = false ]; then
        missing_deps+=("node.js")
    fi

    # Verificar pnpm
    if ! command -v pnpm > /dev/null 2>&1; then
        missing_deps+=("pnpm")
    fi

    # Mostrar avisos se houver
    if [ ${#warnings[@]} -gt 0 ]; then
        for warning in "${warnings[@]}"; do
            $GUM style --foreground 33 "⚠ $warning" >&2
        done
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        $GUM style --foreground 196 "✘ Dependências ausentes:" >&2
        for dep in "${missing_deps[@]}"; do
            $GUM style --foreground 196 "  • $dep" >&2
        done
        $GUM style --foreground 33 "" >&2
        $GUM style --foreground 33 "Instalação sugerida:" >&2
        $GUM style --foreground 33 "  sudo apt install python3 python3-pip nodejs npm" >&2
        $GUM style --foreground 33 "  curl -sSL https://install.python-poetry.org | python3 -" >&2
        $GUM style --foreground 33 "  npm install -g pnpm" >&2
        $GUM style --foreground 33 "" >&2
        $GUM style --foreground 33 "Ou instale NVM para gerenciar versões do Node.js:" >&2
        $GUM style --foreground 33 "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash" >&2
        return 1
    fi

    return 0
}

setup_backend() {
    local context="$1"  # holder, issuer, issuer-verifier
    local port="$2"

    if [ ! -d "clients/$context/server" ]; then
        $GUM style --foreground 196 "✘ Diretório clients/$context/server não encontrado!" >&2
        return 1
    fi

    source venv/bin/activate 2>/dev/null || true
    cd "clients/$context/server" || return 1

    # Instalar dependências se necessário
    if [ ! -f "poetry.lock" ] || [ "pyproject.toml" -nt "poetry.lock" ]; then
        if ! $GUM spin --spinner "points" --title "Instalando dependências Python ($context)..." -- \
            poetry install; then
            $GUM style --foreground 196 "✘ Erro ao instalar dependências Python para $context" >&2
            cd - > /dev/null
            return 1
        fi
    fi

    # Configurar porta se especificada
    if [ -n "$port" ] && [ -f "src/api/__init__.py" ]; then
        if [ -f ".env" ]; then
            sed -i "s/^PORT=.*/PORT=$port/" .env 2>/dev/null || true
        else
            echo "PORT=$port" > .env
        fi
    fi

    cd - > /dev/null
    return 0
}

setup_frontend() {
    local context="$1"  # holder, issuer, issuer-verifier

    if [ ! -d "clients/$context/painel" ]; then
        $GUM style --foreground 196 "✘ Diretório clients/$context/painel não encontrado!" >&2
        return 1
    fi

    # Carregar NVM se disponível
    if [ -f "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh"
        nvm use 20 2>/dev/null || nvm use node 2>/dev/null || $GUM style --foreground 33 "⚠ NVM disponível, mas versão 20 não encontrada" >&2
    elif [ -f "/usr/share/nvm/init-nvm.sh" ]; then
        source "/usr/share/nvm/init-nvm.sh"
        nvm use 20 2>/dev/null || nvm use node 2>/dev/null || $GUM style --foreground 33 "⚠ NVM disponível, mas versão 20 não encontrada" >&2
    else
        $GUM style --foreground 33 "⚠ NVM não encontrado, usando Node.js do sistema" >&2
    fi
    
    cd "clients/$context/painel" || return 1

    # Instalar dependências se necessário
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        $GUM style --foreground 33 "📦 Preparando instalação de dependências..." >&2
        
        # Limpar cache do pnpm se necessário
        if [ -d "node_modules" ]; then
            $GUM style --foreground 33 "🧹 Limpando instalação anterior..." >&2
            rm -rf node_modules package-lock.json pnpm-lock.yaml 2>/dev/null || true
        fi
        
        # Instalar com opções não-interativas
        if ! $GUM spin --spinner "points" --title "Instalando dependências Node.js ($context)..." -- \
            bash -c "echo 'y' | pnpm install --prefer-offline --no-frozen-lockfile --ignore-scripts"; then
            
            $GUM style --foreground 33 "⚠ Tentativa 1 falhou, tentando com limpeza de cache..." >&2
            
            # Segunda tentativa com limpeza completa
            pnpm store prune 2>/dev/null || true
            if ! $GUM spin --spinner "points" --title "Reinstalando dependências..." -- \
                bash -c "echo 'y' | pnpm install --force --no-frozen-lockfile"; then
                $GUM style --foreground 196 "✘ Erro ao instalar dependências Node.js para $context" >&2
                cd - > /dev/null
                return 1
            fi
        fi
    fi

    cd - > /dev/null
    return 0
}

start_backend() {
    local context="$1"  # holder, issuer, issuer-verifier
    local port="$2"

    cd "clients/$context/server" || return 1

    $GUM style --foreground 46 "🚀 Iniciando backend $context na porta $port..." >&2
    
    # Executar em background
    poetry run python src/main.py > "/tmp/ssi-${context}-backend.log" 2>&1 &
    local backend_pid=$!
    echo $backend_pid > "/tmp/ssi-${context}-backend.pid"

    # Verificar se iniciou corretamente
    sleep 3
    if kill -0 "$backend_pid" 2>/dev/null; then
        $GUM style --foreground 46 "✔ Backend $context iniciado (PID: $backend_pid)" >&2
        $GUM style --foreground 33 "  📊 API: http://localhost:$port" >&2
        $GUM style --foreground 33 "  📋 Logs: /tmp/ssi-${context}-backend.log" >&2
        cd - > /dev/null
        return 0
    else
        $GUM style --foreground 196 "✘ Falha ao iniciar backend $context" >&2
        cd - > /dev/null
        return 1
    fi
}

start_frontend() {
    local context="$1"  # holder, issuer, issuer-verifier
    local port="$2"

    # Carregar NVM se disponível
    if [ -f "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh"
    elif [ -f "/usr/share/nvm/init-nvm.sh" ]; then
        source "/usr/share/nvm/init-nvm.sh"
    fi

    cd "clients/$context/painel" || return 1

    $GUM style --foreground 46 "🎨 Iniciando frontend $context na porta $port..." >&2
    
    # Executar em background com NVM carregado
    bash -c "
        if [ -f '$HOME/.nvm/nvm.sh' ]; then
            source '$HOME/.nvm/nvm.sh'
            nvm use 20 2>/dev/null || nvm use node 2>/dev/null || true
        elif [ -f '/usr/share/nvm/init-nvm.sh' ]; then
            source '/usr/share/nvm/init-nvm.sh'
            nvm use 20 2>/dev/null || nvm use node 2>/dev/null || true
        fi
        pnpm dev --port '$port' --host 0.0.0.0
    " > "/tmp/ssi-${context}-frontend.log" 2>&1 &
    
    local frontend_pid=$!
    echo $frontend_pid > "/tmp/ssi-${context}-frontend.pid"

    # Verificar se iniciou corretamente
    sleep 5
    if kill -0 "$frontend_pid" 2>/dev/null; then
        $GUM style --foreground 46 "✔ Frontend $context iniciado (PID: $frontend_pid)" >&2
        $GUM style --foreground 33 "  🌐 Web: http://localhost:$port" >&2
        $GUM style --foreground 33 "  📋 Logs: /tmp/ssi-${context}-frontend.log" >&2
        cd - > /dev/null
        return 0
    else
        $GUM style --foreground 196 "✘ Falha ao iniciar frontend $context" >&2
        $GUM style --foreground 33 "  📋 Verifique os logs em: /tmp/ssi-${context}-frontend.log" >&2
        cd - > /dev/null
        return 1
    fi
}

stop_dev_services() {
    local stopped_count=0

    $GUM style --foreground 33 "🛑 Parando serviços de desenvolvimento..." >&2

    # Parar todos os serviços conhecidos
    for context in "holder" "issuer" "issuer-verifier"; do
        for service in "backend" "frontend"; do
            local pid_file="/tmp/ssi-${context}-${service}.pid"
            if [ -f "$pid_file" ]; then
                local pid
                pid=$(cat "$pid_file")
                if kill -0 "$pid" 2>/dev/null; then
                    kill "$pid" 2>/dev/null
                    $GUM style --foreground 46 "✔ $context $service parado (PID: $pid)" >&2
                    stopped_count=$((stopped_count + 1))
                fi
                rm -f "$pid_file"
            fi
        done
    done

    # Limpar arquivos de log antigos
    rm -f /tmp/ssi-*-backend.log /tmp/ssi-*-frontend.log 2>/dev/null || true

    if [ $stopped_count -eq 0 ]; then
        $GUM style --foreground 33 "⚠ Nenhum serviço em execução foi encontrado" >&2
    else
        $GUM style --foreground 46 "✔ $stopped_count serviço(s) parado(s) com sucesso!" >&2
    fi
}

show_dev_status() {
    $GUM style --foreground 46 "📊 Status dos Serviços de Desenvolvimento" >&2
    $GUM style --foreground 46 "" >&2

    local running_services=0

    for context in "holder" "issuer" "issuer-verifier"; do
        local context_has_services=false
        
        for service in "backend" "frontend"; do
            local pid_file="/tmp/ssi-${context}-${service}.pid"
            if [ -f "$pid_file" ]; then
                local pid
                pid=$(cat "$pid_file")
                if kill -0 "$pid" 2>/dev/null; then
                    if [ "$context_has_services" = false ]; then
                        $GUM style --foreground 33 "📁 $context:" >&2
                        context_has_services=true
                    fi
                    local port="unknown"
                    case "$context-$service" in
                        "holder-backend") port="8000" ;;
                        "holder-frontend") port="5173" ;;
                        "issuer-backend") port="8001" ;;
                        "issuer-frontend") port="5174" ;;
                        "issuer-verifier-backend") port="8002" ;;
                        "issuer-verifier-frontend") port="5175" ;;
                    esac
                    $GUM style --foreground 46 "  ✔ $service rodando (PID: $pid, porta: $port)" >&2
                    running_services=$((running_services + 1))
                fi
            fi
        done
    done

    if [ $running_services -eq 0 ]; then
        $GUM style --foreground 33 "⚠ Nenhum serviço em execução" >&2
    fi

    $GUM style --foreground 46 "" >&2
}

dev_menu() {
    local action
    action=$($GUM choose "start" "stop" "status" "help" "voltar" --header "Desenvolvimento Local - O que deseja fazer?")
    case $action in
        "start")   dev_start ;;
        "stop")    stop_dev_services ;;
        "status")  show_dev_status ;;
        "help")    show_help_dev ;;
        "voltar")  return ;;
    esac
}

dev_start() {
    if ! check_dev_dependencies; then
        return 1
    fi

    # Verificar se há serviços já rodando
    local running_services=0
    for context in "holder" "issuer" "issuer-verifier"; do
        for service in "backend" "frontend"; do
            local pid_file="/tmp/ssi-${context}-${service}.pid"
            if [ -f "$pid_file" ]; then
                local pid
                pid=$(cat "$pid_file")
                if kill -0 "$pid" 2>/dev/null; then
                    running_services=$((running_services + 1))
                fi
            fi
        done
    done

    if [ $running_services -gt 0 ]; then
        if $GUM confirm "Há $running_services serviço(s) já em execução. Deseja parar todos e reiniciar?"; then
            stop_dev_services
            sleep 2
        else
            return 0
        fi
    fi

    # Verificar quais contextos estão disponíveis
    local available_contexts=()
    if [ -d "clients/holder" ]; then
        available_contexts+=("holder")
    fi
    if [ -d "clients/issuer" ]; then
        available_contexts+=("issuer")
    fi
    if [ -d "clients/issuer-verifier" ]; then
        available_contexts+=("issuer-verifier")
    fi

    if [ ${#available_contexts[@]} -eq 0 ]; then
        $GUM style --foreground 196 "✘ Nenhum contexto de aplicação encontrado em clients/" >&2
        return 1
    fi

    # Escolher contexto para executar
    local selected_context
    if [ ${#available_contexts[@]} -eq 1 ]; then
        selected_context="${available_contexts[0]}"
        $GUM style --foreground 33 "📁 Usando contexto disponível: $selected_context" >&2
    else
        selected_context=$($GUM choose "${available_contexts[@]}" --header "Escolha o contexto para executar:")
        if [ -z "$selected_context" ]; then
            $GUM style --foreground 196 "✘ Nenhum contexto selecionado." >&2
            return 1
        fi
    fi

    # Escolher o que executar
    local services_to_run
    services_to_run=$($GUM choose --no-limit "backend" "frontend" --header "O que deseja executar para $selected_context?")
    
    if [ -z "$services_to_run" ]; then
        $GUM style --foreground 196 "✘ Nenhum serviço selecionado." >&2
        return 1
    fi

    $GUM style --foreground 33 "⚙️ Configurando ambiente de desenvolvimento..." >&2

    # Definir portas por contexto
    local backend_port frontend_port
    case "$selected_context" in
        "holder")
            backend_port="8000"
            frontend_port="5173"
            ;;
        "issuer")
            backend_port="8001"
            frontend_port="5174"
            ;;
        "issuer-verifier")
            backend_port="8002"
            frontend_port="5175"
            ;;
    esac

    local started_services=()

    # Executar backend se solicitado
    if echo "$services_to_run" | grep -q "backend"; then
        if setup_backend "$selected_context" "$backend_port"; then
            if start_backend "$selected_context" "$backend_port"; then
                started_services+=("backend")
            fi
        fi
    fi

    # Executar frontend se solicitado
    if echo "$services_to_run" | grep -q "frontend"; then
        if setup_frontend "$selected_context"; then
            if start_frontend "$selected_context" "$frontend_port"; then
                started_services+=("frontend")
            fi
        fi
    fi

    if [ ${#started_services[@]} -gt 0 ]; then
        $GUM style --foreground 46 "" >&2
        $GUM style --foreground 46 "✔ Ambiente de desenvolvimento configurado!" >&2
        $GUM style --foreground 46 "" >&2
        $GUM style --foreground 33 "📋 Serviços iniciados para $selected_context:" >&2
        
        for service in "${started_services[@]}"; do
            case "$service" in
                "backend")
                    $GUM style --foreground 33 "  🔧 Backend: http://localhost:$backend_port" >&2
                    $GUM style --foreground 33 "  📖 API Docs: http://localhost:$backend_port/docs" >&2
                    ;;
                "frontend")
                    $GUM style --foreground 33 "  🎨 Frontend: http://localhost:$frontend_port" >&2
                    ;;
            esac
        done
        
        $GUM style --foreground 46 "" >&2
        $GUM style --foreground 33 "💡 Para parar os serviços: ./make -> dev -> stop" >&2
        $GUM style --foreground 33 "📊 Para ver status: ./make -> dev -> status" >&2
    else
        $GUM style --foreground 196 "✘ Nenhum serviço foi iniciado com sucesso" >&2
    fi
}

show_help_dev() {
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 46 "Uso: Desenvolvimento Local" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Comandos disponíveis:" >&2
    $GUM style --foreground 33 "  start        - Iniciar backend e/ou frontend localmente" >&2
    $GUM style --foreground 33 "  stop         - Parar todos os serviços de desenvolvimento" >&2
    $GUM style --foreground 33 "  status       - Mostrar status dos serviços em execução" >&2
    $GUM style --foreground 33 "  help         - Mostrar esta ajuda" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Funcionalidades:" >&2
    $GUM style --foreground 33 "  • Instalação automática de dependências" >&2
    $GUM style --foreground 33 "  • Execução em background com logs" >&2
    $GUM style --foreground 33 "  • Configuração automática de portas" >&2
    $GUM style --foreground 33 "  • Suporte para múltiplos contextos (holder, issuer, issuer-verifier)" >&2
    $GUM style --foreground 46 "" >&2
    $GUM style --foreground 33 "Portas padrão:" >&2
    $GUM style --foreground 33 "  • Holder Backend: 8000, Frontend: 5173" >&2
    $GUM style --foreground 33 "  • Issuer Backend: 8001, Frontend: 5174" >&2
    $GUM style --foreground 33 "  • Issuer-Verifier Backend: 8002, Frontend: 5175" >&2
    $GUM style --foreground 46 "" >&2
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
    $GUM style --foreground 33 "  dev          - Desenvolvimento local (backend e frontend)" >&2
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
        action=$($GUM choose "git" "container" "dev" "alias" "help" "sair" --header "O que deseja fazer?")
        case $action in
            "git")       git_menu ;;
            "container") container ;;
            "dev")       dev_menu ;;
            "alias")     install_alias ;;
            "help")      show_help ;;
            "sair")      break ;;
        esac
    done
}

main
