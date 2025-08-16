from data_collector.subreddit_finder import SubredditFinder
from data_collector.reddit_data_collector import RedditDataCollector
from data_collector.classification_algorithm import ClassificationAlgorithm
from data_collector.post_selector import PostSelector
from data_collector.channel_finder import ChannelFinder
from data_collector.ranking_algorithm import RankingAlgorithm

from video_pipeline.text_generator import TextGenerator
from video_pipeline.audio_synthesizer import AudioSynthesizer
from video_pipeline.video_selection_algorithm import VideoSelectionAlgorithm
from video_pipeline.video_editor import VideoEditor
from video_pipeline.video_uploader import VideoUploader
from video_pipeline.video_downloader import VideoDownloader

from utils.units import Task
from utils.data_base import LocalDatabase
import uuid

# Main pipeline orchestrator
class VideoGenerationPipeline:
    def __init__(self, db_path: str = 'database.db'):
        self.subreddit_finder = SubredditFinder()
        self.reddit_collector = RedditDataCollector()
        self.classifier = ClassificationAlgorithm()
        self.ranker = RankingAlgorithm()
        self.post_selector = PostSelector()
        self.text_generator = TextGenerator()
        self.audio_synth = AudioSynthesizer()
        self.video_selector = VideoSelectionAlgorithm()
        self.video_editor = VideoEditor()
        self.uploader = VideoUploader()
        self.channel_finder = ChannelFinder()
        self.video_downloader = VideoDownloader()
        self.db = LocalDatabase(db_path)

    def run(self, task_list: list[Task]):

        # Example pipeline flow (details to be filled in)
        for task in task_list:
            
            if task.should_find_subreddit == True:
                task = self.subreddit_finder.find(task)
            if task.should_collect_reddit_data == True:
                task = self.reddit_collector.collect(task)
            if task.should_classify == True:
                task = self.classifier.classify(task)
            if task.should_rank == True:
                task = self.ranker.rank(task)
            if task.should_select_post == True:
                task = self.post_selector.select(task)
                self.save_to_db(task)
            if task.should_generate_text == True:
                task = self.text_generator.generate(task)
            if task.should_synthesize_audio == True:
                task = self.audio_synth.synthesize(task)
            if task.should_select_video == True:
                task = self.video_selector.select_video(task)
            if task.should_edit_video == True:
                task = self.video_editor.edit(task)
            if task.should_upload == True:
                task = self.uploader.upload(task)
        # Channel finder and downloader can be integrated as needed

    def save_to_db(self, task: Task):
        db = self.db
        for subreddit_name, reddit_data in task.reddit_datas.subreddit_to_reddit_data.items():
            pandas_data = reddit_data.to_pandas_dataframe()
            op_details = []
            for ix, row in pandas_data.iterrows():
                op_details.append({
                    'OpName': row['author'],
                    'OpFollowers': None # TODO: get followers from reddit api
                })
            db.execute_insert('OpInfo', op_details)

            content_details = []
            for ix, row in pandas_data.iterrows():
                content_details.append({
                    'PostId': row['id'],
                    'Content': row['selftext'],
                    'Type': None, # TODO: get type from reddit api
                    'MediaPath': None, # TODO: get media path from reddit api
                    'SubredditName': subreddit_name,
                    'Rank': None,
                    'RankingAlgorithm': None,
                    'EngagmentTableId': None,
                    'OpInfoId': row['author'],
                    'PostProductionTableId': None
                })
            db.execute_insert('RedditPostTable', content_details)
        db.close()
        return task
