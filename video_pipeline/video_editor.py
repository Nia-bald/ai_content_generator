from turtle import position
from utils.units import Task, PostData
from scripts.LLM import LLMClient
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_editor.log'),
        logging.StreamHandler()
    ]
)

class VideoEditor:
    """Edits video clips and synchronizes with audio."""
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing VideoEditor")
        self.llm = LLMClient()
        self.output_parent_path = "media/final_output"
        if not os.path.exists(self.output_parent_path):
            self.logger.info(f"Creating output directory: {self.output_parent_path}")
            os.makedirs(self.output_parent_path)
        else:
            self.logger.info(f"Output directory already exists: {self.output_parent_path}")

    def edit(self, task: Task):
        self.logger.info(f"Starting video editing for task with {len(task.reddit_datas.get_all_posts())} posts")

        post_datas = task.reddit_datas.get_all_posts()
        results = {}

        self.logger.info(f"Processing {len(post_datas)} posts using ProcessPoolExecutor")

        # For each post, generate the final video by calling generate_video, and store the result (True/False) in results[post_id]
        for post_data in post_datas:
            try:
                result = self.generate_video(post_data)
                results[post_data.id] = result
            except Exception as e:
                self.logger.error(f"Error editing video for post {post_data.id}: {e}")
                results[post_data.id] = False

        # Set task.success based on all results (True if all succeeded, else False)
        task.success = all(results.values()) if results else False
        success_count = sum(results.values())
        total_count = len(results)
        self.logger.info(f"Video editing completed. Success: {success_count}/{total_count} posts")
        self.logger.info(f"Overall task success: {task.success}")
        return task   
    
    def generate_video(self, post_data:PostData):
        self.logger.info(f"Starting video generation for post {post_data.id}")
        try:
            video_path = post_data.video_file_path
            audio_path = post_data.synthesized_audio_file_path
            output_path = os.path.join(self.output_parent_path, f"post_id_{post_data.id}_final.mp4")

            self.logger.info(f"Post {post_data.id}: Video path: {video_path}")
            self.logger.info(f"Post {post_data.id}: Audio path: {audio_path}")
            self.logger.info(f"Post {post_data.id}: Output path: {output_path}")

            # Check if input files exist
            if not os.path.exists(video_path):
                self.logger.error(f"Post {post_data.id}: Video file not found: {video_path}")
                return False
            if not os.path.exists(audio_path):
                self.logger.error(f"Post {post_data.id}: Audio file not found: {audio_path}")
                return False

            self.logger.info(f"Post {post_data.id}: Generating transcription")
            transcription = self.generate_transcription(audio_path)
            self.logger.info(f"Post {post_data.id}: Transcription completed with {len(transcription.words)} words")

            # Load video and cut to first 10 seconds
            self.logger.info(f"Post {post_data.id}: Loading video file")
            video = VideoFileClip(video_path, audio=False)
            video_duration = video.duration
            self.logger.info(f"Post {post_data.id}: Video loaded, duration: {video_duration}s")

            self.logger.info(f"Post {post_data.id}: Loading audio file")
            new_audio = AudioFileClip(audio_path)
            audio_duration = new_audio.duration
            self.logger.info(f"Post {post_data.id}: Audio loaded, duration: {audio_duration}s")

            min_duration = min(transcription.duration, video_duration, audio_duration)
            self.logger.info(f"Post {post_data.id}: Using minimum duration: {min_duration}s")

            video = video.subclipped(0, min_duration)
            new_audio = new_audio.subclipped(0, min_duration)

            composite_video_list = [video]
            self.logger.info(f"Post {post_data.id}: Creating text overlays for {len(transcription.words)} words")
            
            for i, word in enumerate(transcription.words):
                if i % 50 == 0:  # Log progress every 50 words
                    self.logger.info(f"Post {post_data.id}: Processing word {i+1}/{len(transcription.words)}")
                
                composite_video_list.append(
                    TextClip(
                        text=word.word,
                        font_size=70,
                        color='white',
                        size=video.size
                    ).with_position('center').with_start(word.start).with_duration(word.end - word.start)
                )

            self.logger.info(f"Post {post_data.id}: Creating composite video")
            final = CompositeVideoClip(composite_video_list).with_audio(new_audio)

            # Write the result
            self.logger.info(f"Post {post_data.id}: Writing final video to {output_path}")
            final.write_videofile(output_path)
            self.logger.info(f"Post {post_data.id}: Video generation completed successfully")

            return True

        except Exception as e:
            self.logger.error(f"Post {post_data.id}: Error during video generation: {str(e)}", exc_info=True)
            return False
    
    def generate_transcription(self, audio_path):
        self.logger.info(f"Generating transcription for audio: {audio_path}")
        try:
            transcription = self.llm.client.audio.transcriptions.create(
                    file=open(audio_path, "rb"),
                    model="whisper-1",
                    response_format="verbose_json",  # or "vtt" for web captions
                    timestamp_granularities=["word"]
                )
            self.logger.info(f"Transcription completed successfully")
            return transcription
        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}", exc_info=True)
            raise
