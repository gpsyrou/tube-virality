"""
Non-Trending Video Sampler (control group collector)

Purpose:
    Builds the "not viral" side of the YouTube Virality dataset. For each country
    in TRENDING_COUNTRY_CODES, it samples recently published videos that are NOT
    in that day's trending lists, so they can later be compared against trending
    videos (viral vs. non-viral).

How it works:
    1. Loads every trending file saved for the current day (all countries) and
       builds the set of trending video IDs. A video trending in any country is
       excluded, since it is not a clean negative. Requires the trending script
       to have run first.
    2. For each country, draws random short publish-time windows within the last
       NON_TRENDING_HOURS_BACK hours and runs search.list (regionCode=country)
       to collect candidate video IDs of a similar age to trending videos.
    3. Removes any candidate found in the trending set.
    4. Fetches snippet, statistics, contentDetails and status for the remaining
       IDs via videos.list (batches of 50).
    5. Saves one JSON file per country per day:
       non_trending_videos_<COUNTRY>_<YYYYMMDD>.json
       Each item carries a _meta block (cohort, region, fetched_at, sampling
       window), and the file includes a "sampling" summary for diagnostics.

Configuration (config.json):
    TRENDING_METADATA_LOC             Folder with the trending JSON files (input).
    NON_TRENDING_METADATA_LOC         Folder for the non-trending JSON files (output).
    NON_TRENDING_WINDOWS_PER_COUNTRY  Number of random time windows per country.
    NON_TRENDING_WINDOW_MINUTES       Length of each publish-time window.
    NON_TRENDING_HOURS_BACK           How far back windows may start.
    TRENDING_COUNTRY_CODES            Countries to sample.

Notes and limitations:
    - Quota: each search.list call costs 100 units; videos.list costs 1 unit per
      batch. If the quota runs out, the data collected so far is saved.
    - No label is stored. "Non-trending" only means "not trending on the
      sampling day". A video may enter trending later, so labels must be
      assigned downstream: drop controls that appear in a trending file within
      X days of publishing, and keep younger ones as pending.
    - regionCode means "viewable in the region", not "uploaded in the region".
    - Busy time windows may return only the 50 newest uploads, which biases the
      sample slightly towards the end of each window.

Usage:
    Run daily, after the trending collector (for example: trending.py && non_trending.py).
    Requires the YOUTUBE_API_KEY environment variable.
"""

import glob
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Set

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


class QuotaExceeded(Exception):
    pass


