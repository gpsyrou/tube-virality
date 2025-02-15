import json
import os
from datetime import datetime
from typing import List, Dict, Any
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class YouTubeStatsCollector:
    def __init__(self, api_key: str, metadata_loc: str, trending_data_loc: str):
        self.api_key = api_key
        self.metadata_loc = metadata_loc
        self.trending_data_loc = trending_data_loc
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def fetch_video_details(self, 
                            video_id_list: List[str]) -> List[Dict[str, Any]]:
        if not self.api_key:
            print("Error: YOUTUBE_API_KEY environment variable not set.")
            return []

        video_data = []

        for i in range(0, len(video_id_list), 50):
            video_ids = ",".join(video_id_list[i:i + 50])

            try:
                request = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails,status,topicDetails",
                    id=video_ids
                )
                response = request.execute()

                for item in response.get("items", []):
                    video_id = item["id"]
                    snippet = item.get("snippet", {})
                    statistics = item.get("statistics", {})
                    content_details = item.get("contentDetails", {})
                    status = item.get("status", {})
                    topic_details = item.get("topicDetails", {})

                    video_data.append({
                        "video_id": video_id,
                        "channel_id": snippet.get("channelId"),
                        "title": snippet.get("title"),
                        "description": snippet.get("description"),
                        "published_at": snippet.get("publishedAt"),
                        "tags": ",".join(snippet.get("tags", [])),
                        "view_count": int(statistics.get("viewCount", 0)),
                        "like_count": int(statistics.get("likeCount", 0)),
                        "comment_count": int(statistics.get("commentCount", 0)),
                        "dislike_count": int(statistics.get("dislikeCount", 0)),
                        "favorite_count": int(statistics.get("favoriteCount", 0)),
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
                        "collection_day": datetime.now().strftime("%Y-%m-%d")
                    })
            except Exception as e:
                print(f"An error occurred while fetching video details: {e}")

        return video_data

    def save_to_json(self, 
                     video_data: List[Dict[str, Any]]) -> None:
        try:
            os.makedirs(self.metadata_loc, exist_ok=True)

            run_date = datetime.now().strftime("%Y%m%d")
            filename = os.path.join(self.metadata_loc, f"video_stats_{run_date}.json")

            if os.path.exists(filename):
                with open(filename, mode="r", encoding="utf-8") as file:
                    existing_data = json.load(file)
            else:
                existing_data = {}

            for entry in video_data:
                video_id = entry.pop("video_id")
                existing_data[video_id] = entry

            with open(filename, mode="w", encoding="utf-8") as file:
                json.dump(existing_data, file, indent=4, ensure_ascii=False)

            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"An error occurred while saving to JSON: {e}")

    def get_unique_video_ids(self, directory: str) -> List[str]:
        video_ids = set()
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    for item in data.get('items', []):
                        video_ids.add(item.get('id'))
        return list(video_ids)


if __name__ == "__main__":
    api_key = os.getenv("YOUTUBE_API_KEY")
    metadata_loc = 'tube-virality/assets/meta/video_stats'
    trending_data_loc = '/Users/georgiosspyrou/Desktop/GitHub/Projects/tube-virality/tube-virality/assets/meta/trending'

    collector = YouTubeStatsCollector(api_key, metadata_loc, trending_data_loc)
    video_id_list = collector.get_unique_video_ids(trending_data_loc)

    try:
        video_data = collector.fetch_video_details(video_id_list)
        if video_data:
            collector.save_to_json(video_data)
        else:
            print("No video data found.")
    except Exception as e:
        print(f"An error occurred: {e}")
