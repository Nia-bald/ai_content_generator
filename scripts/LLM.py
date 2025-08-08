import os
from dotenv import load_dotenv
import openai

load_dotenv()

class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment.")
        self.client = openai.OpenAI(api_key=api_key)

    # General-purpose chat completion
    def chat(self, system_prompt: str, user_prompt: str, model: str = "gpt-3.5-turbo") -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    # Generate narration specifically for Reddit post
    def generate_narration(self, title: str, body: str, subreddit: str) -> str:
        prompt = (
            f"Rewrite the following Reddit post to be used directly in a YouTube Shorts voiceover. "
            f"Start with a hook and make it flow like natural speech. No titles, no subreddit mention, no intro text. "
            f"Just return the final script:\n\n"
            f"Title: {title}\n\n"
            f"Body:\n{body}"
        )

        return self.chat(
            system_prompt="You are a YouTube Shorts scriptwriter. Your output will be used directly for AI voiceover.",
            user_prompt=prompt
        )

        
    # Embedding generation 
    def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> list[float]:
        response = self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding

    # Text-to-speech (TTS)
    def synthesize_speech(self, text: str, output_path: str, voice: str = "onyx", model: str = "tts-1"):
        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )
        response.stream_to_file(output_path)
        return output_path
