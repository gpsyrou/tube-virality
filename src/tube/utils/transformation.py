"""
A collection of methods used to support the trending videos retrieval
process, as well as the relevant metadata. The packages acts as a helper
module to compute generic transformations during extracting information and
metadata on Trending page of YouTube.
"""

import urllib.request
import datetime

from typing import List
from bs4 import BeautifulSoup


def url_to_bs4(url: str) -> BeautifulSoup:
    """
    Given a website link (URL), retrieve the corresponding website in an
    HTML format.
    Parameters
    ----------
    url : str
        URL of the webpage that will be transformed to a BeautifulSoup object
    """
    request = urllib.request.urlopen(url)
    if request.getcode() != 200:
        raise Exception('Can not communicate with the client')
    else:
        response = request.read()
        response_html = BeautifulSoup(response, 'html.parser')
        return response_html


def create_url_from_video_id(video_id: str) -> str:
    """ Create the full YouTube URL for a given video_id.
    """
    prefix = 'https://youtu.be/'
    return prefix + video_id


def get_current_datetime(as_type='str') -> str:
    """ Returns the current datetime. Supports 3 output formats:
    Parameters:
    -----------
    as_type:
        'datetime': yyyy-mm-dd hh:mm:ss (default)
        'date': yyyy-mm-dd
        'datetime_ms': yyyy-mm-dd hh:mm:ss.ffffff
    """
    time_now = datetime.datetime.now()
    if as_type == 'datetime':
        return str(time_now).split('.')[0]
    elif as_type == 'date':
        return str(time_now).split('.')[0][0:11]
    elif as_type == 'datetime_ms':
        return time_now
    else:
        raise ValueError('The specified date time is not valid..!')


def get_video_id_from_url(url: str) -> str:
    return url.split('/')[-1]


def get_video_id_from_json_url(
    catalog: dict,
    url_json_tag: str = 'url',
    videos_json_tag: str = 'videos'
) -> List[str]:
    urls_ls = [x[url_json_tag] for x in catalog[videos_json_tag]]
    urls_ls = list(set(map(get_video_id_from_url, urls_ls)))
    return urls_ls
