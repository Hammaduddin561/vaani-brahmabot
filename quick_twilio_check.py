#!/usr/bin/env python3
"""
Quick Twilio Status Check
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Import the WhatsApp bot to check its status
from enhanced_whatsapp_bot import EnhancedWhatsAppBot

def quick_status_check():
    print("🔍 Quick Twilio Status Check")
    print("=" * 40)
    
    # Environment variables
    print(f"TWILIO_ACCOUNT_SID: {'✅ Set' if os.getenv('TWILIO_ACCOUNT_SID') else '❌ Missing'}")
    print(f"TWILIO_AUTH_TOKEN: {'✅ Set' if os.getenv('TWILIO_AUTH_TOKEN') else '❌ Missing'}")
    print(f"TWILIO_PHONE_NUMBER: {'✅ Set' if os.getenv('TWILIO_PHONE_NUMBER') else '❌ Missing'}")
    print(f"Phone Number: {os.getenv('TWILIO_PHONE_NUMBER')}")
    
    # Initialize bot and check status
    try:
        bot = EnhancedWhatsAppBot()
        status = bot.get_twilio_status()
        
        print("\n📊 Bot Twilio Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
            
        print(f"\n✅ Twilio Integration Status: {'WORKING' if status['twilio_configured'] else 'NOT CONFIGURED'}")
        
        if status['twilio_configured'] and status['phone_configured']:
            print("🎉 Twilio is fully configured and ready for WhatsApp!")
        elif status['twilio_configured']:
            print("⚠️ Twilio configured but missing phone number")
        else:
            print("❌ Twilio not properly configured")
            
    except Exception as e:
        print(f"❌ Error checking bot status: {e}")

if __name__ == "__main__":
    quick_status_check()