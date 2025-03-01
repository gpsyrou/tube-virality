import os
import json
import pandas as pd

class VideoStatsProcessor:
    """Class to process YouTube video statistics from JSON files and merge them into a DataFrame."""

    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        base_dir = os.path.dirname(config_path)  # Get base directory from config location
        self.json_dir = os.path.join(base_dir, self.config.get("VIDEO_STATS_METADATA_LOC"))
        self.output_dir = os.path.join(base_dir, self.config.get("VIDEO_STATS_ODS_DIR"))

        if not os.path.exists(self.json_dir):
            raise FileNotFoundError(f"Error: Directory {self.json_dir} not found.")

    @staticmethod
    def load_config(config_path: str) -> dict:
        with open(config_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    def load_json_files(self) -> pd.DataFrame:
        all_data = []

        for filename in os.listdir(self.json_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.json_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        data = json.load(file)

                        for video_id, details in data.items():
                            details["video_id"] = video_id  # Ensure video_id is included
                            all_data.append(details)

                except Exception as e:
                    print(f"Error reading {filename}: {e}")

        return pd.DataFrame(all_data)

    def process_data(self) -> pd.DataFrame:
        df = self.load_json_files()

        if df.empty:
            print("No data found in JSON files.")
        else:
            print(f"Loaded {len(df)} records from JSON files.")
            print(df.head())

        return df

    def save_to_csv(self, df: pd.DataFrame):
        if df.empty:
            print("No data to save.")
            return

        os.makedirs(self.output_dir, exist_ok=True)  # Ensure output directory exists
        output_path = os.path.join(self.output_dir, "merged_video_stats.csv")

        df.to_csv(output_path, index=False, encoding="utf-8")
        print(f"Merged data saved to {output_path}")

if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))

    try:
        processor = VideoStatsProcessor(CONFIG_PATH)
        df = processor.process_data()
        processor.save_to_csv(df)
    except Exception as e:
        print(f"An error occurred: {e}")
