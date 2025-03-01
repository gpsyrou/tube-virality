import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime
from typing import Any, Dict

load_dotenv()

class YouTubeTrending:
    """
    A class to interact with the YouTube API to fetch and save trending videos.

    Attributes:
        api_key (str): The API key for accessing the YouTube API.
        country_code (str): The country code to fetch trending videos for.
        config (Dict[str, Any]): The configuration loaded from a JSON file.
        metadata_loc (str): The location to save metadata files.
        youtube (Resource): The YouTube API resource object.

    Methods:
        __init__(api_key: str, config_path: str, country_code: str):
            Initializes the YouTubeTrending instance with the provided API key, configuration path, and country code.

        load_config(config_path: str) -> Dict[str, Any]:
            Loads the configuration from a JSON file.

        get_trending_videos() -> Dict[str, Any]:
            Fetches trending videos from the YouTube API.

        save_to_json(data: Dict[str, Any], filename: str = "trending_videos.json") -> None:
            Saves trending videos data to a JSON file.
    """

    def __init__(self, api_key: str, config_path: str, country_code: str):
        self.api_key = api_key
        self.country_code = country_code
        self.config = self.load_config(config_path)
        base_dir = os.path.dirname(config_path)  # Get base directory from config location
        self.metadata_loc = os.path.join(base_dir, self.config.get("TRENDING_METADATA_LOC"))
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

        os.makedirs(self.metadata_loc, exist_ok=True)  # Ensure metadata directory exists

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads the configuration from a JSON file."""
        with open(config_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    def get_trending_videos(self) -> Dict[str, Any]:
        """Fetches trending videos from YouTube API."""
        request = self.youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=self.country_code,
            maxResults=50
        )
        response = request.execute()
        return response

    def save_to_json(self, data: Dict[str, Any], filename: str = "trending_videos.json") -> None:
        """Saves trending videos data to a JSON file."""
        date_str = datetime.now().strftime("_%Y%m%d")
        filename = os.path.splitext(filename)[0] + f"_{self.country_code}" + date_str + os.path.splitext(filename)[1]
        filename = os.path.join(self.metadata_loc, filename)

        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        with open(filename, mode="w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Trending videos saved to {filename}")


if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")
        exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    country_codes = config.get("TRENDING_COUNTRY_CODES", [])

    for country_code in country_codes:
        print(f"Fetching trending videos for country: {country_code}")
        yt_trending = YouTubeTrending(api_key, CONFIG_PATH, country_code)
        trending_videos = yt_trending.get_trending_videos()
        yt_trending.save_to_json(trending_videos)
        print(f"Saved trending videos for {country_code}\n")
