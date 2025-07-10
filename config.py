"""
Configuration file for Instagram AI Agent
Centralize all settings here for easy customization
"""

import os
from dotenv import load_dotenv

load_dotenv()
# --- FILE PATHS ---
MUSIC_FOLDER = 'music'
VIDEO_OUTPUT_PATH = 'output.mp4'
GOOGLE_CREDENTIALS_PATH = 'credentials.json'

# --- GOOGLE SHEETS CONFIG ---
SHEET_NAME = 'Instagram quotes'  # The name of your Google Sheet
SHEET_WORKSHEET_INDEX = 0       # 0 for the first sheet

# --- SEQUENTIAL PROCESSING ---
SEQUENTIAL_MODE = True  # Process quotes and music in order, not randomly
PROGRESS_FILE = 'progress.json'  # Track which quote/music pair to use next
RESET_WEEKLY = True  # Reset to first quote every week

# --- GOOGLE DRIVE INTEGRATION ---
USE_GOOGLE_DRIVE = True  # Store videos in Google Drive instead of local
DRIVE_FOLDER_NAME = 'Instagram AI Videos'  # Folder name in Google Drive
UPLOAD_TO_DRIVE = True  # Upload generated videos to Google Drive
DRIVE_MUSIC_FOLDER_ID = "1JWU8VSgShjnuER9Yq9-A_7KqRA0bDPPQ"

# --- INSTAGRAM API CONFIGURATION ---
# Meta Graph API credentials for Instagram posting
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")  # Set this in your environment or GitHub Secrets
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID")           # Set this in your environment or GitHub Secrets

# Instagram posting settings
ENABLE_INSTAGRAM_POSTING = True  # Set to True to enable auto-posting
POST_TO_INSTAGRAM = True  # Whether to post videos to Instagram after creation
POST_AS_REELS = True      # Post as Reels (True) or regular video (False)

# Caption settings
INCLUDE_QUOTE_IN_CAPTION = True   # Include the quote in the Instagram caption
INCLUDE_AUTHOR_IN_CAPTION = True  # Include the author in the Instagram caption
ADD_HASHTAGS = True               # Add relevant hashtags to captions
DEFAULT_HASHTAGS = [
    "#motivation", "#inspiration", "#quotes", "#dailyquote", 
    "#mindset", "#success", "#life", "#wisdom", "#positivevibes"
]

# --- VIDEO SETTINGS ---
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # For Instagram Reels/Stories
VIDEO_DURATION_SECONDS = 15  # Increased for better engagement
VIDEO_FPS = 30  # Higher FPS for smoother transitions

# --- TEXT STYLING ---
QUOTE_FONT_SIZE = 60  # Reduced from 80 for better fit
QUOTE_COLOR = 'white'
QUOTE_FONT = 'Arial-Bold'  # We'll try to use better fonts
QUOTE_MARGIN = 100  # Pixels from edge

AUTHOR_FONT_SIZE = 40  # Reduced from 50 for better proportion
AUTHOR_COLOR = 'white'  # Changed from gold to white for better visibility
AUTHOR_FONT = 'Arial'
AUTHOR_POSITION_Y = 0.75  # Percentage from top (0.75 = 75% down)

# --- TEXT EFFECTS ---
TEXT_FADE_IN_DURATION = 1.5  # seconds
TEXT_FADE_OUT_DURATION = 1.5  # seconds
TEXT_EFFECT_DURATION = 3.0  # Maximum effect duration
TEXT_STAGGER_DELAY = 0.8  # Delay between quote and author appearing

# --- AVAILABLE EFFECTS ---
AVAILABLE_EFFECTS = [
    'fade',           # Simple fade in and out
    'blur',           # Blur effect
    'diamond_blur'    # Diamond blur effect
]

# --- BACKGROUND SETTINGS ---
BACKGROUND_COLOR = (0, 0, 0)  # Black background (R, G, B)

# --- TRANSITIONS AND EFFECTS ---
FADE_IN_DURATION = 1.5  # seconds
FADE_OUT_DURATION = 1.5  # seconds
AUDIO_FADE_OUT_DURATION = 2.0  # seconds

# --- OPTIMAL POSTING TIMES ---
# Best times for Instagram engagement (in 24-hour format)
OPTIMAL_POSTING_TIMES = [
   
    "12:00",  # 12 PM
    "15:00",  # 3 PM
    "18:00",  # 6 PM
    "20:00",  # 8 PM
]

# --- AUTOMATION SETTINGS ---
MAX_VIDEOS_TO_KEEP = 10  # Number of recent videos to keep
AUTOMATION_LOG_DIR = 'logs'

# --- LOGGING ---
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# --- VALIDATION ---
def validate_config():
    """Validate that all required paths and settings are correct."""
    errors = []
    
    # Check if music folder exists
    if not os.path.exists(MUSIC_FOLDER):
        errors.append(f"Music folder '{MUSIC_FOLDER}' does not exist")
    
    # Check if credentials file exists
    if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        errors.append(f"Credentials file '{GOOGLE_CREDENTIALS_PATH}' does not exist")
    
    # Validate video dimensions
    if VIDEO_WIDTH <= 0 or VIDEO_HEIGHT <= 0:
        errors.append("Video dimensions must be positive numbers")
    
    # Validate duration
    if VIDEO_DURATION_SECONDS <= 0:
        errors.append("Video duration must be positive")
    
    # Validate font sizes
    if QUOTE_FONT_SIZE <= 0 or AUTHOR_FONT_SIZE <= 0:
        errors.append("Font sizes must be positive numbers")
    
    # Validate Instagram credentials if posting is enabled
    if ENABLE_INSTAGRAM_POSTING:
        if not INSTAGRAM_ACCESS_TOKEN:
            errors.append("Instagram access token is required when posting is enabled")
        if not INSTAGRAM_USER_ID:
            errors.append("Instagram user ID is required when posting is enabled")
    
    return errors

# --- PRESET CONFIGURATIONS ---
PRESETS = {
    'instagram_story': {
        'VIDEO_WIDTH': 1080,
        'VIDEO_HEIGHT': 1920,
        'VIDEO_DURATION_SECONDS': 15,
        'QUOTE_FONT_SIZE': 70,
        'AUTHOR_FONT_SIZE': 45,
    },
    'instagram_reel': {
        'VIDEO_WIDTH': 1080,
        'VIDEO_HEIGHT': 1920,
        'VIDEO_DURATION_SECONDS': 30,
        'QUOTE_FONT_SIZE': 80,
        'AUTHOR_FONT_SIZE': 50,
    },
    'youtube_short': {
        'VIDEO_WIDTH': 1080,
        'VIDEO_HEIGHT': 1920,
        'VIDEO_DURATION_SECONDS': 60,
        'QUOTE_FONT_SIZE': 90,
        'AUTHOR_FONT_SIZE': 55,
    },
    'tiktok': {
        'VIDEO_WIDTH': 1080,
        'VIDEO_HEIGHT': 1920,
        'VIDEO_DURATION_SECONDS': 15,
        'QUOTE_FONT_SIZE': 75,
        'AUTHOR_FONT_SIZE': 48,
    }
}

def apply_preset(preset_name):
    """Apply a preset configuration."""
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    preset = PRESETS[preset_name]
    for key, value in preset.items():
        if hasattr(__import__(__name__), key):
            globals()[key] = value
    
    print(f"Applied preset: {preset_name}") 