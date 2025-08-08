from abc import ABC, abstractmethod
from utils.units import Task

class RankingAlgorithm:
    """Ranks classified posts for selection."""
    def rank(self, task: Task):

        # for subreddit, processed_reddit_data in task.processed_reddit_data.items():
        #     processed_reddit_data['rank'] = range(1, len(processed_reddit_data) + 1)
        #     task.processed_reddit_data[subreddit] = processed_reddit_data
        return task  # Logic to rank posts
