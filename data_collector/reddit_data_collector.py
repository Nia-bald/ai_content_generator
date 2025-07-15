from utils.units import Task, RedditData, RedditDataList
import requests

class RedditDataCollector:
    def __init__(self):
        self.reddit_base_url = "https://www.reddit.com"
    """Collects data from Reddit based on subreddits."""
    def collect(self, task: Task):
        reddit_data_list = RedditDataList([])
        for subreddit in task.possible_subreddits:
            url = f"{self.reddit_base_url}/r/{subreddit}/hot.json?limit=100"
            response = requests.get(url)
            data = response.json()
            reddit_data_list.add_reddit_data(RedditData(subreddit, data))
        task.reddit_datas = reddit_data_list
        return task  # Logic to collect data from Reddit
    