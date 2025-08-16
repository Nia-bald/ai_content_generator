import pandas as pd
from utils.units import Task
from scripts.LLM import LLMClient

class TextGenerator:
    def __init__(self):
        self.llm = LLMClient()

    def generate(self, task: Task):

        for subreddit, reddit_data in task.reddit_datas.subreddit_to_reddit_data.items():

            for post_id, post_data in reddit_data.post_data_dict.items():
                if not post_data.filtered_out:
                    title = post_data.title
                    body = post_data.selftext

                    try:
                        narration = self.llm.generate_narration(title, body, subreddit)
                    except Exception as e:
                        print(f"[TextGenerator] LLM error for r/{subreddit}: {e}")
                        narration = f"{title}. {body}"
                    post_data.narration = narration
        return task
