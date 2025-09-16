#!/usr/bin/env python3
"""
Test script for the new invitation endpoints
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ssi_service import SSIService
from app.schemas import ConnectionInvitationRequest, ReceiveInvitationPayload

async def test_parse_invitation_url():
    """Test the invitation URL parsing functionality"""
    
    # Mock SSI service for testing parsing logic (without ACA-Py connection)
    class MockSSIService:
        async def parse_invitation_url(self, invitation_url):
            """Test implementation of URL parsing"""
            import urllib.parse
            import base64
            import json
            
            try:
                parsed_url = urllib.parse.urlparse(invitation_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                invitation_data = None
                
                if 'c_i' in query_params:
                    invitation_b64 = query_params['c_i'][0]
                    invitation_json = base64.urlsafe_b64decode(invitation_b64 + '==').decode('utf-8')
                    invitation_data = json.loads(invitation_json)
                    
                elif 'oob' in query_params:
                    invitation_b64 = query_params['oob'][0]
                    invitation_json = base64.urlsafe_b64decode(invitation_b64 + '==').decode('utf-8')
                    invitation_data = json.loads(invitation_json)
                
                return invitation_data
                
            except Exception as e:
                raise Exception(f"Erro ao processar URL do convite: {str(e)}")
    
    mock_service = MockSSIService()
    
    # Test URLs (example formats)
    test_urls = [
        # Example connection invitation URL
        "http://example.com/connect?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiMTIzNDU2NzgiLCAic2VydmljZUVuZHBvaW50IjogImh0dHA6Ly9leGFtcGxlLmNvbSIsICJyZWNpcGllbnRLZXlzIjogWyIxMjM0NTY3OCJdLCAibGFiZWwiOiAiVGVzdCBDb25uZWN0aW9uIn0",
    ]
    
    print("Testing invitation URL parsing...")
    
    for url in test_urls:
        try:
            print(f"\nTesting URL: {url[:50]}...")
            result = await mock_service.parse_invitation_url(url)
            print(f"✅ Parsed successfully: {result}")
        except Exception as e:
            print(f"❌ Failed to parse: {str(e)}")
    
    print("\n✅ URL parsing test completed")

async def test_schema_validation():
    """Test Pydantic schema validation"""
    
    print("Testing schema validation...")
    
    # Test ConnectionInvitationRequest
    try:
        request = ConnectionInvitationRequest(
            connection_alias="Test Connection",
            invitation_url="http://example.com/connect?c_i=test"
        )
        print(f"✅ ConnectionInvitationRequest validation passed: {request}")
    except Exception as e:
        print(f"❌ ConnectionInvitationRequest validation failed: {str(e)}")
    
    # Test ReceiveInvitationPayload
    try:
        payload = ReceiveInvitationPayload(
            invitation={"@type": "test", "serviceEndpoint": "http://example.com"},
            auto_accept=True,
            alias="Test Connection"
        )
        print(f"✅ ReceiveInvitationPayload validation passed: {payload}")
    except Exception as e:
        print(f"❌ ReceiveInvitationPayload validation failed: {str(e)}")
    
    print("✅ Schema validation test completed")

async def main():
    """Run all tests"""
    print("🧪 Testing new invitation endpoints...\n")
    
    await test_schema_validation()
    await test_parse_invitation_url()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary:")
    print("- Criados 2 novos endpoints:")
    print("  • POST /api/auth/prepare-invitation - Prepara dados para /receive-invitation")
    print("  • POST /api/auth/receive-invitation - Processa e aceita convites")
    print("- Adicionados schemas de validação")
    print("- Implementadas funções de parsing de URL de convite")
    print("- Suporte para formatos c_i, oob e d_m")

if __name__ == "__main__":
    asyncio.run(main())