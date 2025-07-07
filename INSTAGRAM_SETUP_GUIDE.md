# 📱 Complete Instagram Auto-Posting Setup Guide

This guide will walk you through setting up automatic Instagram posting using the Meta Graph API. This is the **legal and safe** way to automate Instagram posts.

## 🎯 What You'll Achieve

- ✅ **Fully Automated Instagram Posting** - Videos posted automatically at optimal times
- ✅ **Legal and Safe** - Uses Meta's official API
- ✅ **Business Account Required** - No personal account restrictions
- ✅ **Complete Integration** - Works with your existing video generation system

## 📋 Prerequisites Checklist

Before you start, ensure you have:

- [ ] **Instagram Business Account** (not personal)
- [ ] **Facebook Page** linked to your Instagram
- [ ] **Meta Developer Account** (free)
- [ ] **Meta App** with Instagram permissions
- [ ] **Long-lived Access Token** (expires in 60 days)

## 🚀 Step-by-Step Setup Process

### **Step 1: Convert to Instagram Business Account**

1. **Open Instagram app** on your phone
2. **Go to Settings** → **Account**
3. **Tap "Switch to Business Account"**
4. **Choose a category** (e.g., "Personal Blog", "Creator", "Business")
5. **Add business information** (optional)
6. **Complete the setup**

⚠️ **IMPORTANT**: Personal accounts cannot use the Instagram API!

### **Step 2: Create Facebook Page**

1. **Go to**: https://facebook.com/pages/create
2. **Choose "Business or Brand"**
3. **Fill in page details**:
   - Page Name: Your brand name
   - Category: Choose appropriate category
   - Description: Brief description
4. **Upload profile picture** (optional)
5. **Complete setup**

### **Step 3: Link Instagram to Facebook Page**

1. **Go to your Facebook Page**
2. **Click "Settings"** (left sidebar)
3. **Click "Linked Accounts"**
4. **Click "Connect Account"** next to Instagram
5. **Enter your Instagram credentials**
6. **Confirm the connection**

### **Step 4: Create Meta Developer Account**

1. **Go to**: https://developers.facebook.com
2. **Click "Get Started"** or **"Log In"**
3. **Complete verification**:
   - Add phone number
   - Verify email
   - Accept terms
4. **Complete developer account setup**

### **Step 5: Create Meta App**

1. **In Developer Console**, click **"Create App"**
2. **Choose "Business"** as app type
3. **Fill in app details**:
   - **App Name**: "Instagram AI Agent"
   - **App Contact Email**: Your email
   - **Business Account**: Your business account
4. **Click "Create App"**

### **Step 6: Add Instagram Permissions**

1. **In your app dashboard**, click **"Add Product"**
2. **Find and add "Instagram Basic Display"**
3. **Go to "Instagram Basic Display"** → **"Basic Display"**
4. **Add your Instagram account**:
   - Click **"Add Instagram Test Users"**
   - Enter your Instagram username
   - Accept invitation on Instagram
5. **Go to "Instagram Graph API"** → **"Getting Started"**
6. **Add these permissions**:
   - `instagram_basic`
   - `pages_show_list`
   - `instagram_content_publish`
   - `pages_read_engagement`

### **Step 7: Get Instagram User ID**

**Method 1: Using Graph API Explorer**
1. **Go to**: https://developers.facebook.com/tools/explorer/
2. **Select your app** from dropdown
3. **Add permissions**: `instagram_basic`, `pages_show_list`
4. **Click "Generate Access Token"**
5. **Make this request**: `GET /me/accounts`
6. **Find your page ID**, then make: `GET /{page-id}?fields=instagram_business_account`
7. **The 'id' field** is your Instagram User ID

**Method 2: Using Instagram Basic Display**
1. **Go to your app** → **Instagram Basic Display**
2. **Click "Basic Display"**
3. **Your Instagram User ID** is shown there

### **Step 8: Generate Long-Lived Access Token**

1. **Go to**: https://developers.facebook.com/tools/explorer/
2. **Select your app** from dropdown
3. **Add these permissions**:
   - `instagram_basic`
   - `pages_show_list`
   - `instagram_content_publish`
   - `pages_read_engagement`
4. **Click "Generate Access Token"**
5. **Copy the generated token**

⚠️ **IMPORTANT**: This token expires in 60 days! You'll need to regenerate it periodically.

