import sys
import os
from pathlib import Path

PROJECT_DIR_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parents[2]
COLLECTOR_DIR_PATH = os.path.join(PROJECT_DIR_PATH, 'src/tube')
DATA_DIR_PATH = os.path.join(PROJECT_DIR_PATH, 'src/tube/data')
sys.path.append(COLLECTOR_DIR_PATH)

from trending import TrendingVideoCollector  # noqa: E402

# Configuarations for Trending Page
CONFIGS_DIR_PATH = os.path.join(PROJECT_DIR_PATH, 'config')
catalog_filename = os.path.join(CONFIGS_DIR_PATH, 'video_catalog.json')

trending_page = 'https://www.youtube.com/feed/trending'

trending_videos_file = 'trending_videos_metadata.csv'
trending_videos_filename = os.path.join(DATA_DIR_PATH, trending_videos_file)


if __name__ == '__main__':

    video_collector = TrendingVideoCollector(
        trending_page=trending_page
        )
    video_collector.write_trending_dataframes_to_csv(
        out_filename=trending_videos_filename
    )
    video_collector.populate_video_catalog(catalog_path=catalog_filename)
