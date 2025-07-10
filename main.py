import os
import json
import random
import gspread
import gspread.exceptions
import pandas as pd
from moviepy.editor import *
from moviepy.config import change_settings
from datetime import datetime, timedelta
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import schedule
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from instagram_api import InstagramAPI
import requests
import io
from video_creator import VideoCreator


import os

# Write credentials.json
google_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if google_creds:
    with open("credentials.json", "w") as f:
        f.write(google_creds)

# Write instagram_credentials.json
insta_creds = os.environ.get("INSTAGRAM_CREDENTIALS_JSON")
if insta_creds:
    with open("instagram_credentials.json", "w") as f:
        f.write(insta_creds)

# Write .env
dotenv_content = os.environ.get("DOTENV_FILE")
if dotenv_content:
    with open(".env", "w") as f:
        f.write(dotenv_content)
        
# Configure MoviePy to use a different text rendering method
try:
    change_settings({"IMAGEMAGICK_BINARY": "magick"})
except:
    # If ImageMagick is not available, use PIL for text rendering
    pass

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler('instagram_agent.log'),
        logging.StreamHandler()
    ]
)

class InstagramAIAgent:
    def __init__(self):
        self.progress_data = self.load_progress()
        self.drive_service = None
        self.drive_folder_id = None
        self.instagram_api = None
        self.video_creator = VideoCreator()
        
        if USE_GOOGLE_DRIVE:
            self.setup_google_drive()
        
        if ENABLE_INSTAGRAM_POSTING:
            self.setup_instagram_api()
    
    def load_progress(self):
        """Load progress data to track which quote/music pair to use next."""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    data = json.load(f)
                    if 'effect_index' not in data:
                        data['effect_index'] = 0
                    logging.info(f"Loaded progress: Quote {data.get('quote_index', 0)}, Music {data.get('music_index', 0)}, Effect {data.get('effect_index', 0)}")
                    return data
            except Exception as e:
                logging.error(f"Error loading progress: {e}")
        
        # Initialize with first items
        return {'quote_index': 0, 'music_index': 0, 'last_reset': datetime.now().isoformat(), 'effect_index': 0}
    
    def save_progress(self):
        """Save current progress."""
        try:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
            logging.info(f"Saved progress: Quote {self.progress_data['quote_index']}, Music {self.progress_data['music_index']}, Effect {self.progress_data.get('effect_index', 0)}")
        except Exception as e:
            logging.error(f"Error saving progress: {e}")
    
    def setup_google_drive(self):
        """Setup Google Drive API for storing videos."""
        try:
            scopes = ['https://www.googleapis.com/auth/drive']
            credentials = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=scopes)
            self.drive_service = build('drive', 'v3', credentials=credentials)
            
            # Create or find the folder
            self.drive_folder_id = self.get_or_create_drive_folder()
            logging.info(f"Google Drive setup complete. Folder ID: {self.drive_folder_id}")
        except Exception as e:
            logging.error(f"Error setting up Google Drive: {e}")
            self.drive_service = None
    
    def setup_instagram_api(self):
        """Setup Instagram API for posting."""
        try:
            self.instagram_api = InstagramAPI(
                INSTAGRAM_ACCESS_TOKEN,
                INSTAGRAM_USER_ID,
                upload_to_drive=self.upload_to_drive,
                drive_service=self.drive_service
            )
            if self.instagram_api:
                logging.info("Instagram API setup complete")
            else:
                logging.warning("Instagram API setup failed - posting will be disabled")
        except Exception as e:
            logging.error(f"Error setting up Instagram API: {e}")
            self.instagram_api = None
    
    def get_or_create_drive_folder(self):
        """Get or create the Google Drive folder for videos."""
        try:
            # Search for existing folder
            query = f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.drive_service.files().list(q=query).execute()
            files = results.get('files', [])
            
            if files:
                return files[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': DRIVE_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.drive_service.files().create(body=folder_metadata, fields='id').execute()
            logging.info(f"Created Google Drive folder: {DRIVE_FOLDER_NAME}")
            return folder.get('id')
        except Exception as e:
            logging.error(f"Error creating Drive folder: {e}")
            return None
    
    def upload_to_drive(self, file_path, filename):
        """Upload video to Google Drive."""
        if not self.drive_service or not self.drive_folder_id:
            print("[Drive] Google Drive not available, skipping upload")
            logging.warning("Google Drive not available, skipping upload")
            return None
        
        try:
            print(f"[Drive] Uploading '{filename}' to Google Drive...")
            file_metadata = {
                'name': filename,
                'parents': [self.drive_folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"[Drive] Upload complete! File ID: {file.get('id')}")
            logging.info(f"Uploaded to Google Drive: {filename} (ID: {file.get('id')})")
            return file.get('id')
        except Exception as e:
            print(f"[Drive] Error uploading to Drive: {e}")
            logging.error(f"Error uploading to Drive: {e}")
            return None
    
    def check_weekly_reset(self):
        """Check if we should reset to the first quote (weekly)."""
        if not RESET_WEEKLY:
            return False
        
        last_reset = datetime.fromisoformat(self.progress_data.get('last_reset', datetime.now().isoformat()))
        days_since_reset = (datetime.now() - last_reset).days
        
        if days_since_reset >= 7:
            self.progress_data['quote_index'] = 0
            self.progress_data['music_index'] = 0
            self.progress_data['last_reset'] = datetime.now().isoformat()
            self.save_progress()
            logging.info("Weekly reset: Starting from first quote and music")
            return True
        
        return False
    
    def list_available_sheets(self):
        """List all available Google Sheets to help debug sheet access."""
        try:
            gc = gspread.service_account(filename=GOOGLE_CREDENTIALS_PATH)
            all_sheets = gc.openall()
            
            if not all_sheets:
                logging.info("No Google Sheets found. Please check:")
                logging.info("1. Your service account has access to any sheets")
                logging.info("2. Sheets are shared with your service account email")
                return
            
            logging.info("Available Google Sheets:")
            for sheet in all_sheets:
                logging.info(f"- '{sheet.title}' (ID: {sheet.id})")
                
        except Exception as e:
            logging.error(f"Error listing sheets: {e}")
    
    def get_quotes_from_sheet(self):
        """Fetch quotes from Google Sheets."""
        try:
            gc = gspread.service_account(filename=GOOGLE_CREDENTIALS_PATH)
            worksheet = gc.open(SHEET_NAME).get_worksheet(SHEET_WORKSHEET_INDEX)
            records = worksheet.get_all_records()
            df = pd.DataFrame(records)
            
            # Check if we have the required columns
            required_columns = ['Quote', 'Author']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logging.error(f"Missing required columns in Google Sheet: {missing_columns}")
                logging.info(f"Available columns: {list(df.columns)}")
                logging.info("Please ensure your Google Sheet has columns named 'Quote' and 'Author'")
                return None
            
            if df.empty:
                logging.error("Google Sheet is empty. Please add some quotes.")
                return None
            
            logging.info(f"Successfully fetched {len(df)} quotes from Google Sheets.")
            logging.info(f"Columns found: {list(df.columns)}")
            return df
            
        except gspread.exceptions.APIError as e:
            logging.error(f"Google Sheets API Error: {e}")
            return None
        except gspread.exceptions.SpreadsheetNotFound:
            logging.error(f"Google Sheet '{SHEET_NAME}' not found. Please check the sheet name.")
            return None
        except gspread.exceptions.WorksheetNotFound:
            logging.error(f"Worksheet not found in '{SHEET_NAME}'. Please check the worksheet index.")
            return None
        except FileNotFoundError:
            logging.error(f"Credentials file '{GOOGLE_CREDENTIALS_PATH}' not found.")
            return None
        except Exception as e:
            logging.error(f"Error connecting to Google Sheets: {e}")
            logging.info("Please check:")
            logging.info("1. Your credentials.json file exists and is valid")
            logging.info("2. The Google Sheet name is correct")
            logging.info("3. The sheet is shared with your service account email")
            return None
    
    def get_sequential_quote(self, quotes_df):
        """Get the next quote in sequence."""
        if quotes_df is None or quotes_df.empty:
            return None, None
        
        quote_index = self.progress_data['quote_index']
        if quote_index >= len(quotes_df):
            # Reset to beginning if we've used all quotes
            quote_index = 0
            self.progress_data['quote_index'] = 0
        
        quote_row = quotes_df.iloc[quote_index]
        quote = quote_row['Quote']
        author = quote_row['Author']
        
        # Move to next quote
        self.progress_data['quote_index'] = (quote_index + 1) % len(quotes_df)
        
        return quote, author
    
    def get_sequential_music(self):
        """Get the next music file from Google Drive."""
        try:
            music_files = self.list_drive_music_files()
            if not music_files:
                logging.error("No .mp3 files found in the Drive music folder.")
                return None

            music_files.sort(key=lambda x: x['name'])  # Consistent order
            music_index = self.progress_data['music_index']

            if music_index >= len(music_files):
                music_index = 0
                self.progress_data['music_index'] = 0

            selected_file = music_files[music_index]
            temp_path = f"temp_{selected_file['name']}"
            self.download_drive_file(selected_file['id'], temp_path)

            # Move to next music
            self.progress_data['music_index'] = (music_index + 1) % len(music_files)

            logging.info(f"Selected Music: {temp_path}")
            return temp_path
        except Exception as e:
            logging.error(f"Error selecting music: {e}")
            return None
    
    def create_instagram_caption(self, quote, author):
        """Create Instagram caption with quote, author, and hashtags."""
        caption_parts = []
        
        if INCLUDE_QUOTE_IN_CAPTION:
            caption_parts.append(f'"{quote}"')
        
        if INCLUDE_AUTHOR_IN_CAPTION:
            caption_parts.append(f"- {author}")
        
        caption = "\n\n".join(caption_parts)
        
        if ADD_HASHTAGS:
            hashtags = " ".join(DEFAULT_HASHTAGS)
            caption += f"\n\n{hashtags}"
        
        return caption
    
    def post_to_instagram(self, video_path, quote, author):
        """Post video to Instagram."""
        if not self.instagram_api or not POST_TO_INSTAGRAM:
            print("[Instagram] Posting disabled or API not available.")
            logging.info("Instagram posting disabled or API not available")
            return False
        
        try:
            caption = self.create_instagram_caption(quote, author)
            print("[Instagram] Preparing to post to Instagram...")
            logging.info("Posting to Instagram with caption: ...")
            
            file_id = self.upload_to_drive(video_path, os.path.basename(video_path))
            if not file_id:
                print("[Drive] Failed to upload video to Google Drive.")
                logging.error("Failed to upload video to Google Drive")
                return False

            print("[Drive] Making file public...")
            # Make file public and get the link
            if not self.instagram_api.set_drive_file_public(file_id):
                print("[Drive] Failed to set Drive file public.")
                logging.error("Failed to set Drive file public")
                return False

            public_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            print(f"[Drive] Public video URL: {public_url}")
            logging.info(f"Public video URL: {public_url}")

            print("[Instagram] Posting video to Instagram...")
            # Post to Instagram using the public URL
            success = self.instagram_api.post_video(public_url, caption)
            
            if success:
                print("[Instagram] 🎉 Successfully posted to Instagram!")
                logging.info("Successfully posted to Instagram!")
                return True
            else:
                print("[Instagram] ❌ Failed to post to Instagram.")
                logging.error("Failed to post to Instagram")
                return False
                
        except Exception as e:
            print(f"[Instagram] ❌ Error posting to Instagram: {e}")
            logging.error(f"Error posting to Instagram: {e}")
            return False
    
    def get_optimal_posting_time(self):
        """Get the next optimal posting time."""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        for time_str in OPTIMAL_POSTING_TIMES:
            hour, minute = map(int, time_str.split(':'))
            if hour > current_hour or (hour == current_hour and minute > current_minute):
                return hour, minute
        
        # If all times have passed today, return first time tomorrow
        return int(OPTIMAL_POSTING_TIMES[0].split(':')[0]), int(OPTIMAL_POSTING_TIMES[0].split(':')[1])
    
    def create_video(self):
        """Main function to create a video."""
        logging.info("Starting Instagram AI Agent...")
        
        # Check weekly reset
        self.check_weekly_reset()
        
        # Get quotes
        quotes_df = self.get_quotes_from_sheet()
        if quotes_df is None or quotes_df.empty:
            logging.error("Could not fetch quotes. Exiting.")
            return False
        
        # Get sequential quote and music
        quote, author = self.get_sequential_quote(quotes_df)
        if not quote or not author:
            logging.error("Could not get quote. Exiting.")
            return False
        
        music_file = self.get_sequential_music()
        if not music_file:
            logging.error("Could not get music file. Exiting.")
            return False
        
        logging.info(f"Selected Quote: '{quote}' by {author}")
        
        # --- Effect cycling logic ---
        from config import AVAILABLE_EFFECTS
        effect_index = self.progress_data.get('effect_index', 0)
        effect = AVAILABLE_EFFECTS[effect_index % len(AVAILABLE_EFFECTS)]
        self.progress_data['effect_index'] = (effect_index + 1) % len(AVAILABLE_EFFECTS)
        # --- Video creation with keyframe logic ---
        logging.info(f"Creating video with effect: {effect}")
        video_filename = self.video_creator.create_video_with_pil_text_and_blur_keyframe(
            quote, author, music_file, effect
        )
        if not video_filename:
            logging.error("Video creation failed.")
            return False
        
        logging.info(f"Video created successfully: {video_filename}")
        logging.info(f"Quote: '{quote}' by {author}")
        
        # Upload to Google Drive if enabled
        drive_id = None
        public_url = None
        if UPLOAD_TO_DRIVE and USE_GOOGLE_DRIVE:
            drive_id = self.upload_to_drive(video_filename, video_filename)
            if drive_id:
                logging.info(f"Video uploaded to Google Drive with ID: {drive_id}")
                # Make file public and get the link
                self.instagram_api.set_drive_file_public(drive_id)
                public_url = f"https://drive.google.com/uc?id={drive_id}&export=download"
                print("Public video URL:", public_url)
        
        # Use test1.py style Instagram posting with the generated public_url
        if public_url:
            IG_USER_ID = INSTAGRAM_USER_ID
            ACCESS_TOKEN = INSTAGRAM_ACCESS_TOKEN
            VIDEO_URL = public_url
            CAPTION = self.create_instagram_caption(quote, author)
            # 1. Create media container
            media_container_url = f'https://graph.facebook.com/v19.0/{IG_USER_ID}/media'
            media_container_payload = {
                'media_type': 'REELS',
                'video_url': VIDEO_URL,
                'caption': CAPTION,
                'access_token': ACCESS_TOKEN
            }
            media_container_resp = requests.post(media_container_url, data=media_container_payload)
            print('Media container response:', media_container_resp.json())
            container_id = media_container_resp.json().get('id')
            print('Container ID:', container_id)
            # 2. Poll for status
            status_url = f'https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={ACCESS_TOKEN}'
            while True:
                status_resp = requests.get(status_url)
                status = status_resp.json().get('status_code')
                print('Status:', status)
                if status == 'FINISHED':
                    break
                elif status == 'ERROR':
                    print('Error:', status_resp.json())
                    return False
                time.sleep(5)
            # 3. Publish media
            publish_url = f'https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish'
            publish_payload = {
                'creation_id': container_id,
                'access_token': ACCESS_TOKEN
            }
            publish_resp = requests.post(publish_url, data=publish_payload)
            print('Publish response:', publish_resp.json())
        
        # Save progress
        self.save_progress()
        
        # Clean up the downloaded temp music file
        if music_file and music_file.startswith("temp_") and os.path.exists(music_file):
            os.remove(music_file)
            logging.info(f"Deleted temporary music file: {music_file}")
        
        return True

    def post_video_direct_url(self, public_url, caption):
        # Step 1: Create media container
        media_url = f"https://graph.facebook.com/v18.0/{self.ig_user_id}/media"
        params = {
            "media_type": "REELS",
            "video_url": public_url,
            "caption": caption,
            "access_token": self.access_token
        }
        resp = requests.post(media_url, data=params)
        creation_id = resp.json().get("id")
        if not creation_id:
            logging.error(f"Failed to create media container: {resp.json()}")
            return False

        # Step 2: Poll for status
        for i in range(12):
            status_url = f"https://graph.facebook.com/v18.0/{creation_id}?fields=status_code&access_token={self.access_token}"
            status_resp = requests.get(status_url)
            status_code = status_resp.json().get("status_code")
            if status_code == "FINISHED":
                break
            elif status_code == "ERROR":
                logging.error(f"Instagram processing error: {status_resp.json()}")
                return False
            time.sleep(10)
        if status_code == "FINISHED":
            publish_url = f"https://graph.facebook.com/v18.0/{self.ig_user_id}/media_publish"
            params = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            publish_resp = requests.post(publish_url, data=params)
            logging.info(f"Publish response: {publish_resp.json()}")
            return True
        else:
            logging.error("Media was not ready after waiting.")
            return False

    def list_drive_music_files(self):
        """List all .mp3 files in the Google Drive music folder."""
        try:
            query = f"'{DRIVE_MUSIC_FOLDER_ID}' in parents and mimeType='audio/mpeg' and trashed=false"
            results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
            return results.get('files', [])
        except Exception as e:
            logging.error(f"Error listing music files in Drive: {e}")
            return []

    def download_drive_file(self, file_id, destination_path):
        """Download a file from Google Drive to a local path."""
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            logging.info(f"Downloaded file {file_id} to {destination_path}")
            return destination_path
        except Exception as e:
            logging.error(f"Error downloading file from Drive: {e}")
            return None

def main():
    """Main execution function."""
    agent = InstagramAIAgent()
    
    # First, let's see what sheets are available
    logging.info("Checking available Google Sheets...")
    agent.list_available_sheets()
    
    # Then try to create the video
    return agent.create_video()

if __name__ == "__main__":
    main() 