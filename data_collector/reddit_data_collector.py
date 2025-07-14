from utils.units import Task, RedditData
import requests

class RedditDataCollector:
    def __init__(self):
        self.reddit_base_url = "https://www.reddit.com"
    """Collects data from Reddit based on subreddits."""
    def collect(self, task: Task):
        for subreddit in task.possible_subreddits:
            url = f"{self.reddit_base_url}/r/{subreddit}/top.json?limit=100"
            response = requests.get(url)
            data = response.json()
            task.reddit_datas.append(RedditData(subreddit, data))
        return task  # Logic to collect data from Reddit
    