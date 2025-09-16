#!/usr/bin/env python3
"""
Test script for SSI Issuer endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configurações do teste
BASE_URL = "http://localhost:8001"  # Issuer runs on port 8001
API_BASE = f"{BASE_URL}/api"

class IssuerTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.test_email = f"issuer_{int(time.time())}@example.com"
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
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            return None
    
    def test_health_check(self):
        """Test health check endpoint"""
        self.log("Testing health check...")
        
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            self.log(f"✓ Health check passed: {data['message']}")
            return True
        else:
            self.log("✗ Health check failed", "ERROR")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        self.log(f"Testing user registration with email: {self.test_email}")
        
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": "Test",
            "last_name": "Issuer"
        }
        
        response = self.make_request("POST", "/register", user_data)
        if response and response.status_code == 201:
            self.user_data = response.json()
            self.log(f"✓ User registered successfully: {self.user_data['user']['email']}")
            return True
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ User registration failed: {error_msg}", "ERROR")
            return False
    
    def test_user_login(self):
        """Test user login"""
        self.log("Testing user login...")
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self.make_request("POST", "/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            self.token = data["token"]
            self.log(f"✓ User login successful")
            return True
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ User login failed: {error_msg}", "ERROR")
            return False
    
    def test_create_invitation(self):
        """Test creating connection invitation"""
        self.log("Testing connection invitation creation...")
        
        invitation_data = {
            "alias": "Test Connection"
        }
        
        response = self.make_request("POST", "/create-invitation", invitation_data, auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            self.log(f"✓ Invitation created: {data['connection_id']}")
            self.log(f"  Invitation URL: {data['invitation_url']}")
            return data
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ Invitation creation failed: {error_msg}", "ERROR")
            return None
    
    def test_create_certificate_schema(self):
        """Test creating certificate schema"""
        self.log("Testing certificate schema creation...")
        
        schema_data = {
            "schema_name": "TestCertificate",
            "schema_version": "1.0",
            "attributes": ["name", "date_of_birth", "certification_date", "certification_type"]
        }
        
        response = self.make_request("POST", "/create-certificate", schema_data, auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            self.log(f"✓ Certificate schema created: {data['schema_id']}")
            self.log(f"  Schema name: {data['schema_name']}")
            self.log(f"  Attributes: {data['attributes']}")
            return data
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ Certificate schema creation failed: {error_msg}", "ERROR")
            return None
    
    def test_show_users(self):
        """Test showing connected users"""
        self.log("Testing show users...")
        
        response = self.make_request("GET", "/show-users", auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            self.log(f"✓ Users retrieved: {data['total_users']} users")
            for user in data['users']:
                self.log(f"  User: {user['their_label']} - {user['state']}")
            return data
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ Show users failed: {error_msg}", "ERROR")
            return None
    
    def test_show_offers(self):
        """Test showing credential offers"""
        self.log("Testing show offers...")
        
        response = self.make_request("GET", "/show-offers", auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            self.log(f"✓ Offers retrieved: {data['total_offers']} offers")
            self.log(f"  Pending: {data['pending_offers']}, Completed: {data['completed_offers']}")
            for offer in data['offers']:
                self.log(f"  Offer: {offer['schema_name']} - {offer['state']}")
            return data
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ Show offers failed: {error_msg}", "ERROR")
            return None
    
    def test_show_certificates(self):
        """Test showing issued certificates"""
        self.log("Testing show certificates...")
        
        response = self.make_request("GET", "/show-certificates", auth_required=True)
        if response and response.status_code == 200:
            data = response.json()
            self.log(f"✓ Certificates retrieved: {data['total_certificates']} certificates")
            for cert in data['certificates']:
                self.log(f"  Certificate: {cert['schema_name']} - {cert['state']}")
            return data
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ Show certificates failed: {error_msg}", "ERROR")
            return None
    
    def test_webhook_status(self):
        """Test webhook status endpoint"""
        self.log("Testing webhook status...")
        
        response = self.make_request("GET", "/webhook-status")
        if response and response.status_code == 200:
            data = response.json()
            self.log(f"✓ Webhook status: {data['status']}")
            self.log(f"  Supported topics: {data['supported_topics']}")
            return data
        else:
            error_msg = response.json().get("detail") if response else "No response"
            self.log(f"✗ Webhook status failed: {error_msg}", "ERROR")
            return None
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("=" * 60)
        self.log("Starting SSI Issuer API Tests")
        self.log("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Create Invitation", self.test_create_invitation),
            ("Create Certificate Schema", self.test_create_certificate_schema),
            ("Show Users", self.test_show_users),
            ("Show Offers", self.test_show_offers),
            ("Show Certificates", self.test_show_certificates),
            ("Webhook Status", self.test_webhook_status),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n--- Running {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"✗ {test_name} failed with exception: {str(e)}", "ERROR")
                failed += 1
            
            time.sleep(0.5)  # Small delay between tests
        
        self.log("\n" + "=" * 60)
        self.log(f"Test Results: {passed} passed, {failed} failed")
        self.log("=" * 60)
        
        return failed == 0

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python test_issuer_endpoints.py")
        print("Make sure the SSI Issuer API is running on localhost:8001")
        return
    
    tester = IssuerTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()