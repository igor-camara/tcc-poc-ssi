#!/bin/bash

echo "🚀 Iniciando ambiente SSI..."

./make run-env

# Verificar se von-network está rodando
if ! curl -s http://localhost:9000/status > /dev/null; then
    echo "❌ von-network não está disponível em localhost:9000"
    echo "   Certifique-se de que a von-network esteja rodando"
    exit 1
fi

echo "✅ von-network detectada"

# Subir containers
echo "📦 Subindo containers..."
docker compose up --build -d

# Aguardar containers estarem prontos
echo "⏳ Aguardando containers ficarem prontos..."
sleep 5

# Executar setup
#echo "🔧 Configurando agentes..."
#python agent.py

echo "✅ Ambiente SSI pronto!"
echo ""
echo "URLs dos agentes:"
echo "- Holder: http://localhost:8031"
echo "- Issuer: http://localhost:8041"
echo "- Verifier/Issuer: http://localhost:8051"
echo "- von-network: http://localhost:9000"