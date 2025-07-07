"""
Instagram API Setup Script
Guides users through the complete Meta Developer setup process for Instagram posting
"""

import os
import json
import webbrowser
import requests
from datetime import datetime

def print_header():
    """Print a nice header."""
    print("=" * 80)
    print("📱 INSTAGRAM API SETUP - Meta Developer Platform")
    print("=" * 80)
    print()

def check_instagram_requirements():
    """Check if user meets Instagram API requirements."""
    print("🔍 Checking Instagram API Requirements...")
    print()
    
    requirements = [
        "✅ Instagram Business Account (not personal)",
        "✅ Facebook Page linked to Instagram",
        "✅ Meta Developer Account",
        "✅ App with Instagram permissions",
        "✅ Long-lived access token"
    ]
    
    for req in requirements:
        print(req)
    
    print("\n📋 If any requirement is missing, follow the setup steps below.")
    return True

def setup_instagram_business_account():
    """Guide user through Instagram Business Account setup."""
    print("\n📱 STEP 1: Instagram Business Account Setup")
    print("=" * 50)
    print("1. Open Instagram app on your phone")
    print("2. Go to Settings → Account")
    print("3. Tap 'Switch to Business Account'")
    print("4. Choose a category (e.g., 'Personal Blog')")
    print("5. Add business information (optional)")
    print("6. Complete the setup")
    print()
    print("⚠️  IMPORTANT: You must have a Business or Creator account!")
    print("   Personal accounts cannot use the Instagram API.")
    
    response = input("\nHave you completed this step? (y/n): ")
    return response.lower() in ['y', 'yes']

def setup_facebook_page():
    """Guide user through Facebook Page setup."""
    print("\n📘 STEP 2: Facebook Page Setup")
    print("=" * 50)
    print("1. Go to https://facebook.com/pages/create")
    print("2. Create a new Facebook Page")
    print("3. Choose a category (e.g., 'Personal Blog')")
    print("4. Add page information")
    print("5. Link your Instagram account:")
    print("   - Go to Page Settings")
    print("   - Click 'Linked Accounts'")
    print("   - Connect your Instagram Business Account")
    print()
    
    response = input("Have you completed this step? (y/n): ")
    return response.lower() in ['y', 'yes']

def setup_meta_developer_account():
    """Guide user through Meta Developer Account setup."""
    print("\n👨‍💻 STEP 3: Meta Developer Account Setup")
    print("=" * 50)
    print("1. Go to https://developers.facebook.com")
    print("2. Click 'Get Started' or 'Log In'")
    print("3. Complete developer account verification")
    print("4. Accept terms and conditions")
    print()
    
    response = input("Have you completed this step? (y/n): ")
    if response.lower() in ['y', 'yes']:
        print("\nWould you like to open Meta Developer Console now? (y/n): ")
        if input().lower() in ['y', 'yes']:
            webbrowser.open('https://developers.facebook.com')
        return True
    return False

def create_meta_app():
    """Guide user through Meta App creation."""
    print("\n🔧 STEP 4: Create Meta App")
    print("=" * 50)
    print("1. In Meta Developer Console, click 'Create App'")
    print("2. Choose 'Business' as the app type")
    print("3. Fill in app details:")
    print("   - App Name: 'Instagram AI Agent'")
    print("   - App Contact Email: your email")
    print("   - Business Account: your business account")
    print("4. Click 'Create App'")
    print()
    
    response = input("Have you created the app? (y/n): ")
    if response.lower() in ['y', 'yes']:
        print("\nWould you like to open Meta Developer Console now? (y/n): ")
        if input().lower() in ['y', 'yes']:
            webbrowser.open('https://developers.facebook.com/apps/')
        return True
    return False

def add_instagram_permissions():
    """Guide user through adding Instagram permissions."""
    print("\n📱 STEP 5: Add Instagram Permissions")
    print("=" * 50)
    print("1. In your app dashboard, click 'Add Product'")
    print("2. Find and add 'Instagram Basic Display'")
    print("3. Go to 'Instagram Basic Display' → 'Basic Display'")
    print("4. Add your Instagram account:")
    print("   - Click 'Add Instagram Test Users'")
    print("   - Enter your Instagram username")
    print("   - Accept the invitation on Instagram")
    print("5. Go to 'Instagram Graph API' → 'Getting Started'")
    print("6. Add permissions:")
    print("   - instagram_basic")
    print("   - pages_show_list")
    print("   - instagram_content_publish")
    print()
    
    response = input("Have you added the permissions? (y/n): ")
    return response.lower() in ['y', 'yes']

def get_instagram_user_id():
    """Help user get their Instagram User ID."""
    print("\n🆔 STEP 6: Get Instagram User ID")
    print("=" * 50)
    print("Method 1: Using Graph API Explorer")
    print("1. Go to https://developers.facebook.com/tools/explorer/")
    print("2. Select your app from dropdown")
    print("3. Add permissions: instagram_basic, pages_show_list")
    print("4. Click 'Generate Access Token'")
    print("5. Make this request:")
    print("   GET /me/accounts")
    print("6. Find your page ID, then make:")
    print("   GET /{page-id}?fields=instagram_business_account")
    print("7. The 'id' field is your Instagram User ID")
    print()
    
    print("Method 2: Using Instagram Basic Display")
    print("1. Go to your app → Instagram Basic Display")
    print("2. Click 'Basic Display'")
    print("3. Your Instagram User ID is shown there")
    print()
    
    user_id = input("Enter your Instagram User ID: ").strip()
    return user_id if user_id else None

