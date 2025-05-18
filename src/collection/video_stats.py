import os
import json
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple
from googleapiclient.discovery import build

load_dotenv()


class YouTubeStatsCollector:
    """
    A class to collect YouTube video statistics using the YouTube Data API.
    """

    def __init__(self, api_key: str, config_path: str):
        self.api_key = api_key
        self.config = self.load_config(config_path)
        self.metadata_loc = self.config.get("VIDEO_STATS_METADATA_LOC")
        self.trending_csv_path = os.path.join(self.config.get("TRENDING_ODS_DIR"), "trending_videos.csv")
        self.youtube = build("youtube", "v3", developerKey=api_key)

        os.makedirs(self.metadata_loc, exist_ok=True)

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads the configuration from a JSON file."""
        with open(config_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    def fetch_video_details_batch(self, video_id_list: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Fetches video details from YouTube API in batches (max 50 at a time)."""
        video_data = []
        video_ids = ",".join([vid[0] for vid in video_id_list])
        country_codes = {vid[0]: vid[1] for vid in video_id_list}  # Map video_id → country_code

        try:
            time.sleep(1.5)  # Delay to prevent rate limits
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails,status,topicDetails",
                id=video_ids,
            )
            response = request.execute()

            if not response:  # Ensure response is valid
                print("Warning: Empty API response.")
                return []

            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})
                content_details = item.get("contentDetails", {})
                status = item.get("status", {})
                topic_details = item.get("topicDetails", {})

                video_data.append(
                    {
                        "video_id": item["id"],
                        "channel_id": snippet.get("channelId"),
                        "title": snippet.get("title"),
                        "description": snippet.get("description"),
                        "published_at": snippet.get("publishedAt"),
                        "tags": ",".join(snippet.get("tags", [])),
                        "view_count": int(statistics.get("viewCount", 0)),
                        "like_count": int(statistics.get("likeCount", 0)),
                        "comment_count": int(statistics.get("commentCount", 0)),
                        "duration": content_details.get("duration"),
                        "dimension": content_details.get("dimension"),
                        "definition": content_details.get("definition"),
                        "caption": content_details.get("caption"),
                        "licensed_content": content_details.get("licensedContent"),
                        "projection": content_details.get("projection"),
                        "privacy_status": status.get("privacyStatus"),
                        "license": status.get("license"),
                        "embeddable": status.get("embeddable"),
                        "public_stats_viewable": status.get("publicStatsViewable"),
                        "topic_categories": topic_details.get("topicCategories", []),
                        "collection_day": datetime.now().strftime("%Y-%m-%d"),
                        "country_code": country_codes.get(item["id"], "UNKNOWN"),
                    }
                )
        except Exception as e:
            print(f"Error fetching video details: {e}")

        return video_data

    def fetch_video_details(self, video_id_list: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Fetches video details sequentially from the YouTube API."""
        video_data = []

        for i in range(0, len(video_id_list), 50):  # Process in batches of 50
            batch = video_id_list[i : i + 50]
            batch_data = self.fetch_video_details_batch(batch)  # Call batch fetcher
            video_data.extend(batch_data)
            time.sleep(1.5)  # Avoid hitting API rate limits

        return video_data

    def save_to_json(self, video_data: List[Dict[str, Any]]) -> None:
        """Saves the fetched video data to a JSON file."""
        try:
            run_date = datetime.now().strftime("%Y%m%d")
            filename = os.path.join(self.metadata_loc, f"video_stats_{run_date}.json")

            existing_data = {}
            if os.path.exists(filename):
                with open(filename, mode="r", encoding="utf-8") as file:
                    existing_data = json.load(file)

            existing_data.update({entry.pop("video_id"): entry for entry in video_data})

            with open(filename, mode="w", encoding="utf-8") as file:
                json.dump(existing_data, file, indent=4, ensure_ascii=False)

            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def get_unique_video_ids_from_csv(self) -> List[Tuple[str, str]]:
        """Reads unique video IDs and country codes from the CSV file."""
        if not os.path.exists(self.trending_csv_path):
            print(f"Error: CSV file {self.trending_csv_path} not found.")
            return []

        try:
            df = pd.read_csv(self.trending_csv_path, usecols=["id", "country_code"])
            df.drop_duplicates(inplace=True)  # Ensure unique video IDs
            return list(df.itertuples(index=False, name=None))  # Convert to list of tuples (video_id, country_code)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []


if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))

    api_key = os.getenv("YOUTUBE_API_KEY")
    collector = YouTubeStatsCollector(api_key, CONFIG_PATH)
    
    video_id_list = collector.get_unique_video_ids_from_csv()

    if video_id_list:
        try:
            video_data = collector.fetch_video_details(video_id_list)
            if video_data:
                collector.save_to_json(video_data)
            else:
                print("No video data found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("No video IDs found in CSV.")
