import json
import os
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Define the metadata location
metadata_loc = 'tube-virality/assets/meta/video_stats'

def fetch_video_details(video_id_list):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")
        return []

    youtube = build("youtube", "v3", developerKey=api_key)

    video_data = []

    # Batch requests for video details
    for i in range(0, len(video_id_list), 50):  # API allows a maximum of 50 IDs per request
        video_ids = ",".join(video_id_list[i:i + 50])

        try:
            request = youtube.videos().list(
                part="snippet,statistics",
                id=video_ids
            )
            response = request.execute()

            for item in response.get("items", []):
                video_id = item["id"]
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})

                video_data.append({
                    "video_id": video_id,
                    "channel_id": snippet.get("channelId"),
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "published_at": snippet.get("publishedAt"),
                    "view_count": int(statistics.get("viewCount", 0)),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "comment_count": int(statistics.get("commentCount", 0)),
                    "tags": ",".join(snippet.get("tags", [])),
                    "collection_day": datetime.now().strftime("%Y-%m-%d")
                })
        except Exception as e:
            print(f"An error occurred while fetching video details: {e}")

    return video_data

def save_to_json(video_data):
    try:
        # Create the directory if it doesn't exist
        os.makedirs(metadata_loc, exist_ok=True)

        # Construct the filename with the current date
        run_date = datetime.now().strftime("%Y%m%d")
        filename = os.path.join(metadata_loc, f"video_statistics_{run_date}.json")

        # Load existing data if the file exists
        if os.path.exists(filename):
            with open(filename, mode="r", encoding="utf-8") as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        # Create a dictionary for fast look-up by video_id and collection_day
        existing_data_dict = {
            (entry["video_id"], entry["collection_day"]): entry
            for entry in existing_data
        }

        # Update or add new data
        for entry in video_data:
            key = (entry["video_id"], entry["collection_day"])
            existing_data_dict[key] = entry

        # Convert the dictionary back to a list
        updated_data = list(existing_data_dict.values())

        # Save the updated data to the JSON file
        with open(filename, mode="w", encoding="utf-8") as file:
            json.dump(updated_data, file, indent=4, ensure_ascii=False)

        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")

# Example usage
if __name__ == "__main__":
    video_id_list = ["xqdUBkO-zjo", "V2HqOw1-w20"]  # Replace with actual video IDs

    try:
        video_data = fetch_video_details(video_id_list)
        if video_data:
            save_to_json(video_data)
        else:
            print("No video data found.")
    except Exception as e:
        print(f"An error occurred: {e}")
