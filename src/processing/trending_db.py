import os
import json
import pandas as pd


class TrendingVideoProcessor:
    """Class to process trending video metadata and save it as a CSV."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
        self.metadata_dir = self.config.get("TRENDING_METADATA_LOC")
        self.output_dir = self.config.get("TRENDING_ODS_DIR")

        if not os.path.isdir(self.metadata_dir):
            raise FileNotFoundError(f"Metadata directory '{self.metadata_dir}' does not exist")

        os.makedirs(self.output_dir, exist_ok=True)

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)

    def extract_video_data(self, json_file: str):
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        videos = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})

            video_info = {
                "id": item.get("id"),
                "publishedAt": snippet.get("publishedAt"),
                "channelId": snippet.get("channelId"),
                "channelTitle": snippet.get("channelTitle"),
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "categoryId": snippet.get("categoryId"),
                "viewCount": statistics.get("viewCount"),
                "likeCount": statistics.get("likeCount"),
                "commentCount": statistics.get("commentCount"),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "defaultAudioLanguage": snippet.get("defaultAudioLanguage"),
            }
            videos.append(video_info)
        return videos

    def process_videos(self):
        all_videos = []
        for filename in os.listdir(self.metadata_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.metadata_dir, filename)
                all_videos.extend(self.extract_video_data(file_path))

        df = pd.DataFrame(all_videos)
        output_path = os.path.join(self.output_dir, "trending_videos.csv")
        df.to_csv(output_path, index=False)

        print(f"Trending videos merged file saved to {output_path}")


if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))
    processor = TrendingVideoProcessor(CONFIG_PATH)
    processor.process_videos()
