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
        return task

class PostSelectionStrategy(ABC):

    @abstractmethod
    def select(self, task: Task):
        return task

class MostUpvotedPostStrategy(PostSelectionStrategy):
    def select(self, task: Task):
        for subreddit, reddit_data in task.reddit_datas.subreddit_to_reddit_data.items():
            pandas_data = reddit_data.to_pandas_dataframe(filter_out=False)
            # TODO: these top_x values should come from config ans should be diff for each individual subreddit
            top_10_posts = pandas_data.sort_values(by='ups', ascending=False).head(3)
            top_10_post_id = list(top_10_posts['id'].values)
            for post_id in top_10_post_id:
                reddit_data.post_data_dict.get(post_id).filtered_out = False
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