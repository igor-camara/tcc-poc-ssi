# ==========================
# Etapa 1 - Build da aplicação
# ==========================
FROM node:18-alpine AS build-stage

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN pnpm install

# Copiar código da aplicação
COPY ./frontend .

# Build para produção
RUN pnpm build


# ==========================
# Etapa 2 - Servir com nginx
# ==========================
FROM nginx:alpine AS production-stage

# Copiar build gerado para o nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expor a porta do nginx
EXPOSE 81

# Iniciar o nginx
CMD ["nginx", "-g", "daemon off;"]
