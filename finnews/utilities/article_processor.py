import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz
from transformers import pipeline
from finnews.utilities.add_content import enrich_news_article
from finnews.utilities.openai_functions import identify_stocks_and_investors

class ArticleProcessor:
    def __init__(self):
        self.sentiment_pipeline = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

    def process_xml(self, xml_data, topic):
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        items = channel.findall('item')

        now = datetime.now(pytz.utc)
        twenty_four_hours_ago = now - timedelta(hours=24)

        return [self._process_item(item, topic, now, twenty_four_hours_ago)
                for item in items
                if self._is_recent(item, now, twenty_four_hours_ago)]

    def _process_item(self, item, topic, now, twenty_four_hours_ago):
        article = self._create_article_dict(item, topic)
        enriched_article = enrich_news_article(article)
        enriched_article['Sentiment'] = self._analyze_sentiment(enriched_article['Title'])
        enriched_article['StockAnalysis'] = identify_stocks_and_investors(enriched_article['Summary']).dict()
        self._print_article_info(enriched_article)
        return enriched_article

    def _create_article_dict(self, item, topic):
        return {
            "Title": item.find('title').text,
            "Link": item.find('link').text,
            "Publication Date": item.find('pubDate').text,
            "Source_ID": f"CNBC.investing_feeds.{topic}",
            "Topic": topic
        }

    def _is_recent(self, item, now, twenty_four_hours_ago):
        try:
            # Try parsing the date in the format provided by Yahoo Finance
            pub_date = datetime.strptime(item.find('pubDate').text, '%Y-%m-%dT%H:%M:%SZ')
            pub_date = pub_date.replace(tzinfo=pytz.UTC)
        except ValueError:
            # If that fails, try the original format
            pub_date = datetime.strptime(item.find('pubDate').text, '%a, %d %b %Y %H:%M:%S %Z')
            pub_date = pub_date.replace(tzinfo=pytz.UTC)

        return twenty_four_hours_ago <= pub_date <= now

    def _analyze_sentiment(self, title):
        result = self.sentiment_pipeline(title)[0]
        return {'label': result['label'], 'score': result['score']}

    def _print_article_info(self, article):
        print(f"Title: {article['Title']}")
        print(f"Link: {article['Link']}")
        print(f"Publication Date: {article['Publication Date']}")
        print(f"Summary: {article['Summary']}")
        print(f"Sentiment: {article['Sentiment']}")
        print("-" * 80)
