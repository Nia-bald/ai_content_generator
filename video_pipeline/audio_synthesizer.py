from scripts.LLM import LLMClient
import os
from utils.units import Task

class AudioSynthesizer:
    """Synthesizes audio from generated text."""
    def __init__(self, output_dir="generated_audio"):
        self.llm = LLMClient()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def synthesize(self, task: Task):
        if not hasattr(task, "generated_reddit_data") or not task.generated_reddit_data:
            print("[AudioSynthesizer] No generated text found in task.")
            return task

        for subreddit, reddit_data in task.reddit_datas.subreddit_to_reddit_data.items():
            subreddit_dir = os.path.join(self.output_dir, subreddit)
            os.makedirs(subreddit_dir, exist_ok=True)
            for post_id, post_data in reddit_data.post_data_dict.items():
                if not post_data.filtered_out:
                    file_path = os.path.join(subreddit_dir, f"post_{post_id}_{task.name}.mp3")
                    try:
                        self.llm.synthesize_speech(post_data.narration, file_path)
                        print(f"[AudioSynthesizer] Audio saved: {file_path}")
                    except Exception as e:
                        print(f"[AudioSynthesizer] Error generating audio for r/{subreddit} post {post_id}: {e}")
                    post_data.synthesized_audio_file_path = file_path

        return task
