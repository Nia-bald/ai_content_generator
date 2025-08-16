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
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Main pipeline orchestrator
class VideoGenerationPipeline:
    def __init__(self, db_path: str = 'database.db'):
        logger.info("Initializing VideoGenerationPipeline")
        try:
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
            logger.info("All pipeline components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline components: {str(e)}")
            raise

    def run(self, task_list: list[Task]):
        logger.info(f"Starting pipeline execution with {len(task_list)} tasks")
        start_time = time.time()
        
        successful_tasks = 0
        failed_tasks = 0

        # Example pipeline flow (details to be filled in)
        for i, task in enumerate(task_list, 1):
            task_start_time = time.time()
            logger.info(f"Processing task {i}/{len(task_list)}: {task.__class__.__name__}")
            
            try:
                if task.should_find_subreddit == True:
                    logger.info(f"Task {i}: Finding subreddit")
                    task = self.subreddit_finder.find(task)
                    logger.info(f"Task {i}: Subreddit finding completed")
                    
                if task.should_collect_reddit_data == True:
                    logger.info(f"Task {i}: Collecting Reddit data")
                    task = self.reddit_collector.collect(task)
                    logger.info(f"Task {i}: Reddit data collection completed")
                    
                if task.should_classify == True:
                    logger.info(f"Task {i}: Classifying content")
                    task = self.classifier.classify(task)
                    logger.info(f"Task {i}: Classification completed")
                    
                if task.should_rank == True:
                    logger.info(f"Task {i}: Ranking content")
                    task = self.ranker.rank(task)
                    logger.info(f"Task {i}: Ranking completed")
                    
                if task.should_select_post == True:
                    logger.info(f"Task {i}: Selecting post")
                    task = self.post_selector.select(task)
                    logger.info(f"Task {i}: Post selection completed")
                    self.save_to_db(task)
                    logger.info(f"Task {i}: Data saved to database")
                    
                if task.should_generate_text == True:
                    logger.info(f"Task {i}: Generating text")
                    task = self.text_generator.generate(task)
                    logger.info(f"Task {i}: Text generation completed")
                    
                if task.should_synthesize_audio == True:
                    logger.info(f"Task {i}: Synthesizing audio")
                    task = self.audio_synth.synthesize(task)
                    logger.info(f"Task {i}: Audio synthesis completed")
                    
                if task.should_select_video == True:
                    logger.info(f"Task {i}: Selecting video")
                    task = self.video_selector.select_video(task)
                    logger.info(f"Task {i}: Video selection completed")
                    
                if task.should_edit_video == True:
                    logger.info(f"Task {i}: Editing video")
                    task = self.video_editor.edit(task)
                    logger.info(f"Task {i}: Video editing completed")
                    
                if task.should_upload == True:
                    logger.info(f"Task {i}: Uploading video")
                    task = self.uploader.upload(task)
                    logger.info(f"Task {i}: Video upload completed")
                    
                task_duration = time.time() - task_start_time
                logger.info(f"Task {i} completed successfully in {task_duration:.2f} seconds")
                successful_tasks += 1
                
            except Exception as e:
                task_duration = time.time() - task_start_time
                logger.error(f"Task {i} failed after {task_duration:.2f} seconds: {str(e)}")
                failed_tasks += 1
                continue
                
        total_duration = time.time() - start_time
        logger.info(f"Pipeline execution completed in {total_duration:.2f} seconds")
        logger.info(f"Results: {successful_tasks} successful, {failed_tasks} failed out of {len(task_list)} total tasks")
        
        # Channel finder and downloader can be integrated as needed

    def save_to_db(self, task: Task):
        logger.info("Starting database save operation")
        start_time = time.time()
        
        try:
            db = self.db
            total_posts = 0
            
            for subreddit_name, reddit_data in task.reddit_datas.subreddit_to_reddit_data.items():
                logger.info(f"Processing data for subreddit: {subreddit_name}")
                pandas_data = reddit_data.to_pandas_dataframe()
                
                # Process OpInfo
                op_details = []
                for ix, row in pandas_data.iterrows():
                    op_details.append({
                        'OpInfoId': row['author_fullname'],
                        'OpName': row['author'],
                        'OpFollowers': None # TODO: get followers from reddit api
                    })
                
                logger.info(f"Inserting {len(op_details)} OpInfo records for subreddit {subreddit_name}")
                db.execute_insert('OpInfo', op_details)

                # Process RedditPostTable
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
                
                logger.info(f"Inserting {len(content_details)} RedditPostTable records for subreddit {subreddit_name}")
                db.execute_insert('RedditPostTable', content_details)
                total_posts += len(content_details)
            
            db.close()
            save_duration = time.time() - start_time
            logger.info(f"Database save completed successfully in {save_duration:.2f} seconds. Total posts saved: {total_posts}")
            
        except Exception as e:
            save_duration = time.time() - start_time
            logger.error(f"Database save failed after {save_duration:.2f} seconds: {str(e)}")
            raise
            
        return task
