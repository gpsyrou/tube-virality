from dotenv import load_dotenv
import os
import json
from googleapiclient.discovery import build
from datetime import datetime
from typing import Any, Dict

load_dotenv()

class YouTubeTrending:
    def __init__(self,
                 api_key: str, 
                 region_code: str = "GB", 
                 metadata_loc: str = 'tube-virality/assets/meta/trending'
    ):
        self.api_key = api_key
        self.region_code = region_code
        self.metadata_loc = metadata_loc
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_trending_videos(self) -> Dict[str, Any]:
        request = self.youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=self.region_code,
            maxResults=10
        )
        response = request.execute()
        return response

    def save_to_json(self, 
                     data: Dict[str, Any], 
                     filename: str = "trending_videos.json"
    ) -> None:
        output_dir = self.metadata_loc
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.getcwd(), output_dir)

        date_str = datetime.now().strftime("_%Y%m%d")
        filename = os.path.splitext(
            filename)[0] + f"_{self.region_code}" + date_str + os.path.splitext(filename)[1]
        filename = os.path.join(output_dir, filename)

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Trending videos saved to {filename}")


if __name__ == "__main__":
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")

    region_code = "GB"
    yt_trending = YouTubeTrending(api_key, region_code)
    trending_videos = yt_trending.get_trending_videos()
    yt_trending.save_to_json(trending_videos)
