import asyncio
import os
import shutil
import time
from playwright.async_api import async_playwright
from google.cloud import storage
import google.auth

PROJECT_ID = "qwiklabs-gcp-03-42373a35b923"
BUCKET_NAME = "fitcoach-ai-media-qwiklabs-gcp-03-42373a35b923"
URL = "https://fitcoach-ai-frontend-744804734982.us-east1.run.app"
RECORD_DIR = "/tmp/demo_video"

async def record_demo():
    if os.path.exists(RECORD_DIR):
        shutil.rmtree(RECORD_DIR)
    os.makedirs(RECORD_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=RECORD_DIR,
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print(f"Navigating to {URL}...")
        await page.goto(URL, wait_until="networkidle")
        await asyncio.sleep(2)

        # 1. First prompt: Show app doing what it does best (HIIT Workout routine)
        print("Sending Prompt 1...")
        input_el = page.locator("#input")
        await input_el.fill("Suggest a 20-minute HIIT workout routine for weight loss.")
        await asyncio.sleep(1)
        await page.click("button:has-text('Send')")
        
        # Wait for agent response
        print("Waiting for response 1...")
        await asyncio.sleep(10)

        # 2. Second, richer prompt: Tool calls (Visual diagram, HR training zones, Nearby gyms)
        print("Sending Prompt 2...")
        await input_el.fill("Generate a workout diagram visual for a Barbell Back Squat, calculate my heart rate training zones for age 30, and find nearby gyms in San Francisco.")
        await asyncio.sleep(1)
        await page.click("button:has-text('Send')")

        # Wait for multi-tool execution and rendering
        print("Waiting for response 2 (multi-tool execution)...")
        await asyncio.sleep(18)

        # Scroll to view results smoothly
        await page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        await asyncio.sleep(3)

        await page.close()
        await context.close()
        await browser.close()

    # Find recorded video file
    video_files = [f for f in os.listdir(RECORD_DIR) if f.endswith(".webm") or f.endswith(".mp4")]
    if not video_files:
        print("Error: No video file was generated!")
        return

    src_video = os.path.join(RECORD_DIR, video_files[0])
    target_video = "/config/.gemini/antigravity/scratch/fitcoach-ai/frontend/static/demo_video.webm"
    shutil.copyfile(src_video, target_video)
    print(f"Saved demo video locally to {target_video}")

    # Upload video to GCS
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    storage_client = storage.Client(project=PROJECT_ID, credentials=credentials)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("demo_video.webm")
    blob.upload_from_filename(target_video, content_type="video/webm")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/demo_video.webm"
    print(f"Public Demo Video URL: {public_url}")

if __name__ == "__main__":
    asyncio.run(record_demo())
