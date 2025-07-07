"""
Instagram API Integration using Meta Graph API
Handles automatic posting to Instagram Business accounts
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import time

class InstagramAPI:
    def __init__(self, access_token: str, ig_user_id: str, upload_to_drive=None, drive_service=None):
        """
        Initialize Instagram API client
        Args:
            access_token: Long-lived access token from Meta Developer Console
            ig_user_id: Instagram Business Account ID
            upload_to_drive: Function to upload files to Google Drive
            drive_service: Google Drive service instance
        """
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.upload_to_drive = upload_to_drive
        self.drive_service = drive_service
        # Validate credentials
        if not self.validate_credentials():
            raise ValueError("Invalid Instagram API credentials")
    
    def validate_credentials(self) -> bool:
        """Validate the access token and Instagram user ID."""
        try:
            url = f"{self.base_url}/{self.ig_user_id}"
            params = {
                'fields': 'id,username',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                logging.error(f"Instagram API Error: {data['error']}")
                return False
            
            logging.info(f"✅ Instagram API validated for user: {data.get('username', 'Unknown')}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to validate Instagram credentials: {e}")
            return False
    
    def upload_video(self, video_path: str, caption: str = "") -> Optional[str]:
        # TEST MODE: Use a provided public video URL instead of uploading
        try:
            logging.info(f"[TEST] Using provided public video URL for upload: {video_path}")
            public_url = ""
            url = f"{self.base_url}/{self.ig_user_id}/media"
            data = {
                'video_url': public_url,
                'caption': caption,
                'access_token': self.access_token,
                'media_type': 'REELS'
            }
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            if 'error' in result:
                logging.error(f"Instagram API Error: {result['error']}")
                return None
            media_id = result.get('id')
            logging.info(f"Video uploaded successfully. Media ID: {media_id}")
            return media_id
        except Exception as e:
            logging.error(f"Failed to upload video: {e}")
            return None
    
    def publish_video(self, media_id: str) -> bool:
        """
        Publish the uploaded video to Instagram
        Args:
            media_id: Media container ID from upload_video
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"Publishing video with media ID: {media_id}")

            url = f"{self.base_url}/{self.ig_user_id}/media_publish"
            data = {
                'creation_id': media_id,
                'access_token': self.access_token
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()
            if 'error' in result:
                logging.error(f"Instagram API Error: {result['error']}")
                return False

            post_id = result.get('id')
            logging.info(f"Video published successfully! Post ID: {post_id}")
            return True

        except Exception as e:
            logging.error(f"Failed to publish video: {e}")
            return False
    
    def get_public_video_url(self, video_path: str) -> Optional[str]:
        if self.upload_to_drive is None:
            logging.error("upload_to_drive function not provided to InstagramAPI.")
            return None
        file_id = self.upload_to_drive(video_path, os.path.basename(video_path))
        if file_id:
            self.set_drive_file_public(file_id)
            return f"https://drive.google.com/uc?id={file_id}&export=download"
        else:
            logging.error("Failed to upload video to Google Drive")
            return None
    
    def get_google_drive_shareable_url(self, video_path: str) -> Optional[str]:
        """
        Get a shareable Google Drive URL for the video
        This requires the video to be uploaded to Google Drive first
        """
        try:
            # This is a simplified version - you'll need to implement based on your Google Drive setup
            # The video should already be uploaded to Google Drive by the main system
            
            # Extract filename from path
            filename = os.path.basename(video_path)
            
            # Search for the file in Google Drive
            query = f"name='{filename}' and trashed=false"
            results = self.drive_service.files().list(q=query).execute()
            files = results.get('files', [])
            
            if not files:
                logging.error(f"❌ Video file not found in Google Drive: {filename}")
                return None
            
            file_id = files[0]['id']
            
            # Make the file publicly accessible
            self.drive_service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
            
            # Get the shareable link
            shareable_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            logging.info(f"✅ Generated shareable URL: {shareable_url}")
            return shareable_url
            
        except Exception as e:
            logging.error(f"❌ Failed to get Google Drive shareable URL: {e}")
            return None
    
    def post_video(self, video_path: str, caption: str = "") -> bool:
        """
        Complete process: Upload and publish video to Instagram
        Args:
            video_path: Path to the video file
            caption: Caption for the post
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"Starting Instagram posting process for: {video_path}")

            # Step 1: Upload video (create media container)
            media_id = self.upload_video(video_path, caption)
            if not media_id:
                return False

            # Step 2: Poll for status
            status = "IN_PROGRESS"
            status_code = None
            for i in range(12):  # Try for up to 2 minutes (12 x 10s)
                status_url = f"{self.base_url}/{media_id}?fields=status_code&access_token={self.access_token}"
                status_resp = requests.get(status_url)
                status_code = status_resp.json().get("status_code")
                logging.info(f"Check {i+1}: status_code = {status_code}")
                if status_code == "FINISHED":
                    break
                elif status_code == "ERROR":
                    logging.error(f"Instagram processing error: {status_resp.json()}")
                    return False
                time.sleep(10)
            if status_code != "FINISHED":
                logging.error("Media was not ready after waiting.")
                return False

            # Step 3: Publish video
            success = self.publish_video(media_id)
            if success:
                logging.info("Instagram post completed successfully!")
                return True
            else:
                logging.error("Failed to publish video to Instagram")
                return False

        except Exception as e:
            logging.error(f"Instagram posting failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get Instagram account information."""
        try:
            url = f"{self.base_url}/{self.ig_user_id}"
            params = {
                'fields': 'id,username,account_type,followers_count,media_count',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logging.error(f"❌ Failed to get account info: {e}")
            return {}

    def set_drive_file_public(self, file_id):
        if self.drive_service is None:
            logging.error("drive_service not provided to InstagramAPI.")
            return False
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            logging.info(f"Set file {file_id} to public")
            return True
        except Exception as e:
            logging.error(f"Failed to set file public: {e}")
            return False

def create_instagram_api_from_config() -> Optional[InstagramAPI]:
    """
    Create Instagram API instance from configuration
    """
    try:
        # Load Instagram credentials from config
        from config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID
        
        if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_USER_ID:
            logging.warning("⚠️ Instagram credentials not configured")
            return None
        
        return InstagramAPI(INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID)
        
    except ImportError:
        logging.error("❌ Instagram configuration not found in config.py")
        return None
    except Exception as e:
        logging.error(f"❌ Failed to create Instagram API: {e}")
        return None 