def _execute(request, retries: int = 3):
    """Executes a request, retrying on 5xx and raising QuotaExceeded on quota errors."""
    for attempt in range(retries):
        try:
            return request.execute()
        except HttpError as e:
            if e.resp.status == 403 and "quotaExceeded" in str(e):
                raise QuotaExceeded() from e
            if e.resp.status >= 500 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class YouTubeNonTrending:
    """Samples recent videos per country that are NOT in the trending lists of the same day.

    Attributes:
        api_key (str): API key for the YouTube API.
        config (Dict[str, Any]): Configuration loaded from a JSON file.
        trending_loc (str): Folder holding the trending JSON files.
        metadata_loc (str): Folder where non-trending files are saved.
        youtube (Resource): The YouTube API resource object.
    """

    VIDEO_PARTS = "snippet,statistics,contentDetails,status"

    def __init__(self, api_key: str, config_path: str):
        self.config = self.load_config(config_path)
        base_dir = os.path.dirname(config_path)
        self.trending_loc = os.path.join(base_dir, self.config["TRENDING_METADATA_LOC"])
        self.metadata_loc = os.path.join(base_dir, self.config["NON_TRENDING_METADATA_LOC"])
        self.n_windows = self.config.get("NON_TRENDING_WINDOWS_PER_COUNTRY", 4)
        self.window_minutes = self.config.get("NON_TRENDING_WINDOW_MINUTES", 10)
        self.hours_back = self.config.get("NON_TRENDING_HOURS_BACK", 48)
        self.youtube = build("youtube", "v3", developerKey=api_key, cache_discovery=False)
        os.makedirs(self.metadata_loc, exist_ok=True)

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    # ---------- exclusion set ----------
    def load_trending_ids(self, date_str: str) -> Set[str]:
        """Union of video IDs trending in ANY country on the given day (YYYYMMDD)."""
        pattern = os.path.join(self.trending_loc, f"trending_videos_*_{date_str}*.json")
        files = glob.glob(pattern)
        if not files:
            raise FileNotFoundError(
                f"No trending files for {date_str} in {self.trending_loc}. Run the trending script first."
            )
        ids: Set[str] = set()
        for path in files:
            with open(path, "r", encoding="utf-8") as f:
                ids.update(item["id"] for item in json.load(f).get("items", []))
        log.info("Loaded %d trending IDs from %d files for %s", len(ids), len(files), date_str)
        return ids

    # ---------- sampling ----------
    def sample_video_ids(self, country_code: str, seed: int | None = None) -> Dict[str, Dict[str, str]]:
        """Random short publish-time windows -> {video_id: window info}.

        Stops early (keeping what it has) if the quota runs out.
        """
        rng = random.Random(seed)
        now = datetime.now(timezone.utc)
        sampled: Dict[str, Dict[str, str]] = {}

        for _ in range(self.n_windows):
            start = now - timedelta(minutes=rng.uniform(self.window_minutes, self.hours_back * 60))
            end = start + timedelta(minutes=self.window_minutes)
            try:
                resp = _execute(self.youtube.search().list(
                    part="id", type="video", regionCode=country_code,
                    publishedAfter=_iso(start), publishedBefore=_iso(end),
                    order="date", maxResults=50,
                ))
            except QuotaExceeded:
                log.error("Quota exceeded during sampling for %s; keeping %d IDs", country_code, len(sampled))
                break
            for item in resp.get("items", []):
                sampled[item["id"]["videoId"]] = {
                    "window_start": _iso(start), "window_end": _iso(end)
                }
        return sampled

    def fetch_videos(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for i in range(0, len(video_ids), 50):
            try:
                resp = _execute(self.youtube.videos().list(
                    part=self.VIDEO_PARTS, id=",".join(video_ids[i:i + 50])))
            except QuotaExceeded:
                log.error("Quota exceeded while fetching video details; returning partial data")
                break
            items.extend(resp.get("items", []))
        return items

    def get_non_trending_videos(self, country_code: str, trending_ids: Set[str]) -> Dict[str, Any]:
        sampled = self.sample_video_ids(country_code)
        candidates = [v for v in sampled if v not in trending_ids]
        log.info("%s: sampled %d IDs, %d after excluding trending",
                 country_code, len(sampled), len(candidates))

        fetched_at = datetime.now(timezone.utc).isoformat()
        items = self.fetch_videos(candidates)
        for item in items:
            item["_meta"] = {
                "cohort": "non_trending",
                "rank": None,
                "region": country_code,
                "fetched_at": fetched_at,
                **sampled[item["id"]],
            }
        return {
            "fetched_at": fetched_at,
            "region": country_code,
            "cohort": "non_trending",
            "sampling": {
                "n_windows": self.n_windows,
                "window_minutes": self.window_minutes,
                "hours_back": self.hours_back,
                "n_sampled": len(sampled),
                "n_excluded_trending": len(sampled) - len(candidates),
            },
            "items": items,
        }

    # ---------- save ----------
    def save_to_json(self, data: Dict[str, Any], country_code: str, date_str: str,
                     filename: str = "non_trending_videos.json") -> None:
        stem, ext = os.path.splitext(filename)
        path = os.path.join(self.metadata_loc, f"{stem}_{country_code}_{date_str}{ext}")
        with open(path, mode="w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        log.info("Non-trending videos saved to %s", path)


if __name__ == "__main__":
    CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config.json"))

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        log.error("YOUTUBE_API_KEY environment variable not set.")
        exit(1)

    collector = YouTubeNonTrending(api_key, CONFIG_PATH)
    country_codes = collector.config.get("TRENDING_COUNTRY_CODES", [])
    date_str = datetime.now().strftime("%Y%m%d")  # same local-date convention as the trending script

    try:
        trending_ids = collector.load_trending_ids(date_str)
    except FileNotFoundError as e:
        log.error(e)
        exit(1)

    for country_code in country_codes:
        log.info("Sampling non-trending videos for country: %s", country_code)
        try:
            data = collector.get_non_trending_videos(country_code, trending_ids)
            collector.save_to_json(data, country_code, date_str)
        except Exception:
            log.exception("Failed for %s, continuing with next country", country_code)
