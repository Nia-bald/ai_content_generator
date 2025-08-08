from scripts.LLM import LLMClient
import os

class AudioSynthesizer:
    """Synthesizes audio from generated text."""
    def __init__(self, output_dir="generated_audio"):
        self.llm = LLMClient()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def synthesize(self, task):
        if not hasattr(task, "generated_reddit_data") or not task.generated_reddit_data:
            print("[AudioSynthesizer] No generated text found in task.")
            return task

        audio_paths = {}
        for subreddit, narrations in task.generated_reddit_data.items():
            subreddit_dir = os.path.join(self.output_dir, subreddit)
            os.makedirs(subreddit_dir, exist_ok=True)

            paths = []
            for idx, narration in enumerate(narrations, start=1):
                file_path = os.path.join(subreddit_dir, f"post_{idx}.mp3")
                try:
                    self.llm.synthesize_speech(narration, file_path)
                    print(f"[AudioSynthesizer] Audio saved: {file_path}")
                    paths.append(file_path)
                except Exception as e:
                    print(f"[AudioSynthesizer] Error generating audio for r/{subreddit} post {idx}: {e}")

            audio_paths[subreddit] = paths

        task.generated_audio_paths = audio_paths
        return task