def generate_access_token():
    """Guide user through generating access token."""
    print("\n🔑 STEP 7: Generate Long-Lived Access Token")
    print("=" * 50)
    print("1. Go to https://developers.facebook.com/tools/explorer/")
    print("2. Select your app from dropdown")
    print("3. Add these permissions:")
    print("   - instagram_basic")
    print("   - pages_show_list")
    print("   - instagram_content_publish")
    print("   - pages_read_engagement")
    print("4. Click 'Generate Access Token'")
    print("5. Copy the generated token")
    print()
    print("⚠️  IMPORTANT: This token expires in 60 days!")
    print("   You'll need to regenerate it periodically.")
    print()
    
    response = input("Would you like to open Graph API Explorer now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        webbrowser.open('https://developers.facebook.com/tools/explorer/')
    
    access_token = input("\nEnter your access token: ").strip()
    return access_token if access_token else None

def test_instagram_connection(access_token, user_id):
    """Test the Instagram API connection."""
    print("\n🧪 Testing Instagram API Connection...")
    
    try:
        # Test basic connection
        url = f"https://graph.facebook.com/v18.0/{user_id}"
        params = {
            'fields': 'id,username',
            'access_token': access_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'error' in data:
            print(f"❌ API Error: {data['error']['message']}")
            return False
        
        print(f"✅ Connected successfully!")
        print(f"   Username: {data.get('username', 'Unknown')}")
        print(f"   Account Type: {data.get('account_type', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def save_instagram_config(access_token, user_id):
    """Save Instagram configuration to config.py."""
    print("\n💾 Saving Instagram Configuration...")
    
    try:
        # Read current config
        with open('config.py', 'r') as f:
            config_content = f.read()
        
        # Update Instagram credentials
        config_content = config_content.replace(
            'INSTAGRAM_ACCESS_TOKEN = ""',
            f'INSTAGRAM_ACCESS_TOKEN = "{access_token}"'
        )
        config_content = config_content.replace(
            'INSTAGRAM_USER_ID = ""',
            f'INSTAGRAM_USER_ID = "{user_id}"'
        )
        config_content = config_content.replace(
            'ENABLE_INSTAGRAM_POSTING = False',
            'ENABLE_INSTAGRAM_POSTING = True'
        )
        
        # Write updated config
        with open('config.py', 'w') as f:
            f.write(config_content)
        
        print("✅ Instagram configuration saved to config.py")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False

def create_instagram_credentials_file(access_token, user_id):
    """Create a separate credentials file for Instagram."""
    try:
        credentials = {
            'instagram_access_token': access_token,
            'instagram_user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'note': 'Long-lived access token expires in 60 days'
        }
        
        with open('instagram_credentials.json', 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print("✅ Instagram credentials saved to instagram_credentials.json")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save credentials file: {e}")
        return False

def main():
    """Main setup function."""
    print_header()
    
    print("🎯 This script will guide you through setting up Instagram API access")
    print("   for automatic posting to your Instagram Business account.")
    print()
    
    if not check_instagram_requirements():
        return
    
    # Step-by-step setup
    steps = [
        ("Instagram Business Account", setup_instagram_business_account),
        ("Facebook Page", setup_facebook_page),
        ("Meta Developer Account", setup_meta_developer_account),
        ("Meta App Creation", create_meta_app),
        ("Instagram Permissions", add_instagram_permissions)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"\n❌ {step_name} setup incomplete. Please complete this step and run the script again.")
            return
    
    # Get credentials
    print(f"\n{'='*20} Get Credentials {'='*20}")
    user_id = get_instagram_user_id()
    if not user_id:
        print("❌ Instagram User ID is required. Please get it and run the script again.")
        return
    
    access_token = generate_access_token()
    if not access_token:
        print("❌ Access token is required. Please get it and run the script again.")
        return
    
    # Test connection
    if not test_instagram_connection(access_token, user_id):
        print("❌ Instagram API connection failed. Please check your credentials.")
        return
    
    # Save configuration
    if not save_instagram_config(access_token, user_id):
        print("❌ Failed to save configuration.")
        return
    
    if not create_instagram_credentials_file(access_token, user_id):
        print("⚠️  Failed to save credentials file, but config.py was updated.")
    
    print("\n" + "="*80)
    print("🎉 INSTAGRAM API SETUP COMPLETE!")
    print("="*80)
    print()
    print("✅ Your Instagram AI Agent can now post automatically!")
    print()
    print("📋 Next Steps:")
    print("1. Test the setup: python main.py")
    print("2. Enable cloud automation: python cloud_automation.py start")
    print("3. Monitor logs for posting status")
    print()
    print("⚠️  Important Notes:")
    print("- Access tokens expire in 60 days")
    print("- You'll need to regenerate the token periodically")
    print("- Keep your credentials secure")
    print("- Monitor your Instagram account for any issues")
    print()
    print("🚀 Happy posting!")

if __name__ == "__main__":
    main() 