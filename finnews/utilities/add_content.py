import requests
from textblob import TextBlob
from newspaper import Article

def fetch_article_summary(url):
    """
    Fetches the summary of an article from the given URL.

    Args:
        url (str): The URL of the article.

    Returns:
        str: The summary of the article.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    session = requests.Session()
    session.headers.update(headers)

    response = session.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    article = Article(url)
    article.set_html(response.text)
    article.parse()
    article.nlp()
    return article.summary

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        Sentiment: The sentiment analysis result.
    """
    analysis = TextBlob(text)
    return analysis.sentiment

def enrich_news_article(article):
    """
    Enriches a news article with a summary and sentiment analysis.

    Args:
        article (dict): The article to enrich. Must contain 'Title', 'Link', 'Publication Date', and 'Media Content URL'.

    Returns:
        dict: The enriched article with summary and sentiment.
    """
    summary = fetch_article_summary(article['Link'])
    sentiment = analyze_sentiment(summary)

    enriched_article = {
        "Title": article['Title'],
        "Link": article['Link'],
        "Publication Date": article['Publication Date'],
        "Summary": summary,
        "Sentiment": sentiment,
        "Source_ID": article['Source_ID'],
        "Topic": article['Topic']
    }

    return enriched_article
