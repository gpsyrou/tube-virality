import unittest
import numpy as np
from utils.transformation import create_url_from_video_id

video_url = 'https://youtu.be/iByQSaWTR1g'


class TestTubeTranformation(unittest.TestCase):

    def testCreateURLfromVideoId(
        self,
        err_msg: str = 'Constructed URL  is not valid'
    ):
        url_from_video_id = create_url_from_video_id(video_id='iByQSaWTR1g')
        self.assertEqual(video_url, url_from_video_id, msg=err_msg)
