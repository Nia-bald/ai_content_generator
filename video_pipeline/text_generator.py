import pandas as pd
from scripts.LLM import LLMClient

class TextGenerator:
    def __init__(self):
        self.llm = LLMClient()

    def generate(self, task):
        generated_data = {}

        for subreddit, df in task.processed_reddit_data.items():
            if df.empty:
                continue

            narrations = []
            for _, row in df.iterrows():
                title = row.get("title", "").strip()
                body = row.get("selftext", "").strip()

                try:
                    narration = self.llm.generate_narration(title, body, subreddit)
                except Exception as e:
                    print(f"[TextGenerator] LLM error for r/{subreddit}: {e}")
                    narration = f"{title}. {body}"

                narrations.append(narration)

            generated_data[subreddit] = narrations
            print(f"[TextGenerator] Generated {len(narrations)} narrations for r/{subreddit}")

        task.generated_reddit_data = generated_data
        return task
