from enum import Enum
import pandas as pd


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
        self.success = None

    def __str__(self):
        return f"{self.name}: {self.description} - {self.status}"
    

class PostSelectionStrategyEnum(Enum):
    MOST_UPVOTED = "MostUpvotedPostStrategy"
    MOST_RECENT = "MostRecentPostStrategy"
    MOST_CONTROVERSIAL = "MostControversialPostStrategy"

class PostData:
    def __init__(
        self,
        id: str,
        title: str,
        selftext: str,
        subreddit: str,
        ups=None,
        score=None,
        num_comments=None,
        created_utc=None,
        author_fullname=None,
        author=None,
        permalink=None,
        upvote_ratio=None,
        is_self=None,
        over_18=None,
        spoiler=None,
        **kwargs
    ):
        self.id = id
        self.title = title
        self.selftext = selftext
        self.subreddit = subreddit
        self.ups = ups
        self.score = score
        self.num_comments = num_comments
        self.created_utc = created_utc
        self.author_fullname = author_fullname
        self.author = author
        self.permalink = permalink
        self.upvote_ratio = upvote_ratio
        self.is_self = is_self
        self.over_18 = over_18
        self.spoiler = spoiler
        self.filtered_out = True
        self.narration = None
        self.synthesized_audio_file_path = None
        self.video_file_path = None
    
    def __str__(self):
        return f"{self.id}: {self.title} - {self.selftext} - {self.subreddit}"


class RedditData:
    def __init__(self, subreddit: str, data: dict):
        self.subreddit = subreddit
        self.data = data
        # Complete: create a dict mapping post_id to post_data for all posts in the subreddit data
        self.post_data_dict = {
            post_data.get("data", {}).get("id"): PostData(**post_data.get("data"))
            for post_data in data.get("data", {}).get("children", [])
            if post_data.get("data", {}).get("id") is not None
        }

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
            row = {
                "id": post_data.id,
                "title": post_data.title,
                "selftext": post_data.selftext,
                "subreddit": post_data.subreddit,
                "ups": post_data.ups,
                "score": post_data.score,
                "num_comments": post_data.num_comments,
                "created_utc": post_data.created_utc,
                "author_fullname": post_data.author_fullname,
                "author": post_data.author,
                "permalink": post_data.permalink,
                "upvote_ratio": post_data.upvote_ratio,
                "is_self": post_data.is_self,
                "over_18": post_data.over_18,
                "spoiler": post_data.spoiler,
            }
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

