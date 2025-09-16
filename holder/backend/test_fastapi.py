#!/usr/bin/env python3
"""
Test script for FastAPI SSI Holder endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configurações do teste
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class FastAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.test_email = f"test_{int(time.time())}@example.com"
        self.test_password = "password123"
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def make_request(self, method, endpoint, data=None, headers=None, auth_required=False):
        """Make HTTP request with error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add authorization header if required
        if auth_required and self.token:
            if headers is None:
                headers = {}
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.ConnectionError:
            self.log("❌ Conexão falhou! Certifique-se de que o servidor está rodando.", "ERROR")
            return None
        except Exception as e:
            self.log(f"❌ Erro na requisição: {str(e)}", "ERROR")
            return None
    
    def test_health_check(self):
        """Teste 1: Health Check"""
        self.log("🔍 Testando Health Check...")
        
        response = self.make_request("GET", "/health")
        if response is None:
            return False
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ Health Check OK: {data.get('message', 'N/A')}")
            return True
        else:
            self.log(f"❌ Health Check falhou: {response.status_code}")
            return False
    
    def test_register(self):
        """Teste 2: Registro de usuário"""
        self.log("🔍 Testando registro de usuário...")
        
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = self.make_request("POST", "/auth/register", user_data)
        if response is None:
            return False
        
        if response.status_code == 201:
            data = response.json()
            self.token = data.get('token')
            self.user_data = data.get('user')
            
            self.log(f"✅ Registro bem-sucedido para: {self.user_data.get('email')}")
            self.log(f"🔑 Token JWT recebido: {self.token[:20]}...")
            
            # Verificar se DID foi criado
            if self.user_data.get('did'):
                self.log(f"🆔 DID criado: {self.user_data.get('did')}")
            else:
                self.log("⚠️  DID não foi criado (ACA-Py pode estar indisponível)")
            
            return True
        else:
            self.log(f"❌ Registro falhou: {response.status_code}")
            if response.text:
                self.log(f"   Resposta: {response.text}")
            return False
    
    def test_register_duplicate(self):
        """Teste 3: Tentar registrar usuário duplicado"""
        self.log("🔍 Testando registro duplicado...")
        
        user_data = {
            "email": self.test_email,  # Mesmo email do teste anterior
            "password": self.test_password,
            "first_name": "Test",
            "last_name": "Duplicate"
        }
        
        response = self.make_request("POST", "/auth/register", user_data)
        if response is None:
            return False
        
        if response.status_code == 409:
            self.log("✅ Registro duplicado corretamente rejeitado")
            return True
        else:
            self.log(f"❌ Registro duplicado deveria retornar 409, mas retornou: {response.status_code}")
            return False
    
    def test_login_invalid(self):
        """Teste 4: Login com credenciais inválidas"""
        self.log("🔍 Testando login com credenciais inválidas...")
        
        login_data = {
            "email": self.test_email,
            "password": "senha_errada"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response is None:
            return False
        
        if response.status_code == 401:
            self.log("✅ Login inválido corretamente rejeitado")
            return True
        else:
            self.log(f"❌ Login inválido deveria retornar 401, mas retornou: {response.status_code}")
            return False
    
    def test_login_valid(self):
        """Teste 5: Login com credenciais válidas"""
        self.log("🔍 Testando login com credenciais válidas...")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response is None:
            return False
        
        if response.status_code == 200:
            data = response.json()
            new_token = data.get('token')
            user = data.get('user')
            
            self.log(f"✅ Login bem-sucedido para: {user.get('email')}")
            self.log(f"🔑 Novo token JWT recebido: {new_token[:20]}...")
            
            # Atualizar token para próximos testes
            self.token = new_token
            return True
        else:
            self.log(f"❌ Login falhou: {response.status_code}")
            return False
    
    def test_me_without_token(self):
        """Teste 6: Acessar /me sem token"""
        self.log("🔍 Testando acesso a /me sem token...")
        
        response = self.make_request("GET", "/auth/me")
        if response is None:
            return False
        
        if response.status_code == 403:
            self.log("✅ Acesso sem token corretamente rejeitado")
            return True
        else:
            self.log(f"❌ Acesso sem token deveria retornar 401, mas retornou: {response.status_code}")
            return False
    
    def test_me_with_token(self):
        """Teste 7: Acessar /me com token válido"""
        self.log("🔍 Testando acesso a /me com token válido...")
        
        response = self.make_request("GET", "/auth/me", auth_required=True)
        if response is None:
            return False
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ Perfil do usuário obtido: {data.get('email')}")
            
            # Verificar campos SSI
            if data.get('did'):
                self.log(f"🆔 DID no perfil: {data.get('did')}")
                self.log(f"🔐 Verkey: {data.get('verkey', 'N/A')}")
            
            return True
        else:
            self.log(f"❌ Acesso ao perfil falhou: {response.status_code}")
            return False
    
    def test_ssi_status(self):
        """Teste 8: Verificar status SSI"""
        self.log("🔍 Testando status SSI...")
        
        response = self.make_request("GET", "/auth/ssi-status", auth_required=True)
        if response is None:
            return False
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ Status SSI obtido:")
            self.log(f"   - Serviço SSI disponível: {data.get('ssi_service_available')}")
            self.log(f"   - URL ACA-Py: {data.get('acapy_url', 'N/A')}")
            self.log(f"   - Usuário tem DID: {data.get('user_has_did')}")
            
            if data.get('user_did'):
                self.log(f"   - DID do usuário: {data.get('user_did')}")
                self.log(f"   - Verkey: {data.get('user_verkey', 'N/A')}")
            
            return True
        else:
            self.log(f"❌ Status SSI falhou: {response.status_code}")
            return False
    
    def test_validation_errors(self):
        """Teste 9: Testar validações de entrada"""
        self.log("🔍 Testando validações de entrada...")
        
        # Teste email inválido
        invalid_data = {
            "email": "email_invalido",
            "password": "123456"
        }
        
        response = self.make_request("POST", "/auth/register", invalid_data)
        if response is not None and response.status_code == 422:  # FastAPI usa 422 para validation errors
            self.log("✅ Email inválido corretamente rejeitado")
        else:
            self.log("❌ Validação de email não funcionou")
            return False
        
        # Teste senha muito curta
        invalid_data = {
            "email": "test@example.com",
            "password": "123"
        }
        
        response = self.make_request("POST", "/auth/register", invalid_data)
        if response is not None and response.status_code == 422:
            self.log("✅ Senha curta corretamente rejeitada")
        else:
            self.log("❌ Validação de senha não funcionou")
            return False
        
        return True
    
    def run_all_tests(self):
        """Executar todos os testes"""
        self.log("🚀 Iniciando fluxo de testes da API SSI Holder FastAPI")
        self.log(f"📍 Base URL: {BASE_URL}")
        self.log(f"📧 Email de teste: {self.test_email}")
        print("-" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Registro de Usuário", self.test_register),
            ("Registro Duplicado", self.test_register_duplicate),
            ("Login Inválido", self.test_login_invalid),
            ("Login Válido", self.test_login_valid),
            ("Acesso /me sem Token", self.test_me_without_token),
            ("Acesso /me com Token", self.test_me_with_token),
            ("Status SSI", self.test_ssi_status),
            ("Validações de Entrada", self.test_validation_errors),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}")
            print("-" * 40)
            
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} - PASSOU", "SUCCESS")
                else:
                    failed += 1
                    self.log(f"❌ {test_name} - FALHOU", "ERROR")
            except Exception as e:
                failed += 1
                self.log(f"❌ {test_name} - ERRO: {str(e)}", "ERROR")
            
            time.sleep(0.5)  # Pequena pausa entre testes
        
        # Resumo
        print("\n" + "="*60)
        self.log("📊 RESUMO DOS TESTES")
        print("="*60)
        self.log(f"✅ Testes que passaram: {passed}")
        self.log(f"❌ Testes que falharam: {failed}")
        self.log(f"📈 Taxa de sucesso: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            self.log("🎉 TODOS OS TESTES PASSARAM! API FastAPI está funcionando corretamente.", "SUCCESS")
            return True
        else:
            self.log(f"⚠️  {failed} teste(s) falharam. Verifique os logs acima.", "WARNING")
            return False

def main():
    """Função principal"""
    print("🔬 SSI Holder FastAPI Test Suite")
    print("="*60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor não está respondendo corretamente!")
            print("   Certifique-se de que o backend FastAPI está rodando em http://localhost:8000")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor!")
        print("   Certifique-se de que o backend FastAPI está rodando em http://localhost:8000")
        print("   Execute: python run.py")
        sys.exit(1)
    
    # Executar testes
    tester = FastAPITester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()