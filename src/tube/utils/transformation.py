"""
A collection of methods used to support the trending videos retrieval
process, as well as the relevant metadata. The packages acts as a helper
module to compute generic transformations.
"""

from bs4 import BeautifulSoup
import urllib.request


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
