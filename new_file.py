from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# Load file example.mp4 and keep only the subclip from 00:00:10 to 00:00:20
# Reduce the audio volume to 80% of its original volume

clip = (
    VideoFileClip("videos/edit_subway_surfers_.mp4")
    .subclipped(0.1, 3)
    .with_volume_scaled(0.8)
)

# Generate a text clip. You can customize the font, color, etc.
txt_clip = TextClip(
    text="Hello there!",
    font_size=70,
    color='white'
).with_duration(10).with_position('center')

# Overlay the text clip on the first video clip
final_video = CompositeVideoClip([clip, txt_clip])
final_video.write_videofile("result.mp4")
