from enum import Enum


class Task:
    # Flags for each pipeline step
    def __init__(self, name=None, description=None, status=None):
        self.name = name
        self.description = description
        self.status = status
        self.possible_subreddits = []
        self.reddit_datas = RedditDataList([])
        self.post_selection_strategy = PostSelectionStrategyEnum.MOST_UPVOTED
        self.processed_reddit_data = {}
        self.generated_reddit_data = {}
        self.generated_audio_paths = {}
        # Pipeline step flags
        self.should_find_subreddit = True
        self.should_collect_reddit_data = True
        self.should_classify = True
        self.should_rank = True
        self.should_select_post = True
        self.should_generate_text = True
        self.should_synthesize_audio = True
        self.should_select_video = False
        self.should_edit_video = False
        self.should_upload = False

    def __str__(self):
        return f"{self.name}: {self.description} - {self.status}"


class PostSelectionStrategyEnum(Enum):
    MOST_UPVOTED = "MostUpvotedPostStrategy"
    MOST_RECENT = "MostRecentPostStrategy"
    MOST_CONTROVERSIAL = "MostControversialPostStrategy"

class RedditData:
    def __init__(self, subreddit: str, data: dict):
        self.subreddit = subreddit
        self.data = data

    def __str__(self):
        return f"{self.subreddit}: {self.data}"

class RedditDataList:
    def __init__(self, reddit_datas: list[RedditData]=[]):
        self.reddit_datas = reddit_datas
        self.subreddit_to_reddit_data = {reddit_data.subreddit: reddit_data for reddit_data in reddit_datas}
    
    def add_reddit_data(self, reddit_data: RedditData):
        self.reddit_datas.append(reddit_data)
        self.subreddit_to_reddit_data[reddit_data.subreddit] = reddit_data
    
    def get_reddit_data(self, subreddit: str)->RedditData:
        return self.subreddit_to_reddit_data[subreddit]
    
    def __str__(self):
        return f"{self.reddit_datas}"

