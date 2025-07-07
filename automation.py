"""
Automation Script for Instagram AI Agent
This script can be scheduled to run automatically using Task Scheduler (Windows) or cron (Linux/Mac).
"""

import os
import sys
import logging
from datetime import datetime
import subprocess
import time

# Import the main functions
from main import main as create_video

def setup_logging():
    """Setup logging for automation."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"automation_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def check_prerequisites():
    """Check if all prerequisites are met."""
    logging.info("Checking prerequisites...")
    
    # Check if music folder exists and has files
    if not os.path.exists('music'):
        logging.error("Music folder not found!")
        return False
    
    music_files = [f for f in os.listdir('music') if f.endswith('.mp3')]
    if not music_files:
        logging.error("No .mp3 files found in music folder!")
        return False
    
    # Check if credentials exist
    if not os.path.exists('credentials.json'):
        logging.error("credentials.json not found!")
        return False
    
    logging.info(f"✅ Prerequisites check passed. Found {len(music_files)} music files.")
    return True

def cleanup_old_videos():
    """Clean up old video files to save space."""
    try:
        # Keep only the latest 5 videos
        video_files = [f for f in os.listdir('.') if f.startswith('output') and f.endswith('.mp4')]
        video_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        for old_video in video_files[5:]:  # Keep only the 5 most recent
            os.remove(old_video)
            logging.info(f"Cleaned up old video: {old_video}")
    except Exception as e:
        logging.warning(f"Could not cleanup old videos: {e}")

def run_automation():
    """Main automation function."""
    setup_logging()
    
    logging.info("🤖 Starting Instagram AI Agent Automation")
    logging.info(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            logging.error("❌ Prerequisites check failed. Exiting.")
            return False
        
        # Create video
        logging.info("🎬 Creating video...")
        success = create_video()
        
        if success:
            logging.info("✅ Video created successfully!")
            
            # Cleanup old videos
            cleanup_old_videos()
            
            # Here you could add Instagram posting logic
            # (Note: This would require additional setup and is against Instagram's ToS)
            
            logging.info("🎉 Automation completed successfully!")
            return True
        else:
            logging.error("❌ Video creation failed!")
            return False
            
    except Exception as e:
        logging.error(f"❌ Automation failed with error: {e}")
        return False

def create_windows_task():
    """Create a Windows Task Scheduler task."""
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    
    task_command = f'schtasks /create /tn "Instagram AI Agent" /tr "{python_path} {script_path}" /sc daily /st 10:00 /f'
    
    print("📋 To create a Windows scheduled task, run this command as Administrator:")
    print("=" * 80)
    print(task_command)
    print("=" * 80)
    print("\nThis will run the script daily at 10:00 AM.")
    print("You can modify the time by changing the /st parameter.")

def create_linux_cron():
    """Create a Linux/Mac cron job."""
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    
    cron_line = f"0 10 * * * {python_path} {script_path}"
    
    print("📋 To create a cron job, run:")
    print("=" * 80)
    print("crontab -e")
    print("=" * 80)
    print("Then add this line to run daily at 10:00 AM:")
    print("=" * 80)
    print(cron_line)
    print("=" * 80)

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        print("🔧 Automation Setup")
        print("=" * 50)
        
        if os.name == 'nt':  # Windows
            create_windows_task()
        else:  # Linux/Mac
            create_linux_cron()
        
        print("\n📝 Manual Setup Instructions:")
        print("1. Make sure all prerequisites are met")
        print("2. Test the script manually first: python automation.py")
        print("3. Set up the scheduled task/cron job")
        print("4. Monitor the logs in the 'logs' folder")
        
    else:
        # Run the automation
        success = run_automation()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 