"""
Reddit Fashion Communities Discussion Extractor.
Targets: r/IndianFashionAddicts, r/TwoXIndia, r/delhi, r/bangalore.
Queries: "Myntra wishlist", "Myntra sizing", "Myntra return", "how to style", "worth buying".
"""

import requests
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUBREDDITS = ["IndianFashionAddicts", "TwoXIndia", "delhi", "bangalore"]
QUERIES = ["Myntra wishlist", "Myntra sizing", "Myntra return", "how to style", "worth buying"]

class RedditFashionScraper:
    def __init__(self, subreddits: List[str] = None):
        self.subreddits = subreddits or SUBREDDITS

    def fetch_discussions(self, target_count: int = 3500) -> List[Dict[str, Any]]:
        """
        Attempts to fetch public Reddit search JSON endpoints.
        """
        logger.info(f"Querying Reddit communities: {self.subreddits} (Target: {target_count})...")
        discussions = []
        try:
            for sub in self.subreddits:
                url = f"https://www.reddit.com/r/{sub}/search.json?q=Myntra&restrict_sr=1&limit=25"
                headers = {"User-Agent": "MyntraVoCResearch/1.0"}
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    children = data.get("data", {}).get("children", [])
                    for child in children:
                        post_data = child.get("data", {})
                        title = post_data.get("title", "")
                        selftext = post_data.get("selftext", "")
                        full_text = f"{title} - {selftext}".strip()
                        if len(full_text) > 20:
                            discussions.append({
                                "source": f"Reddit (r/{sub})",
                                "raw_text": full_text,
                                "upvotes": post_data.get("ups", 1),
                                "url": post_data.get("url", "")
                            })
        except Exception as e:
            logger.warning(f"Reddit live scraper encountered exception: {e}")

        logger.info(f"RedditFashionScraper finished. Fetched {len(discussions)} live records.")
        return discussions

if __name__ == "__main__":
    scraper = RedditFashionScraper()
    data = scraper.fetch_discussions(50)
    print(f"Scraped {len(data)} Reddit posts.")
