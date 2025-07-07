# 🚀 Complete Setup Guide - Instagram AI Agent

This guide will walk you through setting up your Instagram AI Agent from scratch to creating your first automated video.

## 📋 Prerequisites Checklist

Before you start, make sure you have:
- [ ] Python 3.8 or higher installed
- [ ] A Google account (for Google Sheets and Cloud Console)
- [ ] Some royalty-free music files (.mp3 format)
- [ ] A computer with at least 2GB free disk space

## 🎯 Step-by-Step Setup

### Step 1: Initial Setup (5 minutes)

1. **Run the Quick Setup Script**
   ```bash
   python quick_setup.py
   ```
   This will:
   - Check your Python version
   - Install all required dependencies
   - Create necessary folders
   - Guide you through the remaining steps

### Step 2: Google Cloud Setup (10 minutes)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click the project dropdown at the top
   - Click "New Project"
   - Name it "Instagram AI Agent"
   - Click "Create"

3. **Enable Google Sheets API**
   - In the search bar, type "Google Sheets API"
   - Click on "Google Sheets API"
   - Click "Enable"

4. **Create Service Account**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name it "sheets-reader"
   - Click "Create and Continue"
   - Click "Done"

5. **Generate API Key**
   - Click on your service account name
   - Go to "KEYS" tab
   - Click "ADD KEY" > "Create new key"
   - Select "JSON" format
   - Click "CREATE"
   - A file will download automatically

6. **Set Up Credentials**
   - Rename the downloaded file to `credentials.json`
   - Move it to your project folder
   - Open the file and copy the `client_email` address

### Step 3: Google Sheets Setup (5 minutes)

1. **Create Your Quotes Sheet**
   - Go to: https://sheets.google.com
   - Create a new spreadsheet
   - Name it "Instagram Quotes"

2. **Set Up the Structure**
   - In cell A1, type: `Quote`
   - In cell B1, type: `Author`
   - Add some sample quotes:
     ```
     A2: "Be the change you wish to see in the world"
     B2: "Mahatma Gandhi"
     A3: "The only way to do great work is to love what you do"
     B3: "Steve Jobs"
     ```

3. **Share the Sheet**
   - Click the "Share" button
   - Paste the `client_email` from your credentials.json
   - Give it "Viewer" access
   - Click "Send"

### Step 4: Add Music Files (5 minutes)

1. **Download Royalty-Free Music**
   - Visit one of these sites:
     - [Pixabay Music](https://pixabay.com/music/)
     - [Bensound](https://bensound.com)
     - [YouTube Audio Library](https://studio.youtube.com)
   - Download 3-5 .mp3 files

2. **Add to Project**
   - Place the .mp3 files in the `music/` folder
   - Make sure they're .mp3 format (not .MP3)

### Step 5: Test Your Setup (2 minutes)

1. **Run the Test**
   ```bash
   python setup_google_sheets.py
   ```
   You should see: "✅ Successfully connected to Google Sheets!"

2. **Create Your First Video**
   ```bash
   python main.py
   ```
   This will create `output.mp4` in your project folder!

## 🎬 Creating Your First Video

Once setup is complete, creating videos is simple:

```bash
python main.py
```

**What happens:**
1. Fetches a random quote from your Google Sheet
2. Selects a random music file
3. Creates a 10-second video with the quote and music
4. Saves it as `output.mp4`

## 🤖 Setting Up Automation

### Windows (Task Scheduler)

1. **Open Task Scheduler**
   - Press Win + R, type `taskschd.msc`
   - Click "Create Basic Task"

2. **Configure the Task**
   - Name: "Instagram AI Agent"
   - Trigger: Daily
   - Time: 10:00 AM
   - Action: Start a program
   - Program: `python`
   - Arguments: `automation.py`

### Mac/Linux (Cron)

1. **Open Crontab**
   ```bash
   crontab -e
   ```

2. **Add the Line**
   ```bash
   0 10 * * * /usr/bin/python3 /path/to/your/project/automation.py
   ```

## 🎨 Customization Options

### Change Video Settings

Edit `config.py` to customize:

```python
# Video dimensions
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Duration
VIDEO_DURATION_SECONDS = 10

# Text styling
QUOTE_FONT_SIZE = 80
QUOTE_COLOR = 'white'
AUTHOR_COLOR = 'gold'
```

### Use Presets

Apply platform-specific presets:

```python
from config import apply_preset

# For Instagram Stories
apply_preset('instagram_story')

# For YouTube Shorts
apply_preset('youtube_short')

# For TikTok
apply_preset('tiktok')
```

## 🔧 Troubleshooting

### Common Issues

**"No .mp3 files found"**
- Check that files are in the `music/` folder
- Ensure file extensions are lowercase (.mp3)

**"Error connecting to Google Sheets"**
- Verify `credentials.json` is in the project folder
- Check that you shared the sheet with the service account email
- Ensure the sheet is named exactly "Instagram Quotes"

**"Font not found"**
- Change the font in `config.py` to a system font:
  - Windows: 'Arial', 'Times New Roman'
  - Mac: 'Helvetica', 'Times'
  - Linux: 'DejaVu Sans', 'Liberation Sans'

### Getting Help

1. **Check the logs**
   - Manual runs: `instagram_agent.log`
   - Automated runs: `logs/automation_YYYYMMDD.log`

2. **Run diagnostics**
   ```bash
   python setup_google_sheets.py
   ```

3. **Read the full documentation**
   - See `README.md` for detailed information

## 🎉 You're Ready!

Your Instagram AI Agent is now set up and ready to create beautiful quote videos automatically!

**Next Steps:**
1. Add more quotes to your Google Sheet
2. Add more music files to the `music/` folder
3. Customize the video style in `config.py`
4. Set up automation to run daily
5. Monitor the logs to ensure everything works smoothly

**Remember:** This tool creates videos but doesn't post them automatically (to comply with Instagram's Terms of Service). You'll need to manually upload the generated videos to Instagram.

---

**Happy creating! 🎬✨** 