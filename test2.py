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
from googleapiclient.http import MediaFileUpload
import schedule
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from config import *
from instagram_api import InstagramAPI
import requests

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
                    logging.info(f"Loaded progress: Quote {data.get('quote_index', 0)}, Music {data.get('music_index', 0)}")
                    return data
            except Exception as e:
                logging.error(f"Error loading progress: {e}")
        
        # Initialize with first items
        return {'quote_index': 0, 'music_index': 0, 'last_reset': datetime.now().isoformat()}
    
    def save_progress(self):
        """Save current progress."""
        try:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
            logging.info(f"Saved progress: Quote {self.progress_data['quote_index']}, Music {self.progress_data['music_index']}")
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
        """Get the next music file in sequence."""
        try:
            music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
            if not music_files:
                logging.error("No .mp3 files found in the 'music' folder.")
                return None
            
            music_files.sort()  # Ensure consistent order
            music_index = self.progress_data['music_index']
            
            if music_index >= len(music_files):
                # Reset to beginning if we've used all music
                music_index = 0
                self.progress_data['music_index'] = 0
            
            selected_music = os.path.join(MUSIC_FOLDER, music_files[music_index])
            
            # Move to next music
            self.progress_data['music_index'] = (music_index + 1) % len(music_files)
            
            logging.info(f"Selected Music: {selected_music}")
            return selected_music
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
    
    def apply_fade_effect(self, base_clip, delay=0):
        """Apply fade in and out effect."""
        try:
            # Fade in
            fade_in = base_clip.fadein(TEXT_FADE_IN_DURATION)
            # Fade out
            fade_out = fade_in.fadeout(TEXT_FADE_OUT_DURATION)
            # Set delay
            return fade_out.set_start(delay)
        except Exception as e:
            logging.error(f"Error applying fade effect: {e}")
            return base_clip.set_start(delay)

    def apply_blur_effect(self, base_clip, delay=0):
        """Apply blur effect using PIL."""
        try:
            # Create a blurred version by scaling down and up
            blurred_clip = base_clip.resize(0.5).resize(2.0)
            blurred_clip = blurred_clip.set_opacity(0.7)
            
            # Combine blurred and original
            combined = CompositeVideoClip([blurred_clip, base_clip])
            
            # Add fade in/out
            fade_in = combined.fadein(TEXT_FADE_IN_DURATION)
            fade_out = fade_in.fadeout(TEXT_FADE_OUT_DURATION)
            
            return fade_out.set_start(delay)
        except Exception as e:
            logging.error(f"Error applying blur effect: {e}")
            return self.apply_fade_effect(base_clip, delay)

    def apply_diamond_blur_effect(self, base_clip, delay=0):
        """Apply diamond blur effect using multiple scaled versions."""
        try:
            # Create multiple scaled versions for diamond effect
            scale1 = base_clip.resize(0.3).set_opacity(0.4)
            scale2 = base_clip.resize(0.6).set_opacity(0.6)
            scale3 = base_clip.resize(0.8).set_opacity(0.8)
            
            # Combine all layers
            diamond_effect = CompositeVideoClip([scale1, scale2, scale3, base_clip])
            
            # Add fade in/out
            fade_in = diamond_effect.fadein(TEXT_FADE_IN_DURATION)
            fade_out = fade_in.fadeout(TEXT_FADE_OUT_DURATION)
            
            return fade_out.set_start(delay)
        except Exception as e:
            logging.error(f"Error applying diamond blur effect: {e}")
            return self.apply_fade_effect(base_clip, delay)

    def create_text_with_random_effect(self, text, font_size, color, position='center', max_width=None, delay=0):
        """Create text with randomly selected effect."""
        try:
            # Create base text image
            base_clip = self.create_text_image(text, font_size, color, position, max_width)
            if base_clip is None:
                return None
            
            # Randomly select an effect
            effect = random.choice(AVAILABLE_EFFECTS)
            logging.info(f"Applying effect: {effect}")
            
            # Apply the selected effect
            if effect == 'fade':
                return self.apply_fade_effect(base_clip, delay)
            elif effect == 'blur':
                return self.apply_blur_effect(base_clip, delay)
            elif effect == 'diamond_blur':
                return self.apply_diamond_blur_effect(base_clip, delay)
            else:
                return self.apply_fade_effect(base_clip, delay)
                
        except Exception as e:
            logging.error(f"Error creating text with random effect: {e}")
            return None

    def create_text_with_effects(self, text, font_size, color, position='center', max_width=None, delay=0):
        """Create text with fade-in, fade-out, and glow effects."""
        try:
            # Create base text image
            base_clip = self.create_text_image(text, font_size, color, position, max_width)
            if base_clip is None:
                return None
            
            # Add glow effect if enabled
            if TEXT_GLOW_EFFECT:
                # Create a larger, semi-transparent version for glow
                glow_clip = self.create_text_image(text, font_size + 4, color, position, max_width)
                if glow_clip:
                    glow_clip = glow_clip.set_opacity(0.3)  # Make it semi-transparent
                    # Combine glow and main text
                    base_clip = CompositeVideoClip([glow_clip, base_clip])
            
            # Add fade-in effect
            fade_in_clip = base_clip.fadein(TEXT_FADE_IN_DURATION)
            
            # Add fade-out effect
            fade_out_clip = fade_in_clip.fadeout(TEXT_FADE_OUT_DURATION)
            
            # Set the delay
            final_clip = fade_out_clip.set_start(delay)
            
            return final_clip
            
        except Exception as e:
            logging.error(f"Error creating text with effects: {e}")
            return None
    
    def create_text_image(self, text, font_size, color, position='center', max_width=None):
        """Create a text image using PIL and convert to MoviePy clip with proper text wrapping."""
        try:
            # Create a transparent image
            img = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Try to use better system fonts in order of preference
            font = None
            font_paths = [
                "C:/Windows/Fonts/calibri.ttf",  # Calibri - modern and clean
                "C:/Windows/Fonts/segoeui.ttf",  # Segoe UI - modern
                "C:/Windows/Fonts/arial.ttf",    # Arial - fallback
                "C:/Windows/Fonts/times.ttf",    # Times New Roman
                "arial.ttf"                      # Try without path
            ]
            
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    logging.info(f"Using font: {font_path}")
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
                logging.warning("Using default font")
            
            # Set max width for text wrapping - use more space
            if max_width is None:
                max_width = VIDEO_WIDTH - 200  # Leave 100px margin on each side
            
            # Function to wrap text
            def wrap_text(text, font, max_width):
                words = text.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    text_width = bbox[2] - bbox[0]
                    
                    if text_width <= max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            # If a single word is too long, break it
                            lines.append(word)
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                return lines
            
            # Wrap the text
            wrapped_lines = wrap_text(text, font, max_width)
            logging.info(f"Text wrapped into {len(wrapped_lines)} lines: {wrapped_lines}")
            
            # Calculate total height of all lines
            line_height = font_size + 15  # Add more spacing between lines
            total_height = len(wrapped_lines) * line_height
            
            # Calculate position - ensure text is fully visible
            if position == 'center':
                x = (VIDEO_WIDTH - max_width) // 2
                y = (VIDEO_HEIGHT - total_height) // 2
                # Ensure text doesn't go off screen
                y = max(50, min(y, VIDEO_HEIGHT - total_height - 50))
            else:
                x, y = position
            
            # Draw each line
            for i, line in enumerate(wrapped_lines):
                line_y = y + (i * line_height)
                
                # Center each line horizontally
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_x = (VIDEO_WIDTH - line_width) // 2
                
                # Ensure line doesn't go off screen
                line_x = max(50, min(line_x, VIDEO_WIDTH - line_width - 50))
                
                draw.text((line_x, line_y), line, fill=color, font=font)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Create MoviePy clip
            clip = ImageClip(img_array, duration=VIDEO_DURATION_SECONDS)
            return clip
            
        except Exception as e:
            logging.error(f"Error creating text image: {e}")
            return None
    
    def create_basic_video_test(self, music_file):
        """Create a basic video test without text to verify video creation works."""
        logging.info("Starting basic video test...")
        
        try:
            # Create background
            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=BACKGROUND_COLOR,
                duration=VIDEO_DURATION_SECONDS
            )
            
            # Load and process audio
            audio = AudioFileClip(music_file).set_duration(VIDEO_DURATION_SECONDS)
            
            # Combine elements
            final_video = CompositeVideoClip([background])
            final_video.audio = audio
            final_video.fps = VIDEO_FPS
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_video_{timestamp}.mp4"
            
            # Write video
            final_video.write_videofile(filename, codec='libx264', audio_codec='aac')
            logging.info(f"Basic video test created: {filename}")
            
            return filename
            
        except Exception as e:
            logging.error(f"Error creating basic video test: {e}")
            return None
    
    def create_video_with_pil_text(self, quote_text, author_text, music_file):
        """Create video with text rendered using PIL and random effects."""
        logging.info("Starting video creation with random effects...")
        
        try:
            # Create background
            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=BACKGROUND_COLOR,
                duration=VIDEO_DURATION_SECONDS
            )
            
            # Create quote text clip with random effect (appears first)
            quote_clip = self.create_text_with_random_effect(
                f'"{quote_text}"', 
                QUOTE_FONT_SIZE, 
                QUOTE_COLOR, 
                'center',
                VIDEO_WIDTH - 300,  # Leave more margin for quotes (150px each side)
                0  # No delay for quote
            )
            
            # Create author text clip with random effect (appears after delay)
            author_clip = self.create_text_with_random_effect(
                f"- {author_text}", 
                AUTHOR_FONT_SIZE, 
                AUTHOR_COLOR, 
                (0, int(VIDEO_HEIGHT * 0.75)),  # Position at 75% down instead of 80%
                VIDEO_WIDTH - 200,  # Leave more margin for author
                TEXT_STAGGER_DELAY  # Delay for author text
            )
            
            if quote_clip is None or author_clip is None:
                logging.error("Failed to create text clips")
                return None
            
            # Load and process audio
            audio = AudioFileClip(music_file).set_duration(VIDEO_DURATION_SECONDS)
            
            # Combine all elements
            final_video = CompositeVideoClip([background, quote_clip, author_clip])
            final_video.audio = audio
            final_video.fps = VIDEO_FPS
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_video_{timestamp}.mp4"
            
            # Write video
            final_video.write_videofile(filename, codec='libx264', audio_codec='aac')
            logging.info(f"Video with random effects created: {filename}")
            
            return filename
            
        except Exception as e:
            logging.error(f"Error creating video with random effects: {e}")
            return None
    
    def create_simple_video(self, quote_text, author_text, music_file):
        """Create a simple video without complex text effects."""
        logging.info("Starting simple video creation...")
        
        try:
            # Create background
            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=BACKGROUND_COLOR,
                duration=VIDEO_DURATION_SECONDS
            )
            
            # Create simple text clips
            quote_clip = TextClip(
                txt=f'"{quote_text}"',
                fontsize=QUOTE_FONT_SIZE,
                color=QUOTE_COLOR,
                font='Arial'
            ).set_position('center').set_duration(VIDEO_DURATION_SECONDS)
            
            author_clip = TextClip(
                txt=f"- {author_text}",
                fontsize=AUTHOR_FONT_SIZE,
                color=AUTHOR_COLOR,
                font='Arial'
            ).set_position(('center', VIDEO_HEIGHT * 0.8)).set_duration(VIDEO_DURATION_SECONDS)
            
            # Load and process audio
            audio = AudioFileClip(music_file).set_duration(VIDEO_DURATION_SECONDS)
            
            # Combine all elements
            final_video = CompositeVideoClip([background, quote_clip, author_clip])
            final_video.audio = audio
            final_video.fps = VIDEO_FPS
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_video_{timestamp}.mp4"
            
            # Write video
            final_video.write_videofile(filename, codec='libx264', audio_codec='aac')
            logging.info(f"Simple video created: {filename}")
            
            return filename
            
        except Exception as e:
            logging.error(f"Error creating simple video: {e}")
            return None
    
    def create_enhanced_video(self, quote_text, author_text, music_file):
        """Create video with enhanced transitions and effects."""
        logging.info("Starting enhanced video creation...")
        
        try:
            # Create background
            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=BACKGROUND_COLOR,
                duration=VIDEO_DURATION_SECONDS
            )
            
            # Create quote text with simple styling (no ImageMagick dependency)
            quote_clip = TextClip(
                txt=f'"{quote_text}"',
                fontsize=QUOTE_FONT_SIZE,
                color=QUOTE_COLOR,
                font=QUOTE_FONT,
                size=(VIDEO_WIDTH - QUOTE_MARGIN, None)
            ).set_position('center')
            
            # Create author text
            author_clip = TextClip(
                txt=f"- {author_text}",
                fontsize=AUTHOR_FONT_SIZE,
                color=AUTHOR_COLOR,
                font=AUTHOR_FONT
            ).set_position(('center', VIDEO_HEIGHT * AUTHOR_POSITION_Y))
            
            # Add enhanced transitions and effects
            quote_clip = self.add_text_effects(quote_clip, delay=0)
            author_clip = self.add_text_effects(author_clip, delay=TEXT_STAGGER_DELAY)
            
            # Load and process audio
            audio = AudioFileClip(music_file).set_duration(VIDEO_DURATION_SECONDS)
            audio = audio.audio_fadeout(AUDIO_FADE_OUT_DURATION)
            
            # Combine all elements
            final_video = CompositeVideoClip([background, quote_clip, author_clip])
            final_video.audio = audio
            final_video.fps = VIDEO_FPS
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_video_{timestamp}.mp4"
            
            # Write video
            final_video.write_videofile(filename, codec='libx264', audio_codec='aac')
            logging.info(f"Enhanced video created: {filename}")
            
            return filename
            
        except Exception as e:
            logging.error(f"Error creating enhanced video: {e}")
            return None
    
    def add_text_effects(self, text_clip, delay=0):
        """Add various text effects and animations."""
        duration = VIDEO_DURATION_SECONDS
        
        # Start time with delay
        start_time = delay
        end_time = duration - FADE_OUT_DURATION
        
        # Fade in effect
        fade_in = text_clip.crossfadein(FADE_IN_DURATION)
        
        # Fade out effect
        fade_out = text_clip.crossfadeout(FADE_OUT_DURATION)
        
        # Combine effects
        final_clip = fade_in.set_duration(duration)
        
        # Add floating animation if enabled
        if USE_FLOAT_EFFECT:
            def float_animation(t):
                # Gentle floating motion
                y_offset = 5 * np.sin(t * 2 * np.pi / 4)  # 4-second cycle
                return ('center', text_clip.position[1] + y_offset)
            
            final_clip = final_clip.set_position(float_animation)
        
        # Add zoom effect if enabled
        if USE_ZOOM_EFFECT:
            def zoom_animation(t):
                # Subtle zoom in and out
                scale = 1 + 0.05 * np.sin(t * 2 * np.pi / 6)  # 6-second cycle
                return scale
            
            final_clip = final_clip.resize(zoom_animation)
        
        return final_clip.set_duration(duration)
    
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
        
        # Create video with PIL-based text rendering
        logging.info("Creating video with text...")
        video_filename = self.create_video_with_pil_text(quote, author, music_file)
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