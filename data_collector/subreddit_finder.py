from utils.units import Task

class SubredditFinder:
    """Finds relevant subreddits for data collection."""
    def find(self, task: Task):
        task.possible_subreddits = ["AmItheAsshole"]
        return task  # Logic to find subreddits 