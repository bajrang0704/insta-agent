"""
Quick Setup Script for Instagram AI Agent
This script guides you through the initial setup process.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_header():
    """Print a nice header."""
    print("=" * 60)
    print("🤖 INSTAGRAM AI AGENT - QUICK SETUP")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible!")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_folders():
    """Create necessary folders."""
    print("\n📁 Creating folders...")
    folders = ['music', 'logs']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Created {folder}/ folder")
        else:
            print(f"✅ {folder}/ folder already exists")

def check_credentials():
    """Check if credentials file exists."""
    print("\n🔐 Checking Google API credentials...")
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found!")
        return True
    else:
        print("❌ credentials.json not found!")
        print("\n📋 To get your credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API")
        print("4. Create a Service Account")
        print("5. Download the JSON credentials file")
        print("6. Rename it to 'credentials.json' and place it in this folder")
        
        # Ask if user wants to open the Google Cloud Console
        response = input("\nWould you like to open Google Cloud Console now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            webbrowser.open('https://console.cloud.google.com/')
        
        return False

def check_music_files():
    """Check if music files are present."""
    print("\n🎵 Checking music files...")
    music_files = [f for f in os.listdir('music') if f.endswith('.mp3')]
    if music_files:
        print(f"✅ Found {len(music_files)} music files")
        return True
    else:
        print("⚠️  No .mp3 files found in music/ folder")
        print("\n📋 To add music files:")
        print("1. Download royalty-free music from:")
        print("   - Pixabay Music (pixabay.com/music/)")
        print("   - Bensound (bensound.com)")
        print("   - YouTube Audio Library")
        print("2. Place .mp3 files in the music/ folder")
        return False

def create_sample_google_sheet():
    """Provide instructions for creating Google Sheet."""
    print("\n📊 Google Sheet Setup:")
    print("1. Go to https://sheets.google.com")
    print("2. Create a new spreadsheet")
    print("3. Name it 'Instagram Quotes'")
    print("4. Add headers: A1='Quote', B1='Author'")
    print("5. Add some sample quotes:")
    print("   A2: 'Be the change you wish to see in the world'")
    print("   B2: 'Mahatma Gandhi'")
    print("   A3: 'The only way to do great work is to love what you do'")
    print("   B3: 'Steve Jobs'")
    print("6. Share with your service account email (from credentials.json)")
    
    response = input("\nWould you like to open Google Sheets now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        webbrowser.open('https://sheets.google.com')

def test_setup():
    """Test the setup by running the setup script."""
    print("\n🧪 Testing setup...")
    try:
        result = subprocess.run([sys.executable, "setup_google_sheets.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Setup test passed!")
            return True
        else:
            print("❌ Setup test failed!")
            print("Error output:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running setup test: {e}")
        return False

def main():
    """Main setup function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create folders
    create_folders()
    
    # Check credentials
    credentials_ok = check_credentials()
    
    # Check music files
    music_ok = check_music_files()
    
    # Provide Google Sheet instructions
    create_sample_google_sheet()
    
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY:")
    print("=" * 60)
    
    if credentials_ok and music_ok:
        print("✅ All components ready!")
        print("\n🎉 You can now run the AI agent!")
        print("Try: python main.py")
        
        # Test the setup
        if test_setup():
            print("\n🚀 Setup complete! Your Instagram AI Agent is ready to use!")
        else:
            print("\n⚠️  Setup test failed. Please check the errors above.")
    else:
        print("⚠️  Some components need attention:")
        if not credentials_ok:
            print("   - Google API credentials missing")
        if not music_ok:
            print("   - Music files missing")
        print("\nPlease complete the missing steps and run this script again.")
    
    print("\n📖 For detailed instructions, see README.md")
    print("🔧 For troubleshooting, run: python setup_google_sheets.py")

if __name__ == "__main__":
    main() 