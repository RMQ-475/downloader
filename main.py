from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
import yt_dlp
import os
import uuid

app = FastAPI()
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloader</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f0f12; color: #fff; text-align: center; padding: 50px 20px; margin: 0; }
        .card { background: #1a1a24; max-width: 420px; margin: 0 auto; padding: 25px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h2 { margin-top: 0; color: #a78bfa; }
        input[type=text] { width: 100%; padding: 14px; margin: 15px 0; border-radius: 10px; border: 1px solid #33334d; background: #0f0f12; color: #fff; font-size: 16px; box-sizing: border-box; }
        button { width: 100%; padding: 14px; background: #7c4dff; color: #fff; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; }
        button:hover { background: #651fff; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Downloader</h2>
        <form action="/download" method="post">
            <input type="text" name="url" placeholder="Paste link here..." required>
            <button type="submit">Download File</button>
        </form>
    </div>
</body>
</html>
"""

def cleanup_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

@app.post("/download")
def download(background_tasks: BackgroundTasks, url: str = Form(...)):
    file_id = str(uuid.uuid4())[:8]
    out_path = f"{DOWNLOAD_DIR}/{file_id}_%(title)s.%(ext)s"

    ydl_opts = {
        'outtmpl': out_path,
        'format': 'best',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    background_tasks.add_task(cleanup_file, filename)

    return FileResponse(
        path=filename,
        filename=os.path.basename(filename),
        media_type='application/octet-stream'
    )
