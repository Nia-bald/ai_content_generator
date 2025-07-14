class Task:
    # Flags for each pipeline step
    def __init__(self, name=None, description=None, status=None):
        self.name = name
        self.description = description
        self.status = status
        self.possible_subreddits = []
        self.reddit_datas = []

        # Pipeline step flags
        self.should_find_subreddit = False
        self.should_collect_reddit_data = False
        self.should_classify = False
        self.should_rank = False
        self.should_select_post = False
        self.should_generate_text = False
        self.should_synthesize_audio = False
        self.should_select_video = False
        self.should_edit_video = False
        self.should_upload = False

    def __str__(self):
        return f"{self.name}: {self.description} - {self.status}"


class RedditData:
    def __init__(self, subreddit: str, data: dict):
        self.subreddit = subreddit
        self.data = data

    def __str__(self):
        return f"{self.subreddit}: {self.data}"