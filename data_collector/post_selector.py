from abc import ABC, abstractmethod
from utils.units import Task
from utils.units import PostSelectionStrategyEnum
import pandas as pd
import uuid

class PostSelector:
    """Selects posts for further processing."""
    def select(self, task: Task):
        post_selection_strategy = PostSelectionStrategyFactory().get_strategy(task)
        task = post_selection_strategy.select(task)  # Logic to select posts 
        task = self.populate_post_details(task)
        return task

    def populate_post_details(self, task: Task):
        for subreddit, reddit_data in task.processed_reddit_data.items():
            reddit_data['PostId'] = [str(uuid.uuid4()) for _ in range(len(reddit_data))]
            reddit_data['Tags'] = ""
            reddit_data['Description'] = ""
            task.processed_reddit_data[subreddit] = reddit_data
        return task

class PostSelectionStrategy(ABC):

    @abstractmethod
    def select(self, task: Task):
        return task

class MostUpvotedPostStrategy(PostSelectionStrategy):
    def select(self, task: Task):
        subreddit_to_reddit_data_list = {}
        for subreddit, reddit_data in task.reddit_datas.subreddit_to_reddit_data.items():
            data = reddit_data.data
            reddit_data_list = [row.get('data') for row in data['data'].get('children')]
            reddit_data_df = pd.DataFrame(reddit_data_list)
            # TODO: these top_x values should come from config ans should be diff for each individual subreddit
            top_10_posts = reddit_data_df.sort_values(by='ups', ascending=False).head(10)
            subreddit_to_reddit_data_list[subreddit] = top_10_posts
        task.processed_reddit_data = subreddit_to_reddit_data_list
        return task


class MostRecentPostStrategy(PostSelectionStrategy):
    def select(self, task: Task):
        return task


class MostControversialPostStrategy(PostSelectionStrategy):
    def select(self, task: Task):
        return task

class PostSelectionStrategyFactory:
    def get_strategy(self, task: Task)->PostSelectionStrategy:
        if task.post_selection_strategy == PostSelectionStrategyEnum.MOST_UPVOTED:
            return MostUpvotedPostStrategy()
        elif task.post_selection_strategy == PostSelectionStrategyEnum.MOST_RECENT:
            return MostRecentPostStrategy()
        elif task.post_selection_strategy == PostSelectionStrategyEnum.MOST_CONTROVERSIAL:
            return MostControversialPostStrategy()
        else:
            raise ValueError(f"Invalid post selection strategy: {task.post_selection_strategy}")