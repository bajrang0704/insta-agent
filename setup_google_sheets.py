"""
Google Sheets Setup Script for Instagram AI Agent
This script helps you set up the Google Sheets API connection.
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

def create_sample_credentials():
    """Creates a sample credentials.json file structure."""
    sample_credentials = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    with open('credentials.json', 'w') as f:
        json.dump(sample_credentials, f, indent=2)
    
    print("Sample credentials.json created. Please replace with your actual credentials.")

def test_google_sheets_connection():
    """Tests the connection to Google Sheets."""
    try:
        if not os.path.exists('credentials.json'):
            print("❌ credentials.json not found!")
            print("Please follow the setup instructions in README.md")
            return False
        
        gc = gspread.service_account(filename='credentials.json')
        
        # Try to open the sheet
        try:
            worksheet = gc.open('Instagram quotes').sheet1
            print("✅ Successfully connected to Google Sheets!")
            print(f"📊 Found worksheet: {worksheet.title}")
            
            # Get the first few rows to verify data
            records = worksheet.get_all_records()
            if records:
                print(f"📝 Found {len(records)} quotes in the sheet")
                print("Sample quote:", records[0])
            else:
                print("⚠️  No quotes found in the sheet. Please add some quotes!")
            
            return True
            
        except gspread.SpreadsheetNotFound:
            print("❌ Could not find 'Instagram Quotes' spreadsheet!")
            print("Please make sure:")
            print("1. You have created a Google Sheet named 'Instagram Quotes'")
            print("2. You have shared it with your service account email")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return False

def create_sample_sheet_structure():
    """Provides instructions for creating the Google Sheet structure."""
    print("\n📋 GOOGLE SHEET SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to sheets.google.com and create a new spreadsheet")
    print("2. Name it 'Instagram Quotes'")
    print("3. In cell A1, type: Quote")
    print("4. In cell B1, type: Author")
    print("5. Add some sample quotes:")
    print("   A2: 'Be the change you wish to see in the world'")
    print("   B2: 'Mahatma Gandhi'")
    print("   A3: 'The only way to do great work is to love what you do'")
    print("   B3: 'Steve Jobs'")
    print("6. Share the sheet with your service account email (found in credentials.json)")
    print("7. Give it 'Viewer' access")
    print("=" * 50)

def main():
    """Main setup function."""
    print("🔧 Instagram AI Agent - Google Sheets Setup")
    print("=" * 50)
    
    # Check if credentials exist
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("\n📝 SETUP INSTRUCTIONS:")
        print("1. Go to Google Cloud Console (console.cloud.google.com)")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API")
        print("4. Create a Service Account")
        print("5. Download the JSON credentials file")
        print("6. Rename it to 'credentials.json' and place it in this folder")
        print("7. Run this script again to test the connection")
        
        create_sample_credentials()
        return
    
    # Test connection
    print("🔍 Testing Google Sheets connection...")
    if test_google_sheets_connection():
        print("\n✅ Setup complete! You can now run main.py")
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
        create_sample_sheet_structure()

if __name__ == "__main__":
    main() 