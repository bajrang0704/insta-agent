"""
Cloud Automation Script for Instagram AI Agent
This script is designed to run on cloud platforms and can be scheduled to run automatically.
"""

import os
import sys
import logging
import schedule
import time
from datetime import datetime, timedelta
import json
from main import InstagramAIAgent
from config import *

# Setup cloud-specific logging
def setup_cloud_logging():
    """Setup logging for cloud environment."""
    log_dir = AUTOMATION_LOG_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"cloud_automation_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

class CloudAutomation:
    def __init__(self):
        self.agent = InstagramAIAgent()
        self.setup_scheduler()
    
    def setup_scheduler(self):
        """Setup the scheduler with optimal posting times."""
        # Schedule for each optimal posting time
        for time_str in OPTIMAL_POSTING_TIMES:
            schedule.every().day.at(time_str).do(self.create_and_upload_video)
            logging.info(f"Scheduled video creation for {time_str}")
        
        # Also schedule a backup time in case optimal times are missed
        schedule.every().day.at("21:00").do(self.create_and_upload_video)
        logging.info("Scheduled backup video creation for 21:00")
    
    def create_and_upload_video(self):
        """Create a video and upload it to Google Drive."""
        try:
            logging.info(f"🎬 Starting scheduled video creation at {datetime.now()}")
            
            # Create the video
            success = self.agent.create_video()
            
            if success:
                logging.info("✅ Scheduled video creation completed successfully!")
                
                # Clean up old local files if needed
                self.cleanup_old_files()
                
                return True
            else:
                logging.error("❌ Scheduled video creation failed!")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error in scheduled video creation: {e}")
            return False
    
    def cleanup_old_files(self):
        """Clean up old video files to save space."""
        try:
            # Keep only the latest videos
            video_files = [f for f in os.listdir('.') if f.startswith('instagram_video_') and f.endswith('.mp4')]
            video_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Remove old files (keep only the latest MAX_VIDEOS_TO_KEEP)
            for old_video in video_files[MAX_VIDEOS_TO_KEEP:]:
                os.remove(old_video)
                logging.info(f"Cleaned up old video: {old_video}")
        except Exception as e:
            logging.warning(f"Could not cleanup old files: {e}")
    
    def run_continuous(self):
        """Run the scheduler continuously."""
        logging.info("🚀 Starting cloud automation scheduler...")
        logging.info(f"📅 Scheduled times: {', '.join(OPTIMAL_POSTING_TIMES)}")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logging.info("🛑 Cloud automation stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Error in scheduler: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def run_once(self):
        """Run video creation once (useful for testing or manual triggers)."""
        logging.info("🎯 Running single video creation...")
        return self.create_and_upload_video()
    
    def get_status(self):
        """Get current status and next scheduled times."""
        status = {
            'current_time': datetime.now().isoformat(),
            'next_runs': [],
            'progress': self.agent.progress_data
        }
        
        # Get next scheduled runs
        for job in schedule.jobs:
            status['next_runs'].append({
                'time': str(job.next_run),
                'interval': str(job.interval)
            })
        
        return status

def main():
    """Main function for cloud automation."""
    setup_cloud_logging()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run":
            # Run once
            automation = CloudAutomation()
            success = automation.run_once()
            sys.exit(0 if success else 1)
            
        elif command == "start":
            # Start continuous scheduler
            automation = CloudAutomation()
            automation.run_continuous()
            
        elif command == "status":
            # Show status
            automation = CloudAutomation()
            status = automation.get_status()
            print(json.dumps(status, indent=2))
            
        elif command == "test":
            # Test the setup
            print("🧪 Testing cloud automation setup...")
            automation = CloudAutomation()
            print("✅ Setup test passed!")
            print("📋 Next scheduled runs:")
            for job in schedule.jobs:
                print(f"   - {job.next_run}")
                
        else:
            print("❌ Unknown command. Use: run, start, status, or test")
            sys.exit(1)
    else:
        # Default: run once
        automation = CloudAutomation()
        success = automation.run_once()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 