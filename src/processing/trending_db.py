import os
import json
import pandas as pd


class TrendingVideoProcessor:
    """Class to process trending video metadata and save it as a CSV."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
        self.metadata_dir = os.path.join('tube-virality', self.config.get("TRENDING_METADATA_LOC"))
        self.output_dir = self.config.get("TRENDING_ODS_DIR")

        if not os.path.isdir(self.metadata_dir):
            raise FileNotFoundError(f"Metadata directory '{self.metadata_dir}' does not exist")

        os.makedirs(self.output_dir, exist_ok=True)

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)

    def extract_video_data(self, json_file: str, video_list: list):
        """Extracts video metadata from a JSON file and appends to video_list."""
        country_code = os.path.basename(json_file).split('_')[2]
        
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        for position, item in enumerate(data.get("items", []), start=1):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})

            video_info = {
                "id": item.get("id"),
                "trending_position": position,
                "publishedAt": snippet.get("publishedAt"),
                "country_code": country_code,
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
            video_list.append(video_info)

    def process_videos(self):
        """Processes all JSON files and saves a CSV with all trending videos."""
        video_list = []
        
        for filename in os.listdir(self.metadata_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.metadata_dir, filename)
                self.extract_video_data(file_path, video_list)

        df = pd.DataFrame(video_list)
        output_path = os.path.join("tube-virality", self.output_dir, "trending_videos.csv")
        df.to_csv(output_path, index=False)

        print(f"Trending videos merged file saved to {output_path}")


if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))
    processor = TrendingVideoProcessor(CONFIG_PATH)
    processor.process_videos()
