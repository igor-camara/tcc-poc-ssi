FROM mongo:7.0

# Variáveis de ambiente para configuração inicial
ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=admin123
ENV MONGO_INITDB_DATABASE=governance

# Expõe a porta padrão do MongoDB
EXPOSE 27017

# Cria diretório para scripts de inicialização
RUN mkdir -p /docker-entrypoint-initdb.d

# Define o volume para persistência de dados
VOLUME ["/data/db"]

# Comando padrão do MongoDB
CMD ["mongod"]
