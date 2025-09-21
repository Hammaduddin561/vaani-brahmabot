#!/usr/bin/env python3
"""
Twilio Integration Test for VAANI WhatsApp Bot
Tests Twilio connection, configuration, and messaging capabilities
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twilio_configuration():
    """Test if Twilio is properly configured"""
    print("🔍 Testing Twilio Configuration...")
    print("=" * 50)
    
    # Check environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    print(f"📋 Account SID: {account_sid}")
    print(f"🔑 Auth Token: {'SET' if auth_token else 'NOT SET'}")
    print(f"📞 Phone Number: {phone_number if phone_number else 'NOT SET'}")
    
    if not account_sid:
        print("❌ TWILIO_ACCOUNT_SID is missing")
        return False
    
    if not auth_token:
        print("❌ TWILIO_AUTH_TOKEN is missing")
        return False
        
    if not phone_number:
        print("⚠️ TWILIO_PHONE_NUMBER is missing - you'll need this for sending messages")
    
    print("✅ Basic configuration looks good")
    return True

def test_twilio_connection():
    """Test connection to Twilio API"""
    print("\n🌐 Testing Twilio API Connection...")
    print("=" * 50)
    
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            print("❌ Missing credentials for API test")
            return False
            
        # Initialize client
        client = Client(account_sid, auth_token)
        
        # Test connection by fetching account info
        account = client.api.accounts(account_sid).fetch()
        
        print(f"✅ Successfully connected to Twilio!")
        print(f"📊 Account Status: {account.status}")
        print(f"🏢 Account Name: {account.friendly_name}")
        
        return True
        
    except ImportError:
        print("❌ Twilio library not installed. Run: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_phone_numbers():
    """Test available phone numbers"""
    print("\n📞 Testing Phone Numbers...")
    print("=" * 50)
    
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)
        
        # Get incoming phone numbers
        numbers = client.incoming_phone_numbers.list(limit=10)
        
        if not numbers:
            print("❌ No phone numbers found in your Twilio account")
            print("💡 You need to buy a phone number with WhatsApp capability")
            return False
            
        print(f"✅ Found {len(numbers)} phone number(s):")
        for number in numbers:
            capabilities = []
            if hasattr(number, 'capabilities'):
                if number.capabilities.get('sms'):
                    capabilities.append('SMS')
                if number.capabilities.get('voice'):
                    capabilities.append('Voice')
                if number.capabilities.get('mms'):
                    capabilities.append('MMS')
            
            print(f"  📱 {number.phone_number} - {', '.join(capabilities) if capabilities else 'Basic'}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error fetching numbers: {e}")
        return False

def test_whatsapp_capability():
    """Test WhatsApp-specific capabilities"""
    print("\n💬 Testing WhatsApp Capabilities...")
    print("=" * 50)
    
    print("ℹ️ WhatsApp Business API requires:")
    print("  1. Approved WhatsApp Business Account")
    print("  2. Phone number verified for WhatsApp")
    print("  3. Webhook URL configured")
    
    # Check if we have WhatsApp-capable number
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    if twilio_number:
        if "whatsapp:" in twilio_number:
            print(f"✅ WhatsApp number configured: {twilio_number}")
        else:
            print(f"⚠️ Number configured but not in WhatsApp format: {twilio_number}")
            print("💡 WhatsApp numbers should be in format: whatsapp:+1234567890")
    else:
        print("❌ No WhatsApp number configured")
    
    return True

def main():
    """Run comprehensive Twilio tests"""
    print("🚀 VAANI Twilio Integration Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_twilio_configuration()
    
    if config_ok:
        # Test API connection
        connection_ok = test_twilio_connection()
        
        if connection_ok:
            # Test phone numbers
            numbers_ok = test_phone_numbers()
            
            # Test WhatsApp capabilities
            whatsapp_ok = test_whatsapp_capability()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    
    if config_ok:
        print("✅ Configuration: PASS")
        if 'connection_ok' in locals() and connection_ok:
            print("✅ API Connection: PASS")
            if 'numbers_ok' in locals() and numbers_ok:
                print("✅ Phone Numbers: AVAILABLE")
            else:
                print("⚠️ Phone Numbers: NEED SETUP")
        else:
            print("❌ API Connection: FAIL")
    else:
        print("❌ Configuration: FAIL")
    
    print("\n🔧 Next Steps:")
    if not config_ok:
        print("  1. Add missing Twilio credentials to .env file")
    else:
        print("  1. Add TWILIO_PHONE_NUMBER to .env file")
        print("  2. Ensure phone number supports WhatsApp")
        print("  3. Configure webhook URL in Twilio Console")
        print("  4. Test messaging functionality")

if __name__ == "__main__":
    main()