## 🔧 Automated Setup

Instead of doing this manually, you can use our automated setup script:

```bash
python instagram_setup.py
```

This script will:
- ✅ Guide you through each step
- ✅ Open relevant websites automatically
- ✅ Test your connection
- ✅ Save your credentials securely
- ✅ Configure your system automatically

## 🧪 Testing Your Setup

After completing the setup, test your connection:

```bash
python main.py
```

You should see:
```
✅ Instagram API setup complete
✅ Connected successfully!
   Username: your_username
   Account Type: BUSINESS
```

## 📱 How Auto-Posting Works

Once configured, your system will:

1. **Create video** with quote and music
2. **Upload to Google Drive** (for public URL)
3. **Post to Instagram** using Meta API
4. **Add caption** with quote, author, and hashtags
5. **Schedule next post** at optimal time

### **API Flow Example**

```python
# 1. Upload video to container
POST https://graph.facebook.com/v18.0/{ig-user-id}/media
{
  "video_url": "https://drive.google.com/...",
  "caption": "Your quote here - Author\n\n#motivation #inspiration",
  "access_token": "your-token"
}

# 2. Publish the video
POST https://graph.facebook.com/v18.0/{ig-user-id}/media_publish
{
  "creation_id": "media-container-id",
  "access_token": "your-token"
}
```

## ⚙️ Configuration Options

In `config.py`, you can customize:

```python
# Instagram posting settings
ENABLE_INSTAGRAM_POSTING = True
POST_TO_INSTAGRAM = True
POST_AS_REELS = True  # Post as Reels or regular video

# Caption settings
INCLUDE_QUOTE_IN_CAPTION = True
INCLUDE_AUTHOR_IN_CAPTION = True
ADD_HASHTAGS = True

# Custom hashtags
DEFAULT_HASHTAGS = [
    "#motivation", "#inspiration", "#quotes", 
    "#dailyquote", "#mindset", "#success"
]
```

## 🔄 Token Renewal

Your access token expires every 60 days. To renew:

1. **Go to**: https://developers.facebook.com/tools/explorer/
2. **Select your app**
3. **Generate new token** with same permissions
4. **Update config.py** with new token
5. **Or run**: `python instagram_setup.py` again

## 🚨 Important Notes

### **Legal Compliance**
- ✅ **Fully Legal**: Uses Meta's official API
- ✅ **Safe**: No risk of account suspension
- ✅ **Compliant**: Follows Instagram's Terms of Service

### **Account Requirements**
- ❌ **Personal accounts** cannot use the API
- ✅ **Business/Creator accounts** are required
- ✅ **Facebook Page** must be linked

### **Rate Limits**
- **Posts per day**: Varies by account type
- **API calls**: Respect rate limits
- **Best practice**: Space out posts (our system does this automatically)

## 🎯 Optimal Posting Times

The system posts at these optimal times for maximum engagement:

- **9:00 AM** - Morning motivation
- **12:00 PM** - Lunch break browsing
- **3:00 PM** - Afternoon pick-me-up
- **6:00 PM** - Evening relaxation
- **8:00 PM** - Prime social media time

## 🔍 Troubleshooting

### **Common Issues**

**"Invalid access token"**
- Token may have expired
- Regenerate token in Graph API Explorer
- Check permissions are correct

**"Instagram account not found"**
- Ensure you're using Business account
- Check Instagram is linked to Facebook Page
- Verify Instagram User ID is correct

**"Permission denied"**
- Add missing permissions to your app
- Ensure Instagram account is added as test user
- Check app is in development mode

### **Getting Help**

1. **Check logs**: `instagram_agent.log`
2. **Test connection**: `python instagram_setup.py`
3. **Verify credentials**: Check `config.py`
4. **Monitor API usage**: Meta Developer Console

## 🎉 You're Ready!

Once setup is complete:

1. **Test locally**: `python main.py`
2. **Deploy to cloud**: `python cloud_deployment.py google_cloud`
3. **Start automation**: `python cloud_automation.py start`
4. **Monitor results**: Check your Instagram feed!

Your Instagram AI Agent will now:
- ✅ Create videos automatically
- ✅ Post at optimal times
- ✅ Use your quotes and music sequentially
- ✅ Store videos in Google Drive
- ✅ Track progress and reset weekly

---

**Happy posting! 🚀📱✨** 