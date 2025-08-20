from pipeline import VideoGenerationPipeline
from utils.units import Task, PostSelectionStrategyEnum

if __name__ == "__main__":
    task_list = [Task('example_task', 'This is an example task', 'pending')]
    pipeline = VideoGenerationPipeline()
    pipeline.run(task_list) 