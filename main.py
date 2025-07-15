from pipeline import VideoGenerationPipeline
from utils.units import Task, PostSelectionStrategyEnum

if __name__ == "__main__":
    task_list = [Task()]
    pipeline = VideoGenerationPipeline()
    pipeline.run(task_list) 