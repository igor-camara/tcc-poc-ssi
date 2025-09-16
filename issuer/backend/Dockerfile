# Usar imagem oficial do Python
FROM python:3.12-slim

# Configurar variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Expor a porta do FastAPI
EXPOSE 8001

# Comando para rodar o servidor (usando Uvicorn)
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
