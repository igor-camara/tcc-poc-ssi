.PHONY: run stop clear help

run:
	@echo "📦 Verificando dependências..."
	@command -v git >/dev/null || (echo "✘ git não encontrado" && exit 1)
	@command -v docker >/dev/null || (echo "✘ docker não encontrado" && exit 1)
	@command -v curl >/dev/null || (echo "✘ curl não encontrado" && exit 1)
	@echo "✔ Clonando repositório von-network..."
	@if [ ! -d "von-network" ]; then \
		git clone https://github.com/bcgov/von-network.git; \
	fi
	@echo "✔ Copiando arquivos customizados..."
	@if [ -d "docker/files-to-replace" ]; then \
		[ -f "docker/files-to-replace/Dockerfile" ] && cp docker/files-to-replace/Dockerfile von-network/Dockerfile; \
		[ -f "docker/files-to-replace/docker-compose.yml" ] && cp docker/files-to-replace/docker-compose.yml von-network/docker-compose.yml; \
		[ -f "docker/files-to-replace/requirements.txt" ] && cp docker/files-to-replace/requirements.txt von-network/server/requirements.txt; \
	fi
	@echo "✔ Construindo von-network..."
	@cd von-network && ./manage build
	@echo "✔ Iniciando von-network..."
	@cd von-network && ./manage start
	@echo "⏳ Aguardando von-network..."
	@for i in $$(seq 1 30); do \
		if curl -s http://localhost:9000/status >/dev/null 2>&1 || curl -s http://localhost:9000/ >/dev/null 2>&1; then \
			echo "✔ von-network disponível!"; \
			break; \
		fi; \
		sleep 2; \
	done
	@if [ -f "docker/docker-compose.yml" ]; then \
		echo "✔ Iniciando containers SSI..."; \
		docker compose -f docker/docker-compose.yml up --build -d; \
		sleep 2; \
	fi
	@echo ""
	@echo "✔ Ambiente SSI pronto!"
	@echo ""
	@echo "URLs dos agentes:"
	@echo "• Holder: http://localhost:8031"
	@echo "• Issuer: http://localhost:8041"
	@echo "• Verifier/Issuer: http://localhost:8051"
	@echo "• von-network: http://localhost:9000"
	@echo ""

stop:
	@echo "⏹ Parando containers SSI..."
	@if [ -f "docker/docker-compose.yml" ]; then \
		docker compose -f docker/docker-compose.yml down; \
	fi
	@echo "⏹ Parando von-network..."
	@if [ -d "von-network" ]; then \
		cd von-network && ./manage stop; \
	fi
	@echo "✔ Serviços parados!"

clear:
	@echo "⚠️  Isso vai remover todos os containers, volumes e redes."
	@printf "Continuar? [y/N] "; \
	read REPLY; \
	if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then \
		if [ -f "docker/docker-compose.yml" ]; then \
			docker compose -f docker/docker-compose.yml down --volumes --remove-orphans; \
		fi; \
		printf "Remover diretório von-network? [y/N] "; \
		read REPLY; \
		if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then \
			if [ -d "von-network" ]; then \
				rm -rf von-network; \
			fi; \
		fi; \
		printf "Remover imagens Docker não utilizadas? [y/N] "; \
		read REPLY; \
		if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then \
			docker system prune -f; \
		fi; \
		echo "✔ Limpeza concluída!"; \
	fi

help:
	@echo ""
	@echo "Gerenciamento de Containers SSI"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make run     - Iniciar ambiente SSI completo"
	@echo "  make stop    - Parar todos os containers"
	@echo "  make clear   - Remover containers e volumes"
	@echo "  make help    - Mostrar esta ajuda"
	@echo ""
	@echo "Componentes:"
	@echo "  • von-network (porta 9000)"
	@echo "  • Holder (porta 8031)"
	@echo "  • Issuer (porta 8041)"
	@echo "  • Verifier/Issuer (porta 8051)"
	@echo ""