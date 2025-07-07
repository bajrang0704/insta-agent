# Instagram AI Agent 🤖

An advanced automated Instagram video generator that creates quote videos with background music, runs in the cloud, and uploads to your Google Drive. This AI agent fetches quotes from Google Sheets sequentially, pairs them with music in order, and generates beautiful Instagram Reels/Stories automatically at optimal posting times.

## ✨ Features

- **🌐 Cloud-Based Automation**: Runs on Google Cloud, AWS Lambda, Heroku, or any cloud platform
- **📊 Sequential Processing**: Uses quotes and music in order, not randomly
- **☁️ Google Drive Integration**: Automatically uploads videos to your Google One storage
- **⏰ Optimal Timing**: Posts at the best times for maximum Instagram engagement
- **🎬 Enhanced Transitions**: Professional fade effects, floating animations, and zoom effects
- **🔄 Weekly Reset**: Automatically resets to first quote every week
- **📈 Progress Tracking**: Keeps track of which quote/music pair to use next
- **📱 Instagram Optimized**: Perfect 1080x1920 format for Reels and Stories
- **🎵 Background Music**: Supports multiple music files with automatic selection
- **📋 Google Sheets Integration**: Fetches quotes from your personal Google Sheets database

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud account (free tier available)
- Google One subscription (for 2TB storage)
- Royalty-free music files (.mp3 format)

### Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd instagram-ai-agent
   ```

2. **Run the Quick Setup Script**
   ```bash
   python quick_setup.py
   ```

3. **Set up Google Cloud and Sheets** (follow the prompts)

4. **Add music files to the `music/` folder**

5. **Test your setup**
   ```bash
   python main.py
   ```

## 🎯 Key Features Explained

### Sequential Processing
Instead of random selection, the system uses quotes and music in order:
- Quote 1 + Music 1 → Video 1
- Quote 2 + Music 2 → Video 2
- Quote 3 + Music 3 → Video 3
- ... and so on

When all quotes/music are used, it cycles back to the beginning. Every week, it resets to start from the first quote.

### Cloud Deployment
The system can run on various cloud platforms:

**Google Cloud Platform (Recommended):**
```bash
python cloud_deployment.py google_cloud
```

**AWS Lambda:**
```bash
python cloud_deployment.py aws_lambda
```

**Heroku:**
```bash
python cloud_deployment.py heroku
```

**DigitalOcean:**
```bash
python cloud_deployment.py digitalocean
```

### Google Drive Integration
- Videos are automatically uploaded to your Google Drive
- Creates a folder called "Instagram AI Videos"
- Uses your Google One 2TB storage
- Easy access from anywhere

### Optimal Posting Times
The system posts at the best times for Instagram engagement:
- 9:00 AM
- 12:00 PM  
- 3:00 PM
- 6:00 PM
- 8:00 PM

## 📖 Usage

### Manual Video Generation

```bash
python main.py
```

### Cloud Automation

**Start the scheduler:**
```bash
python cloud_automation.py start
```

**Run once:**
```bash
python cloud_automation.py run
```

**Check status:**
```bash
python cloud_automation.py status
```

### Docker Deployment

**Build and run:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

## 🎨 Customization

### Video Settings (config.py)

```python
# Video dimensions
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Duration
VIDEO_DURATION_SECONDS = 15

# Text styling
QUOTE_FONT_SIZE = 80
QUOTE_COLOR = 'white'
AUTHOR_COLOR = 'gold'

# Transitions
FADE_IN_DURATION = 1.5
USE_ZOOM_EFFECT = True
USE_FLOAT_EFFECT = True
```

### Sequential Processing Settings

```python
# Sequential mode
SEQUENTIAL_MODE = True
RESET_WEEKLY = True

# Google Drive
USE_GOOGLE_DRIVE = True
DRIVE_FOLDER_NAME = 'Instagram AI Videos'
```

### Optimal Posting Times

```python
OPTIMAL_POSTING_TIMES = [
    "09:00",  # 9 AM
    "12:00",  # 12 PM
    "15:00",  # 3 PM
    "18:00",  # 6 PM
    "20:00",  # 8 PM
]
```

## 📁 Project Structure

```
instagram-ai-agent/
├── main.py                 # Main video generation script
├── cloud_automation.py     # Cloud automation and scheduling
├── cloud_deployment.py     # Cloud platform deployment scripts
├── config.py              # All configuration settings
├── setup_google_sheets.py  # Google Sheets setup helper
├── quick_setup.py         # Interactive setup guide
├── requirements.txt       # Python dependencies
├── requirements-cloud.txt # Cloud-specific dependencies
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose configuration
├── README.md            # This file
├── CLOUD_DEPLOYMENT_GUIDE.md # Cloud deployment guide
├── credentials.json     # Google API credentials (you provide)
├── progress.json        # Progress tracking (auto-generated)
├── music/              # Your music files folder
│   ├── song1.mp3
│   ├── song2.mp3
│   └── ...
├── logs/               # Automation logs (auto-generated)
└── instagram_video_*.mp4 # Generated videos (auto-generated)
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

**"Google Drive upload failed"**
- Check your Google One subscription
- Verify Drive API is enabled in Google Cloud Console
- Check internet connection

**"Cloud deployment issues"**
- Follow the platform-specific instructions in `CLOUD_DEPLOYMENT_GUIDE.md`
- Check logs for detailed error messages
- Verify all environment variables are set

### Logs

Check the logs for detailed information:
- Manual runs: `instagram_agent.log`
- Cloud automation: `logs/cloud_automation_YYYYMMDD.log`

## ⚠️ Important Notes

### Instagram Automation Warning

**⚠️ WARNING**: Automating Instagram posts is against Instagram's Terms of Service and can result in account suspension. This tool creates videos but does not include automatic posting functionality.

### Legal Considerations

- Ensure you have rights to use the music files
- Use royalty-free music or music you own
- Respect copyright laws for quotes and content

### Google One Storage

- Videos are uploaded to your Google Drive
- Uses your 2TB Google One storage
- Old videos are automatically cleaned up locally
- Keep videos in Drive for backup

## 🚀 Cloud Deployment Options

### 1. Google Cloud Platform (Recommended)
- Native Google integration
- Generous free tier
- Easy scaling
- Perfect for Google One users

### 2. AWS Lambda
- Serverless architecture
- Pay-per-use pricing
- Automatic scaling
- Good for infrequent posting

### 3. Heroku
- Easy deployment
- Good free tier
- Simple management
- Good for beginners

### 4. DigitalOcean
- Simple pricing
- Full control
- Good performance
- Cost-effective

### 5. Local Server/VPS
- Full control
- No cloud costs
- Requires 24/7 uptime
- Good for technical users

## 📈 Monitoring and Management

### Check Progress
```bash
python cloud_automation.py status
```

### View Generated Videos
- Check your Google Drive "Instagram AI Videos" folder
- Local videos are in the project directory

### Update Quotes Weekly
1. Edit your Google Sheet
2. Add new quotes
3. The system will automatically use them in sequence

### Monitor Logs
- Check `logs/` folder for detailed logs
- Monitor Google Cloud Console for API usage
- Set up alerts for failures

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this project!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [MoviePy](https://zulko.github.io/moviepy/) for video processing
- [gspread](https://gspread.readthedocs.io/) for Google Sheets integration
- [Google Cloud Platform](https://cloud.google.com/) for cloud services
- [Google Drive API](https://developers.google.com/drive) for storage

---

**Happy creating! 🎬✨** 