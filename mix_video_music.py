import os
import shutil
import imageio_ffmpeg
import subprocess
from google.cloud import storage
import google.auth

PROJECT_ID = "qwiklabs-gcp-03-42373a35b923"
BUCKET_NAME = "fitcoach-ai-media-qwiklabs-gcp-03-42373a35b923"

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

src_video = "/config/.gemini/antigravity/scratch/fitcoach-ai/frontend/static/demo_video.webm"
src_audio = "/tmp/lofi_background.wav"
output_video_local = "/config/.gemini/antigravity/scratch/fitcoach-ai/frontend/static/demo_video_lofi.mp4"
output_artifact = "/config/.gemini/antigravity/brain/9aeb28e7-f7de-4508-a065-80f5b229394c/demo_video_lofi.mp4"

cmd = [
    ffmpeg_exe,
    "-y",
    "-i", src_video,
    "-i", src_audio,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    output_video_local
]

print("Running FFmpeg audio-video mix command...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFmpeg exit code:", res.returncode)
if res.returncode != 0:
    print("FFmpeg stderr:", res.stderr)
else:
    print(f"Successfully created mixed video at {output_video_local}")
    shutil.copyfile(output_video_local, output_artifact)

    # Upload to public GCS bucket
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    storage_client = storage.Client(project=PROJECT_ID, credentials=credentials)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("demo_video_lofi.mp4")
    blob.upload_from_filename(output_video_local, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/demo_video_lofi.mp4"
    print(f"Public Demo Video with Lo-Fi Music URL: {public_url}")
