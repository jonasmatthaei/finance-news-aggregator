from finnews.yahoo_finance import YahooFinance

def main():
    # Create an instance of the CNBC client
    yahoo_client = YahooFinance()

    # Define the technology topic
    technology_topic = 'technology'  # Ensure this matches the key in your cnbc_rss_feeds_id dictionary

    # Get enriched news feed for technology and save to file
    print("\nFetching enriched news feed for technology and saving to file:")
    news = yahoo_client.investing_feeds(topic='news', save_to_file=True, max_articles=5)

    # Print the first few characters of the JSON output
    print("First 500 characters of the JSON output:")
    print(news[:500])

if __name__ == "__main__":
    main()
