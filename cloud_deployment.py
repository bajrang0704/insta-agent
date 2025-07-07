"""
Cloud Deployment Script for Instagram AI Agent
This script helps deploy the system to various cloud platforms.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class CloudDeployment:
    def __init__(self):
        self.platforms = {
            'google_cloud': self.setup_google_cloud,
            'aws_lambda': self.setup_aws_lambda,
            'heroku': self.setup_heroku,
            'digitalocean': self.setup_digitalocean,
            'local_server': self.setup_local_server
        }
    
    def create_requirements_cloud(self):
        """Create cloud-specific requirements file."""
        cloud_requirements = [
            'moviepy==1.0.3',
            'google-api-python-client==2.108.0',
            'google-auth-httplib2==0.1.1',
            'google-auth-oauthlib==1.1.0',
            'pandas==2.1.4',
            'gspread==5.12.0',
            'Pillow==10.1.0',
            'numpy==1.24.3',
            'google-auth==2.23.4',
            'PyDrive2==1.17.0',
            'schedule==1.2.0',
            'python-dateutil==2.8.2',
            'gunicorn==21.2.0',  # For web servers
            'flask==3.0.0',      # For web interface
        ]
        
        with open('requirements-cloud.txt', 'w') as f:
            f.write('\n'.join(cloud_requirements))
        
        print("✅ Created requirements-cloud.txt")
    
    def create_dockerfile(self):
        """Create Dockerfile for containerized deployment."""
        dockerfile_content = """# Instagram AI Agent Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-cloud.txt .
RUN pip install --no-cache-dir -r requirements-cloud.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p music logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the cloud automation
CMD ["python", "cloud_automation.py", "start"]
"""
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        
        print("✅ Created Dockerfile")
    
    def create_docker_compose(self):
        """Create docker-compose.yml for easy deployment."""
        compose_content = """version: '3.8'

services:
  instagram-ai-agent:
    build: .
    container_name: instagram-ai-agent
    restart: unless-stopped
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./music:/app/music:ro
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    command: python cloud_automation.py start
"""
        
        with open('docker-compose.yml', 'w') as f:
            f.write(compose_content)
        
        print("✅ Created docker-compose.yml")
    
    def create_google_cloud_config(self):
        """Create Google Cloud configuration files."""
        # app.yaml for Google App Engine
        app_yaml = """runtime: python39
service: instagram-ai-agent

env_variables:
  PYTHONPATH: /app

automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10
"""
        
        with open('app.yaml', 'w') as f:
            f.write(app_yaml)
        
        # cloudbuild.yaml for automated deployment
        cloudbuild_yaml = """steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/instagram-ai-agent', '.']

- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/instagram-ai-agent']

- name: 'gcr.io/cloud-builders/gcloud'
  args:
  - 'run'
  - 'deploy'
  - 'instagram-ai-agent'
  - '--image'
  - 'gcr.io/$PROJECT_ID/instagram-ai-agent'
  - '--region'
  - 'us-central1'
  - '--platform'
  - 'managed'
  - '--allow-unauthenticated'
"""
        
        with open('cloudbuild.yaml', 'w') as f:
            f.write(cloudbuild_yaml)
        
        print("✅ Created Google Cloud configuration files")
    
    def create_aws_lambda_config(self):
        """Create AWS Lambda configuration."""
        # serverless.yml for AWS Lambda
        serverless_yml = """service: instagram-ai-agent

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  memorySize: 1024
  timeout: 300

functions:
  createVideo:
    handler: lambda_handler.handler
    events:
      - schedule: cron(0 9,12,15,18,20 * * ? *)  # Optimal posting times
    environment:
      GOOGLE_CREDENTIALS: ${ssm:/instagram-ai-agent/credentials}
"""
        
        with open('serverless.yml', 'w') as f:
            f.write(serverless_yml)
        
        # lambda_handler.py
        lambda_handler = """import json
import os
from main import InstagramAIAgent

