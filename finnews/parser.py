import xml.etree.ElementTree as ET

from typing import List
from typing import Dict

import requests


class NewsParser():

    """
    ### Overview:
    ----
    Serves as the parser for each of the
    news clients.
    """

    def __init__(self, client: str) -> None:
        """Initializes the new parser client.

        ### Overview:
        ----
        To help standardize the parser process the
        `NewsParser` client is used to help make the
        request, parse the response, and organize the
        results for each of the news client.

        ### Arguments:
        ----
        client (str): The ID of the client you wish to use
            the parser for.

        ### Usage:
        ----
            >>> self.news_parser = NewsParser(client='cnbc')
        """

        self.client = client
        self.paths = {
            'cnbc': './channel/item',
            'nasdaq': './channel/item',
            'market_watch': './channel/item',
            'sp_global': '.channel/item',
            'seeking_alpha': '.channel/item',
            'cnn_finance': '.channel/item',
            'wsj': '.channel/item',
            'yahoo': '.channel/item'
        }

        self.namespaces = {
            'cnbc': ['{http://search.cnbc.com/rss/2.0/modules/siteContentMetadata}'],
            'nasdaq': [
                '{http://purl.org/dc/elements/1.1/}',
                '{http://nasdaq.com/reference/feeds/1.0}',
                '{http://purl.org/dc/elements/1.1/}'
            ],
            'market_watch': [
                '{http://rssnamespace.org/feedburner/ext/1.0}'
            ],
            'sp_global': [
                ''
            ],
            'seeking_alpha': [
                '{http://search.yahoo.com/mrss/}',
                '{https://seekingalpha.com/api/1.0}'
            ],
            'cnn_finance': [
                '{http://rssnamespace.org/feedburner/ext/1.0}',
                '{http://search.yahoo.com/mrss/}'
            ],
            'wsj': [
                '{http://dowjones.net/rss/}',
                '{http://purl.org/rss/1.0/modules/content/}',
                '{http://search.yahoo.com/mrss/}'
            ],
            'yahoo': [
                '{http://search.yahoo.com/mrss/}'
            ]
        }

    def _parse_response(self, response_content: str) -> List[Dict]:
        """Parses the text content from a request and ### Returns the news item collection.

        ### Arguments:
        ----
        response_content (str): The raw XML content from the RSS feed that
            needs to be parsed.

        ### Returns:
        ----
        List[Dict]: A list of news items objects.
        """

        root = ET.fromstring(response_content)
        entries = []
        for item in root.findall('.//item'):
            entry = {
                'title': item.find('title').text if item.find('title') is not None else '',
                'link': item.find('link').text if item.find('link') is not None else '',
                'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else '',
                'source': item.find('source').text if item.find('source') is not None else '',
                'guid': item.find('guid').text if item.find('guid') is not None else '',
                'media_content': item.find('{http://search.yahoo.com/mrss/}content').attrib.get('url') if item.find('{http://search.yahoo.com/mrss/}content') is not None else '',
                'media_credit': item.find('{http://search.yahoo.com/mrss/}credit').text if item.find('{http://search.yahoo.com/mrss/}credit') is not None else ''
            }
            entries.append(entry)
        return entries


    def _make_request(self, url: str, params: Dict = None) -> str:

        """Used to make a request for each of the news clients.

        ### Arguments:
        ----
        url (str): The URL to request.

        params (dict): The paramters to pass through to the request.

        ### Returns:
        ----
        List[Dict]: A list of news items objects.
        """

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

        headers = {
            'user-agent': user_agent
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text
