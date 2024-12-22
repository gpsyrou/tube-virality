from dotenv import load_dotenv
import os
import json
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Function to fetch trending videos
def get_trending_videos(api_key, region_code="GB"):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=10
    )
    response = request.execute()
    return response

def save_to_json(data, filename="trending_videos.json"):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Trending videos saved to {filename}")

def main():
    # Retrieve the API key from the environment variable
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")
        return

    region_code = "GB"
    trending_videos = get_trending_videos(api_key, region_code)
    save_to_json(trending_videos)

if __name__ == "__main__":
    main()