def handler(event, context):
    try:
        agent = InstagramAIAgent()
        success = agent.create_video()
        
        return {
            'statusCode': 200 if success else 500,
            'body': json.dumps({
                'success': success,
                'message': 'Video created successfully' if success else 'Video creation failed'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
"""
        
        with open('lambda_handler.py', 'w') as f:
            f.write(lambda_handler)
        
        print("✅ Created AWS Lambda configuration files")
    
    def create_heroku_config(self):
        """Create Heroku configuration files."""
        # Procfile for Heroku
        procfile = "worker: python cloud_automation.py start"
        
        with open('Procfile', 'w') as f:
            f.write(procfile)
        
        # runtime.txt
        runtime_txt = "python-3.9.18"
        
        with open('runtime.txt', 'w') as f:
            f.write(runtime_txt)
        
        print("✅ Created Heroku configuration files")
    
    def setup_google_cloud(self):
        """Setup for Google Cloud Platform."""
        print("🚀 Setting up Google Cloud deployment...")
        
        self.create_requirements_cloud()
        self.create_dockerfile()
        self.create_google_cloud_config()
        
        print("\n📋 Google Cloud Setup Instructions:")
        print("1. Install Google Cloud SDK")
        print("2. Run: gcloud auth login")
        print("3. Run: gcloud config set project YOUR_PROJECT_ID")
        print("4. Run: gcloud app deploy")
        print("\nOr use Docker:")
        print("1. Run: docker build -t instagram-ai-agent .")
        print("2. Run: docker run -d --restart unless-stopped instagram-ai-agent")
    
    def setup_aws_lambda(self):
        """Setup for AWS Lambda."""
        print("🚀 Setting up AWS Lambda deployment...")
        
        self.create_requirements_cloud()
        self.create_aws_lambda_config()
        
        print("\n📋 AWS Lambda Setup Instructions:")
        print("1. Install Serverless Framework: npm install -g serverless")
        print("2. Configure AWS credentials")
        print("3. Store Google credentials in AWS SSM:")
        print("   aws ssm put-parameter --name /instagram-ai-agent/credentials --value '$(cat credentials.json)' --type SecureString")
        print("4. Deploy: serverless deploy")
    
    def setup_heroku(self):
        """Setup for Heroku."""
        print("🚀 Setting up Heroku deployment...")
        
        self.create_requirements_cloud()
        self.create_heroku_config()
        
        print("\n📋 Heroku Setup Instructions:")
        print("1. Install Heroku CLI")
        print("2. Run: heroku login")
        print("3. Run: heroku create your-app-name")
        print("4. Set environment variables:")
        print("   heroku config:set GOOGLE_CREDENTIALS='$(cat credentials.json)'")
        print("5. Deploy: git push heroku main")
        print("6. Scale: heroku ps:scale worker=1")
    
    def setup_digitalocean(self):
        """Setup for DigitalOcean."""
        print("🚀 Setting up DigitalOcean deployment...")
        
        self.create_requirements_cloud()
        self.create_dockerfile()
        self.create_docker_compose()
        
        print("\n📋 DigitalOcean Setup Instructions:")
        print("1. Create a DigitalOcean Droplet")
        print("2. Install Docker: curl -fsSL https://get.docker.com | sh")
        print("3. Install Docker Compose")
        print("4. Upload your project files")
        print("5. Run: docker-compose up -d")
    
    def setup_local_server(self):
        """Setup for local server/VPS."""
        print("🚀 Setting up local server deployment...")
        
        self.create_requirements_cloud()
        self.create_dockerfile()
        self.create_docker_compose()
        
        print("\n📋 Local Server Setup Instructions:")
        print("1. Install Docker and Docker Compose")
        print("2. Place your credentials.json and music files")
        print("3. Run: docker-compose up -d")
        print("4. Check logs: docker-compose logs -f")
    
    def create_deployment_guide(self):
        """Create a comprehensive deployment guide."""
        guide_content = """# 🚀 Cloud Deployment Guide - Instagram AI Agent

## Overview
This guide helps you deploy your Instagram AI Agent to various cloud platforms for 24/7 automated video creation.

## Prerequisites
- Google Cloud project with API credentials
- Google Sheets with quotes
- Music files in the music/ folder
- Cloud platform account (Google Cloud, AWS, Heroku, etc.)

## Platform Options

### 1. Google Cloud Platform (Recommended)
**Pros:** Native Google integration, generous free tier
**Cons:** Requires some technical knowledge

**Setup:**
```bash
python cloud_deployment.py google_cloud
```

### 2. AWS Lambda
**Pros:** Serverless, pay-per-use, highly scalable
**Cons:** Cold starts, 15-minute timeout limit

**Setup:**
```bash
python cloud_deployment.py aws_lambda
```

### 3. Heroku
**Pros:** Easy deployment, good free tier
**Cons:** Sleeps after 30 minutes of inactivity

**Setup:**
```bash
python cloud_deployment.py heroku
```

### 4. DigitalOcean
**Pros:** Simple pricing, full control
**Cons:** Requires server management

**Setup:**
```bash
python cloud_deployment.py digitalocean
```

### 5. Local Server/VPS
**Pros:** Full control, no cloud costs
**Cons:** Requires 24/7 server uptime

**Setup:**
```bash
python cloud_deployment.py local_server
```

## Configuration

### Environment Variables
Set these in your cloud platform:
- `GOOGLE_CREDENTIALS`: Your Google API credentials JSON
- `PYTHONPATH`: /app (for Docker deployments)

### File Structure
```
instagram-ai-agent/
├── main.py
├── cloud_automation.py
├── config.py
├── credentials.json
├── music/
├── requirements-cloud.txt
└── [platform-specific files]
```

## Monitoring

### Check Status
```bash
python cloud_automation.py status
```

### View Logs
- Google Cloud: `gcloud app logs tail`
- AWS Lambda: CloudWatch Logs
- Heroku: `heroku logs --tail`
- Docker: `docker-compose logs -f`

## Troubleshooting

### Common Issues
1. **Credentials not found**: Ensure credentials.json is properly uploaded
2. **Music files missing**: Check music/ folder in deployment
3. **API quotas exceeded**: Monitor Google API usage
4. **Memory/timeout errors**: Increase resources for your platform

### Support
- Check logs for detailed error messages
- Verify all dependencies are installed
- Test locally before deploying

## Cost Optimization

### Google Cloud
- Use App Engine with automatic scaling
- Set minimum instances to 0 for cost savings

### AWS Lambda
- Perfect for infrequent video creation
- Pay only for execution time

### Heroku
- Use free tier for testing
- Upgrade to paid dyno for 24/7 operation

## Security

### Best Practices
1. Never commit credentials.json to version control
2. Use environment variables for sensitive data
3. Enable API key restrictions in Google Cloud
4. Use IAM roles instead of access keys (AWS)

## Next Steps

1. Choose your preferred platform
2. Run the deployment script
3. Follow platform-specific instructions
4. Test the deployment
5. Monitor logs and performance
6. Scale as needed

---

**Happy deploying! 🚀✨**
"""
        
        with open('CLOUD_DEPLOYMENT_GUIDE.md', 'w') as f:
            f.write(guide_content)
        
        print("✅ Created CLOUD_DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment function."""
    if len(sys.argv) < 2:
        print("❌ Please specify a platform:")
        print("Available platforms:")
        for platform in ['google_cloud', 'aws_lambda', 'heroku', 'digitalocean', 'local_server']:
            print(f"  - {platform}")
        print("\nExample: python cloud_deployment.py google_cloud")
        sys.exit(1)
    
    platform = sys.argv[1]
    deployment = CloudDeployment()
    
    if platform in deployment.platforms:
        deployment.platforms[platform]()
        deployment.create_deployment_guide()
        print(f"\n🎉 {platform.replace('_', ' ').title()} deployment setup complete!")
    else:
        print(f"❌ Unknown platform: {platform}")
        print("Available platforms:", list(deployment.platforms.keys()))
        sys.exit(1)

if __name__ == "__main__":
    main() 