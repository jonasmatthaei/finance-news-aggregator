import json
import os
from enum import Enum
from datetime import datetime
import xml.etree.ElementTree as ET
from finnews.parser import NewsParser
from finnews.fields import cnbc_rss_feeds_id
from finnews.utilities.add_content import enrich_news_article
from finnews.utilities.openai_functions import identify_stocks_and_investors, post_process_analysis
from typing import Dict, List, Union
from transformers import pipeline

class CNBC:
    def __init__(self):
        self.url = 'https://www.cnbc.com/id/{topic_id}/device/rss/rss.html'
        self.topic_categories = cnbc_rss_feeds_id
        self.news_parser = NewsParser(client='cnbc')
        self.sentiment_pipeline = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

    def investing_feeds(self, topic: str) -> str:
        topic = topic.name.lower() if isinstance(topic, Enum) else topic
        xml_data = self.news_parser._make_request(url=self._check_key(topic_id=topic))

        # Parse XML data
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return json.dumps({"error": "Failed to parse XML data"})

        articles = []

        # Hardcoded max_articles
        max_articles = 3

        for item in root.findall('.//item')[:max_articles]:
            article = {
                'Title': item.find('title').text if item.find('title') is not None else 'No Title',
                'Link': item.find('link').text if item.find('link') is not None else 'No Link',
                'Publication Date': item.find('pubDate').text if item.find('pubDate') is not None else 'No Date',
                'Description': item.find('description').text if item.find('description') is not None else 'No Description',
                'Source_ID': f'CNBC.investing_feeds.{topic}',
                'Topic': topic
            }
            enriched_article = enrich_news_article(article)

            # Analyze the article content using OpenAI
            article_content = f"{enriched_article['Title']} {enriched_article['Summary']}"
            analysis = identify_stocks_and_investors(article_content)
            analysis = post_process_analysis(analysis)

            # Add the analysis to the enriched article
            enriched_article['Stocks'] = [stock.ticker for stock in analysis.stocks]
            enriched_article['Market Update'] = analysis.market_update
            enriched_article['Investor Types'] = analysis.investor_types

            # Perform sentiment analysis
            sentiment_result = self.sentiment_pipeline(article_content)[0]
            enriched_article['Sentiment'] = [sentiment_result['score'], sentiment_result['label']]

            articles.append(enriched_article)

        json_output = json.dumps(articles, indent=2, default=str)

        # Hardcoded save_to_file
        self._save_to_file(json_output, topic)

        return json_output

    def _check_key(self, topic_id: str) -> str:
        if topic_id in self.topic_categories:
            return self.url.format(topic_id=self.topic_categories[topic_id])
        raise KeyError("The value you're searching for does not exist.")

    def _save_to_file(self, json_output: str, topic: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cnbc_investing_{topic}_{timestamp}.json"
        os.makedirs('output', exist_ok=True)
        filepath = os.path.join('output', filename)
        with open(filepath, 'w') as f:
            f.write(json_output)
        print(f"JSON output saved to {filepath}")

print("CNBC module loaded from:", __file__)
