from utils.units import Task, RedditData, RedditDataList
import requests
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_collector.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class RedditDataCollector:
    def __init__(self):
        self.reddit_base_url = "https://www.reddit.com"
        self.max_retries = 3
        self.base_delay = 1  # Base delay in seconds
        logger.info("RedditDataCollector initialized")
    
    def _make_reddit_request(self, url: str) -> Dict[str, Any]:
        """
        Make a request to Reddit API with retry logic and exponential backoff.
        
        Args:
            url: The Reddit API URL to request
            
        Returns:
            Dict containing the JSON response data
            
        Raises:
            requests.RequestException: If all retries are exhausted
        """
        logger.debug(f"Making request to: {url}")
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_retries}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()  # Raise an exception for bad status codes
                logger.debug(f"Request successful on attempt {attempt + 1}")
                return response.json()
            except (requests.RequestException, requests.Timeout) as e:
                logger.warning(f"Request failed on attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt == self.max_retries - 1:  # Last attempt
                    logger.error(f"All retry attempts exhausted for URL: {url}")
                    raise e
                
                # Calculate delay with exponential backoff
                delay = self.base_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    """Collects data from Reddit based on subreddits."""
    def collect(self, task: Task):
        logger.info(f"Starting data collection for task with {len(task.possible_subreddits)} subreddits")
        reddit_data_list = RedditDataList([])
        
        for i, subreddit in enumerate(task.possible_subreddits, 1):
            logger.info(f"Processing subreddit {i}/{len(task.possible_subreddits)}: r/{subreddit}")
            url = f"{self.reddit_base_url}/r/{subreddit}/hot.json?limit=50"
            try:
                data = self._make_reddit_request(url)
                reddit_data_list.add_reddit_data(RedditData(subreddit, data))
                logger.info(f"Successfully collected data from r/{subreddit}")
            except requests.RequestException as e:
                logger.error(f"Failed to collect data from r/{subreddit}: {e}")
                continue  # Skip this subreddit and continue with others
        
        task.reddit_datas = reddit_data_list
        logger.info(f"Data collection completed. Collected data from {len(reddit_data_list.reddit_datas)} subreddits")
        return task  # Logic to collect data from Reddit
    

    #redditdatalist will have [ ds1, ds2, ds3 ,......]
    # reddit data list has these:
    """ 1. redditdatas  has subreddit and data
        2. subredtit to redit data : : has key as subreddit and data as redditdatas
    """