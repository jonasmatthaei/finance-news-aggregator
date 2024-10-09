import sys
import importlib

# Remove all finnews-related modules from sys.modules
for module in list(sys.modules.keys()):
    if module.startswith('finnews'):
        del sys.modules[module]

# Now import and reload
import finnews.cnbc
importlib.reload(finnews.cnbc)
from finnews.cnbc import CNBC
import inspect

def main():
    # Create an instance of the CNBC client
    cnbc_client = CNBC()

    # Print the signature of the investing_feeds method
    print("Signature of investing_feeds method:")
    print(inspect.signature(cnbc_client.investing_feeds))

    # Print the file path of the CNBC class
    print("CNBC class defined in:", inspect.getfile(CNBC))

    # Define the technology topic
    technology_topic = 'technology'

    try:
        # Get enriched news feed for technology and save to file
        print("\nFetching enriched news feed for technology and saving to file:")
        enriched_news = cnbc_client.investing_feeds(topic=technology_topic)

        # Print the entire JSON output
        print("JSON output:")
        print(enriched_news)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Type of exception:", type(e))
        print("Exception details:", e.args)

if __name__ == "__main__":
    main()
