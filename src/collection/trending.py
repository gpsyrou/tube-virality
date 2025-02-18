import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime
from typing import Any, Dict

load_dotenv()

class YouTubeTrending:
    def __init__(self, api_key: str, config_path: str, region_code: str = "GB"):
        self.api_key = api_key
        self.region_code = region_code
        self.config = self.load_config(config_path)
        self.metadata_loc = self.config.get("TRENDING_METADATA_LOC")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

        if not os.path.isdir(self.metadata_loc):
            os.makedirs(self.metadata_loc, exist_ok=True)

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads the configuration from a JSON file."""
        with open(config_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    def get_trending_videos(self) -> Dict[str, Any]:
        """Fetches trending videos from YouTube API."""
        request = self.youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=self.region_code,
            maxResults=30
        )
        response = request.execute()
        return response

    def save_to_json(self, data: Dict[str, Any], filename: str = "trending_videos.json") -> None:
        """Saves trending videos data to a JSON file."""
        date_str = datetime.now().strftime("_%Y%m%d")
        filename = os.path.splitext(filename)[0] + f"_{self.region_code}" + date_str + os.path.splitext(filename)[1]
        filename = os.path.join(self.metadata_loc, filename)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, mode="w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Trending videos saved to {filename}")


if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")
        exit(1)

    region_code = "GB"
    yt_trending = YouTubeTrending(api_key, CONFIG_PATH, region_code)
    trending_videos = yt_trending.get_trending_videos()
    yt_trending.save_to_json(trending_videos)
