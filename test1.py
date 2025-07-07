import requests
import time

ACCESS_TOKEN = "EAAIXWsXZA6JUBO7tA0jBl0koV1ixd7vrZAdLbh7OKZAsHoaVwPPrTHZA7lfCVLTPcR08kezSwFai01HF973LMCbmrJFyn4v7do8n4HXtFTyRok4T1HedhCZBhXBZCZCX1bZCNfrZBk9wddJcPFDjdfBhZA23irufxt0aH9vN42SfwZCz505Jg87x7k9fld4cjZAkhTnC"
IG_USER_ID = "17841468902818843"
VIDEO_URL = "https://drive.google.com/uc?id=1K4aMBIKnAzMHt2RnU5ldkXGxyNM-FP9Z&export=download"

CAPTION = "Test post with direct video URL!"

# Step 1: Create media container
media_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
params = {
    "media_type": "REELS",  # or "VIDEO" for a regular post
    "video_url": VIDEO_URL,
    "caption": CAPTION,
    "access_token": ACCESS_TOKEN
}
resp = requests.post(media_url, data=params)
print("Media container response:", resp.json())
creation_id = resp.json().get("id")

# Step 2: Poll for status and publish if ready
if creation_id:
    status_code = None
    for i in range(12):  # Try for up to 2 minutes (12 x 10s)
        status_url = f"https://graph.facebook.com/v18.0/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}"
        status_resp = requests.get(status_url)
        status_json = status_resp.json()
        status_code = status_json.get("status_code")
        print(f"Check {i+1}: status_code = {status_code}", status_json)
        if status_code == "FINISHED":
            break
        elif status_code == "ERROR":
            print("Instagram returned an error during processing:", status_json)
            break
        time.sleep(10)
    if status_code == "FINISHED":
        publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
        publish_params = {
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }
        publish_resp = requests.post(publish_url, data=publish_params)
        print("Publish response:", publish_resp.json())
    else:
        print("Media was not ready after waiting or an error occurred.")
else:
    print("Failed to create media container.")