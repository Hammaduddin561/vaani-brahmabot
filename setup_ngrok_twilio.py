#!/usr/bin/env python3
"""
Twilio + ngrok Configuration Helper for VAANI WhatsApp Bot
This script helps configure Twilio webhooks with ngrok for local development
"""

import os
import sys
import json
import subprocess
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_ngrok_installed():
    """Check if ngrok is installed"""
    # Try local ngrok first
    local_ngrok = os.path.join(os.getcwd(), 'ngrok.exe')
    if os.path.exists(local_ngrok):
        try:
            result = subprocess.run([local_ngrok, 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ ngrok is installed locally: {result.stdout.strip()}")
                return True
        except subprocess.SubprocessError:
            pass
    
    # Try system ngrok
    try:
        result = subprocess.run(['ngrok', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ngrok is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ ngrok not found")
            return False
    except FileNotFoundError:
        print("❌ ngrok not installed")
        return False

def install_ngrok_instructions():
    """Show instructions to install ngrok"""
    print("\n📥 To install ngrok:")
    print("1. Go to: https://ngrok.com/download")
    print("2. Download ngrok for Windows")
    print("3. Extract to a folder in your PATH")
    print("4. Sign up for free account at: https://dashboard.ngrok.com/signup")
    print("5. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("6. Run: ngrok config add-authtoken YOUR_AUTHTOKEN")

def start_ngrok_tunnel(port=8080):
    """Start ngrok tunnel to local server"""
    print(f"\n🌐 Starting ngrok tunnel to localhost:{port}...")
    
    try:
        # Start ngrok in background
        ngrok_cmd = os.path.join(os.getcwd(), 'ngrok.exe') if os.path.exists(os.path.join(os.getcwd(), 'ngrok.exe')) else 'ngrok'
        process = subprocess.Popen([ngrok_cmd, 'http', str(port), '--log=stdout'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get ngrok tunnels info
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                
                if tunnels['tunnels']:
                    tunnel = tunnels['tunnels'][0]
                    public_url = tunnel['public_url']
                    print(f"✅ ngrok tunnel active: {public_url}")
                    return public_url, process
                else:
                    print("❌ No active tunnels found")
                    return None, process
            else:
                print("❌ Could not get tunnel information")
                return None, process
                
        except requests.RequestException:
            print("❌ ngrok API not accessible")
            return None, process
            
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None, None

def configure_twilio_webhook(webhook_url):
    """Configure Twilio webhook using API"""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            print("❌ Twilio credentials not configured")
            return False
        
        client = Client(account_sid, auth_token)
        
        # Get phone numbers
        numbers = client.incoming_phone_numbers.list()
        
        if not numbers:
            print("❌ No phone numbers in Twilio account")
            print("💡 You need to purchase a phone number first")
            return False
        
        # Configure webhook for each number
        webhook_endpoint = f"{webhook_url}/webhook/whatsapp"
        
        for number in numbers:
            try:
                # Update SMS webhook
                number.update(sms_url=webhook_endpoint, sms_method='POST')
                print(f"✅ SMS webhook configured for {number.phone_number}")
                
                # Note: WhatsApp webhooks are configured differently in Twilio Console
                
            except Exception as e:
                print(f"❌ Failed to configure webhook for {number.phone_number}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configuring Twilio webhook: {e}")
        return False

def show_manual_configuration(webhook_url):
    """Show manual configuration steps"""
    print(f"\n🔧 MANUAL TWILIO CONFIGURATION")
    print("=" * 50)
    print(f"📋 Webhook URL: {webhook_url}/webhook/whatsapp")
    print("\n📞 For SMS Configuration:")
    print("1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    print("2. Click on your phone number")
    print("3. In 'Messaging' section:")
    print(f"   - Webhook URL: {webhook_url}/webhook/whatsapp")
    print("   - HTTP Method: POST")
    print("4. Save configuration")
    
    print("\n💬 For WhatsApp Configuration:")
    print("1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
    print("2. Join the WhatsApp Sandbox")
    print("3. Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox")
    print(f"4. Set Webhook URL: {webhook_url}/webhook/whatsapp")
    print("5. Set HTTP Method: POST")
    print("6. Save configuration")

def test_webhook_endpoint(webhook_url):
    """Test if the webhook endpoint is accessible"""
    test_url = f"{webhook_url}/api/system/twilio-status"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Webhook endpoint accessible: {test_url}")
            return True
        else:
            print(f"⚠️ Webhook endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook endpoint not accessible: {e}")
        return False

def create_test_message():
    """Create a test message for WhatsApp"""
    return """
🚀 **VAANI Test Message** 🚀

Hello! This is a test message from VAANI - The BrahmaBot.

If you're receiving this, your WhatsApp integration is working perfectly!

Try asking me:
• "Tell me about ISRO"
• "What is Chandrayaan-3?"
• "List satellites"

🌟 Ready to explore space technology together!
"""

def main():
    """Main configuration flow"""
    print("🚀 VAANI Twilio + ngrok Configuration Helper")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:8080/api/system/twilio-status', timeout=5)
        print("✅ VAANI server is running on localhost:8080")
    except:
        print("❌ VAANI server is not running")
        print("💡 Please start the server first: python enhanced_app.py")
        return
    
    # Check ngrok installation
    if not check_ngrok_installed():
        install_ngrok_instructions()
        return
    
    # Start ngrok tunnel
    public_url, ngrok_process = start_ngrok_tunnel(8080)
    
    if not public_url:
        print("❌ Failed to start ngrok tunnel")
        return
    
    try:
        # Test webhook endpoint
        webhook_accessible = test_webhook_endpoint(public_url)
        
        # Show configuration instructions
        show_manual_configuration(public_url)
        
        # Update .env file with webhook URL
        print(f"\n💾 Updating .env file...")
        
        # Read current .env
        env_path = '.env'
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        # Add or update webhook URL
        webhook_line = f"TWILIO_WEBHOOK_URL={public_url}/webhook/whatsapp"
        
        if "TWILIO_WEBHOOK_URL=" in env_content:
            # Replace existing
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("TWILIO_WEBHOOK_URL="):
                    lines[i] = webhook_line
                    break
            env_content = '\n'.join(lines)
        else:
            # Add new
            env_content += f"\n{webhook_line}\n"
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file updated with webhook URL")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Configure Twilio webhook using the manual steps above")
        print("2. Test WhatsApp messaging")
        print("3. Keep this terminal open (ngrok tunnel active)")
        print("\n⚠️ IMPORTANT: Don't close this terminal - ngrok tunnel will stop!")
        
        # Wait for user input
        print(f"\n📱 Test your WhatsApp integration now!")
        print(f"📧 Webhook URL: {public_url}/webhook/whatsapp")
        
        input("\nPress Enter to stop ngrok tunnel...")
        
    finally:
        # Clean up ngrok process
        if ngrok_process:
            ngrok_process.terminate()
            print("🛑 ngrok tunnel stopped")

if __name__ == "__main__":
    main()