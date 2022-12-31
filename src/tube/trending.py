import os
import re
import json
import pandas as pd
from typing import List
from pandas.errors import EmptyDataError
from utils.transformation import (
    url_to_bs4,
    create_url_from_video_id,
    get_current_datetime,
    get_video_id_from_json_url
    )

# Setup the schema/column names of the features in the trending output file
trending_df_schema = [
    'video_id', 
    'video_url', 
    'trending_position', 
    'trending_date', 
    'trending_datetime'
    ]

class TrendingVideoCollector:
    """ Class to retrieve the Trending videos and their respective metadata
    from YouTube trending page.

    Attributes:
    ------------
        trending_page: The URL string indicatin the web address of the trending
                       page
        trending_page_parsed:
                       The parsed version of the HTML page as a BeautifulSoup 
                       object.
        trending_videos_dict:
                        Dictionary of the collected videos retrieved from the
                        trending_page.
    """
    def __init__(self, trending_page: str):
        self.trending_page = trending_page
        self.trending_page_parsed = url_to_bs4(trending_page)
        self.trending_videos_dict = self.collect_trending_videos()

    def collect_trending_videos(self) -> dict:
        trending_videos_retrieved = re.findall(
            pattern='(?<=watchEndpoint":{)("videoId":".+?(?="))',
            string=str(self.trending_page_parsed)
            )

        self.trending_videos_dict = {}

        for idx, vid_id in enumerate(trending_videos_retrieved, start=1):
            video_id = vid_id.split(':')[1].strip('"')
            if video_id not in self.trending_videos_dict.keys():
                self.trending_videos_dict[video_id] = idx

        return self.trending_videos_dict

    def generate_trending_videos_metadata(
        self,
        trending_df_schema: List[str]
    ) -> pd.DataFrame:

        df_switch = []

        for video_id, trending_position in self.trending_videos_dict.items():
            video_url = create_url_from_video_id(video_id=video_id)
            datetime = get_current_datetime()
            date = datetime.split(' ')[0]
            df_switch.append(
                (video_id, video_url, trending_position, date, datetime)
                )
        trending_df = pd.DataFrame(
            df_switch,
            columns=trending_df_schema
            )

        return trending_df

    def write_trending_dataframes_to_csv(
        self,
        out_filename: str
    ) -> None:

        trending_videos_df = self.generate_trending_videos_metadata(
            trending_df_schema=trending_df_schema
        )

        if not os.path.isfile(out_filename):
            pd.DataFrame().to_csv(out_filename, index=True)

        try:
            df_trending_history = pd.read_csv(out_filename, index_col=[0])
            df_trending_history = df_trending_history.append(
                trending_videos_df
                )
            print('\nUpdating metadata file at: {0}\n'.format(out_filename))
            df_trending_history.to_csv(out_filename, index=True)
        except EmptyDataError:
            print('\nUpdating metadata file at: {0}\n'.format(out_filename))
            trending_videos_df.to_csv(out_filename, index=True)

    def populate_video_catalog(self, catalog_path: str):

        with open(catalog_path) as video_catalog_json:
            catalog = json.load(video_catalog_json)
        try:
            last_catalog_index = catalog['videos'][-1]['id']
        except IndexError:
            last_catalog_index = 0

        existing_trending_video_ls = get_video_id_from_json_url(catalog)

        for video_id in self.trending_videos_dict.keys():
            # Check that video_id does not already exist in catalog
            if video_id not in existing_trending_video_ls:
                print('\nInserting video_id: {0} to catalog'.format(video_id))
                video_url = create_url_from_video_id(video_id=video_id)
                last_catalog_index = last_catalog_index + 1
                catalog['videos'].append(
                    {'id': last_catalog_index, 'url': video_url, 'run': True}
                    )
            else:
                print('\nSkipping Video_id: {0} - already exists ... '.format(
                    video_id)
                    )
        print('\nUpdating Catalog file with new trending videos ...')
        json.dump(catalog,
                  open(catalog_path, 'w'),
                  sort_keys=True,
                  indent=4,
                  separators=(',', ': ')
                  )
