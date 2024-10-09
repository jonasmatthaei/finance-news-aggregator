from openai import OpenAI
import os
import json
from pydantic import BaseModel
from typing import List, Literal
import dotenv

dotenv.load_dotenv()

# Set up your OpenAI API key



class StockInfo(BaseModel):
    ticker: str

class ArticleAnalysis(BaseModel):
    stocks: List[StockInfo]
    market_update: Literal[
        "Earnings Reports", "IPO Announcements", "Dividend Updates",
        "Economic Indicators", "Market News and Analysis", "Cryptocurrency Market News",
        "Analyst Ratings and Upgrades/Downgrades", "Regulatory Changes",
        "Mergers and Acquisitions", "Blockchain Technology Developments",
        "MEME Investing", "Other"
    ]
    investor_types: List[str]

INVESTOR_TYPES = [
    "Long-term Investor", "Swing Trader", "Day Trader", "Value Investor",
    "Growth Investor", "Income Investor", "Passive Investor", "Options Trader",
    "Cryptocurrency Trader/Investor"
]

MARKET_UPDATE_TYPES = [
    "Earnings Reports", "IPO Announcements", "Dividend Updates", "Economic Indicators",
    "Market News and Analysis", "Cryptocurrency Market News", "Analyst Ratings and Upgrades/Downgrades",
    "Regulatory Changes", "Mergers and Acquisitions", "Blockchain Technology Developments",
    "MEME Investing", "Other"
]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def identify_stocks_and_investors(article_content):
    """
    Identify stocks mentioned in the article content, the overall market update type, and determine relevant investor types.

    :param article_content: str, the article summary or full content
    :return: ArticleAnalysis object with stock information, market update type, and relevant investor types
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a financial analyst identifying stocks, the overall market update type, and relevant investor types in news articles. Provide concise and deterministic outputs."},
            {"role": "user", "content": f"""
            Analyze the following article content and:
            1. Identify any stocks or companies mentioned. Use only official ticker symbols.
            2. Determine the most relevant overall type of market update from this list:
               {MARKET_UPDATE_TYPES}
               Choose only one type that best describes the overall content of the article.
            3. Determine which types of investors would find this article most relevant from this list:
               {INVESTOR_TYPES}
               Choose only the most relevant types. Limit your selection to at most 3 types.

            Article content:
            {article_content}

            Provide the output as an object with three fields:
            1. 'stocks': an array of objects, each with a 'ticker' field.
            2. 'market_update': a single string from the provided list of market update types.
            3. 'investor_types': an array of strings from the provided list of investor types.

            If no stocks are mentioned, return an empty array for 'stocks'.
            If no investor types are clearly relevant, return an empty array for 'investor_types'.
            """}
        ],
        response_format=ArticleAnalysis,
        temperature=0.0000001  # Set an even lower temperature for more deterministic results
    )

    return completion.choices[0].message.parsed

def post_process_analysis(analysis):
    """
    Post-process the analysis to ensure consistency and determinism.
    """
    # Ensure unique stocks
    unique_stocks = {stock.ticker: stock for stock in analysis.stocks}
    analysis.stocks = list(unique_stocks.values())

    # Sort stocks alphabetically by ticker
    analysis.stocks.sort(key=lambda x: x.ticker)

    # Ensure investor types are unique and sorted
    analysis.investor_types = sorted(set(analysis.investor_types))

    return analysis
