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

# Main pipeline orchestrator
class VideoGenerationPipeline:
    def __init__(self):
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

    def run(self, task_list: list[Task]):

        # Example pipeline flow (details to be filled in)
        for task in task_list:
            
            if getattr(task, "should_find_subreddit", False):
                task = self.subreddit_finder.find(task)
            if getattr(task, "should_collect_reddit_data", False):
                task = self.reddit_collector.collect(task)
            if getattr(task, "should_classify", False):
                task = self.classifier.classify(task)
            if getattr(task, "should_rank", False):
                task = self.ranker.rank(task)
            if getattr(task, "should_select_post", False):
                task = self.post_selector.select(task)
            if getattr(task, "should_generate_text", False):
                task = self.text_generator.generate(task)
            if getattr(task, "should_synthesize_audio", False):
                task = self.audio_synth.synthesize(task)
            if getattr(task, "should_select_video", False):
                task = self.video_selector.select_video(task)
            if getattr(task, "should_edit_video", False):
                task = self.video_editor.edit(task)
            if getattr(task, "should_upload", False):
                task = self.uploader.upload(task)
        # Channel finder and downloader can be integrated as needed

