import glob
import json
import logging
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Matches both the legacy "..._US__20261010.json" and the new "..._US_20261010T120000Z.json"
FILENAME_RE = re.compile(
    r"_(?P<region>[A-Z]{2})_+(?P<date>\d{8})(?:T(?P<time>\d{6})Z)?\.json$"
)


class TrendingSilverProcessor:
    """Flattens raw trending JSON files (bronze) into normalized Parquet tables (silver).

    Outputs:
        fact_snapshot/  video x region x fetch time (partitioned by date)
        dim_video.parquet  one row per video (static attributes)
    """

    COUNT_COLS = ["view_count", "like_count", "comment_count"]

    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        base_dir = os.path.dirname(config_path)
        self.json_dir = os.path.join(base_dir, self.config["TRENDING_METADATA_LOC"])
        self.output_dir = os.path.join(base_dir, self.config["TRENDING_ODS_DIR"])

        if not os.path.exists(self.json_dir):
            raise FileNotFoundError(f"Error: Directory {self.json_dir} not found.")

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    # ---------- extract ----------
    def parse_file(self, filepath: str) -> Tuple[List[dict], List[dict]]:
        """Returns (fact_rows, video_rows) for one bronze file."""
        match = FILENAME_RE.search(os.path.basename(filepath))
        if not match:
            raise ValueError("filename does not match the expected pattern")

        with open(filepath, "r", encoding="utf-8") as file:
            payload = json.load(file)

        region = payload.get("region") or match["region"]

        # Legacy files have no fetched_at: fall back to the date in the filename
        if payload.get("fetched_at"):
            fetched_at, inferred = pd.Timestamp(payload["fetched_at"]), False
        else:
            fetched_at = pd.Timestamp(datetime.strptime(match["date"], "%Y%m%d"), tz="UTC")
            inferred = True

        facts, videos = [], []
        for position, item in enumerate(payload.get("items", []), start=1):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            facts.append({
                "video_id": item["id"],
                "region": region,
                "fetched_at": fetched_at,
                "fetched_at_inferred": inferred,
                "rank": item.get("_meta", {}).get("rank", position),
                "view_count": stats.get("viewCount"),
                "like_count": stats.get("likeCount"),        # missing if hidden
                "comment_count": stats.get("commentCount"),  # missing if disabled
                "published_at": snippet.get("publishedAt"),  # only used for age_hours
            })
            videos.append({
                "video_id": item["id"],
                "channel_id": snippet.get("channelId"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "title": snippet.get("title"),
                "description": snippet.get("description", ""),
                "category_id": snippet.get("categoryId"),
                "default_language": snippet.get("defaultLanguage"),
                "default_audio_language": snippet.get("defaultAudioLanguage"),
                "tags": snippet.get("tags", []),
                "seen_at": fetched_at,
            })
        return facts, videos

    def load_json_files(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        all_facts, all_videos = [], []

        for filepath in sorted(glob.glob(os.path.join(self.json_dir, "*.json"))):
            try:
                facts, videos = self.parse_file(filepath)
                all_facts += facts
                all_videos += videos
            except Exception as e:
                log.error("Error reading %s: %s", os.path.basename(filepath), e)

        return pd.DataFrame(all_facts), pd.DataFrame(all_videos)

    # ---------- transform ----------
    def build_fact(self, raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.copy()
        for col in self.COUNT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        df["fetched_at"] = pd.to_datetime(df["fetched_at"], utc=True)
        df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
        df["age_hours"] = (df["fetched_at"] - df["published_at"]).dt.total_seconds() / 3600

        df = (
            df.drop(columns="published_at")
              .drop_duplicates(["video_id", "region", "fetched_at"])
              .sort_values(["fetched_at", "region", "rank"])
        )
        df["date"] = df["fetched_at"].dt.date.astype(str)
        return df

    def build_dim_video(self, raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.copy()
        df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
        df["seen_at"] = pd.to_datetime(df["seen_at"], utc=True)
        df = df.sort_values("seen_at")

        seen = df.groupby("video_id")["seen_at"].agg(first_seen_at="min", last_seen_at="max")
        # Keep the most recent title/description/tags per video
        latest = df.drop_duplicates("video_id", keep="last").drop(columns="seen_at")
        return latest.merge(seen, on="video_id")

    def process_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        raw_facts, raw_videos = self.load_json_files()

        if raw_facts.empty:
            log.warning("No data found in JSON files.")
            return pd.DataFrame(), pd.DataFrame()

        fact = self.build_fact(raw_facts)
        dim_video = self.build_dim_video(raw_videos)
        log.info("Loaded %d snapshots, %d unique videos.", len(fact), len(dim_video))
        self.validate(fact, dim_video)
        return fact, dim_video

    # ---------- validate ----------
    @staticmethod
    def validate(fact: pd.DataFrame, dim_video: pd.DataFrame) -> None:
        checks = {
            "duplicate fact keys": fact.duplicated(["video_id", "region", "fetched_at"]).sum(),
            "duplicate video_id in dim_video": dim_video["video_id"].duplicated().sum(),
            "likes > views": (fact["like_count"] > fact["view_count"]).sum(),
            "negative age_hours": (fact["age_hours"] < 0).sum(),
            "facts without a dim_video row": (~fact["video_id"].isin(dim_video["video_id"])).sum(),
        }
        for name, count in checks.items():
            (log.warning if count else log.info)("check '%s': %d", name, count)

        null_rates = fact.groupby("region")[["like_count", "comment_count"]].agg(
            lambda s: s.isna().mean()
        )
        log.info("Null rates by region:\n%s", null_rates.round(3))

        multi = fact.groupby("video_id")["region"].nunique()
        log.info("Videos trending in >1 region: %.1f%%", 100 * (multi > 1).mean())

    # ---------- load ----------
    def save_to_parquet(self, fact: pd.DataFrame, dim_video: pd.DataFrame) -> None:
        if fact.empty:
            log.warning("No data to save.")
            return

        os.makedirs(self.output_dir, exist_ok=True)
        fact_dir = os.path.join(self.output_dir, "fact_snapshot")
        shutil.rmtree(fact_dir, ignore_errors=True)  # full rebuild: avoid duplicate part files

        fact.to_parquet(fact_dir, partition_cols=["date"], index=False)
        dim_path = os.path.join(self.output_dir, "dim_video.parquet")
        dim_video.to_parquet(dim_path, index=False)
        log.info("Saved fact_snapshot to %s and dim_video to %s", fact_dir, dim_path)


if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))

    try:
        processor = TrendingSilverProcessor(CONFIG_PATH)
        fact, dim_video = processor.process_data()
        processor.save_to_parquet(fact, dim_video)
    except Exception:
        log.exception("An error occurred")
