#!/usr/bin/env python3
"""
Test script to simulate Twilio WhatsApp webhook
"""

import requests
import json

def test_local_webhook():
    """Test the local webhook endpoint"""
    
    # Simulate Twilio webhook data
    webhook_data = {
        'Body': 'Hi',
        'From': 'whatsapp:+1234567890',
        'MessageSid': 'test_message_123',
        'AccountSid': 'test_account',
        'ToCountry': 'US',
        'ToState': '',
        'SmsMessageSid': 'test_sms_123',
        'NumMedia': '0',
        'ToCity': '',
        'FromCountry': 'US',
        'To': 'whatsapp:+14155238886',
        'FromCity': '',
        'FromState': '',
        'SmsStatus': 'received',
        'FromZip': '',
        'ToZip': ''
    }
    
    print("🔍 Testing Local Webhook Endpoint")
    print("=" * 50)
    
    # Test local endpoint
    try:
        response = requests.post(
            'http://localhost:8080/webhook/whatsapp',
            data=webhook_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        print(f"✅ Local webhook response: {response.status_code}")
        print(f"📄 Response content: {response.text}")
        
    except Exception as e:
        print(f"❌ Local webhook error: {e}")

def test_ngrok_webhook():
    """Test the ngrok webhook endpoint"""
    
    # Simulate Twilio webhook data
    webhook_data = {
        'Body': 'Hi',
        'From': 'whatsapp:+1234567890',
        'MessageSid': 'test_message_123',
        'AccountSid': 'test_account',
        'ToCountry': 'US',
        'ToState': '',
        'SmsMessageSid': 'test_sms_123',
        'NumMedia': '0',
        'ToCity': '',
        'FromCountry': 'US',
        'To': 'whatsapp:+14155238886',
        'FromCity': '',
        'FromState': '',
        'SmsStatus': 'received',
        'FromZip': '',
        'ToZip': ''
    }
    
    print("\n🌐 Testing ngrok Webhook Endpoint")
    print("=" * 50)
    
    # Test ngrok endpoint
    try:
        response = requests.post(
            'https://ffb318baa276.ngrok-free.app/webhook/whatsapp',
            data=webhook_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'ngrok-skip-browser-warning': 'true'
            },
            timeout=15
        )
        
        print(f"✅ ngrok webhook response: {response.status_code}")
        print(f"📄 Response content: {response.text}")
        
    except Exception as e:
        print(f"❌ ngrok webhook error: {e}")

if __name__ == "__main__":
    test_local_webhook()
    test_ngrok_webhook()