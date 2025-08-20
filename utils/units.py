from enum import Enum
from pydantic import BaseModel
import pandas as pd
import logging
logger = logging.getLogger(__name__)


class Task:
    # Flags for each pipeline step
    def __init__(self, name=None, description=None, status=None):
        self.name = name
        self.description = description
        self.status = status
        self.possible_subreddits = []
        self.reddit_datas = RedditDataList([])
        self.post_selection_strategy = PostSelectionStrategyEnum.MOST_UPVOTED
        # Pipeline step flags
        self.should_find_subreddit = True
        self.should_collect_reddit_data = True
        self.should_classify = True
        self.should_rank = True
        self.should_select_post = True
        self.should_generate_text = True
        self.should_synthesize_audio = True
        self.should_select_video = True
        self.should_edit_video = True
        self.should_upload = False
        self.save_to_db = True
        self.success = None

    def __str__(self):
        return f"{self.name}: {self.description} - {self.status}"
    

class PostSelectionStrategyEnum(Enum):
    MOST_UPVOTED = "MostUpvotedPostStrategy"
    MOST_RECENT = "MostRecentPostStrategy"
    MOST_CONTROVERSIAL = "MostControversialPostStrategy"

class PostData(BaseModel):
    id: str
    title: str
    selftext: str
    subreddit: str
    ups: int = None
    score: int = None
    num_comments: int = None
    created_utc: float = None
    author_fullname: str = None
    author: str = None
    permalink: str = None
    upvote_ratio: float = None
    is_self: bool = None
    over_18: bool = None
    spoiler: bool = None
    filtered_out: bool = True
    narration: str = None
    synthesized_audio_file_path: str = None
    video_file_path: str = None
    final_video_path: str = None

    def __str__(self):
        return f"{self.id}: {self.title} - {self.selftext} - {self.subreddit}"


class RedditData:
    def __init__(self, subreddit: str, data: dict, distinct_available_post_ids:set):
        self.subreddit = subreddit
        self.data = data
        # Complete: create a dict mapping post_id to post_data for all posts in the subreddit data
        self.post_data_dict = {}
        for post_data in data.get("data", {}).get("children", []):
            post_id = post_data.get("data", {}).get("id")
            if post_id is None:
                continue
            if post_id in distinct_available_post_ids:
                logger.info(f"Post id {post_id} already processed, skipping.")
                continue
            self.post_data_dict[post_id] = PostData(**post_data.get("data"))

    def __str__(self):
        return f"{self.subreddit}: {self.data}"
    
    def get_unfiltered_data(self):
        return self.post_data_dict
    
    def get_all_posts(self, filter_out=True):
        return [post for post in list(self.post_data_dict.values()) if filter_out and not post.filtered_out]

    def to_pandas_dataframe(self, filter_out = True):
        """
        Converts the RedditData's posts into a pandas DataFrame.
        Each row corresponds to a post, with columns for all PostData attributes.
        """

        rows = []
        for post_id, post_data in self.post_data_dict.items():
            if filter_out and post_data.filtered_out == True:
                continue
            row = post_data.dict()
            rows.append(row)
        return pd.DataFrame(rows)

class RedditDataList:
    def __init__(self, reddit_datas: list[RedditData]=[]):
        self.reddit_datas = reddit_datas
        self.subreddit_to_reddit_data: dict[str, RedditData] = {reddit_data.subreddit: reddit_data for reddit_data in reddit_datas}
    
    def add_reddit_data(self, reddit_data: RedditData):
        self.reddit_datas.append(reddit_data)
        self.subreddit_to_reddit_data[reddit_data.subreddit] = reddit_data
    
    def get_reddit_data(self, subreddit: str)->RedditData:
        return self.subreddit_to_reddit_data[subreddit]
    
    def get_all_posts(self, filter_out=True)-> list[PostData]:
        posts = []
        for subreddit, reddit_datas in self.subreddit_to_reddit_data.items():
            posts.extend(reddit_datas.get_all_posts(filter_out=filter_out))
        return posts

    def __str__(self):
        return f"{self.reddit_datas}"

