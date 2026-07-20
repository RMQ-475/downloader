from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
import yt_dlp
import os
import uuid

app = FastAPI()
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloader</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f0f12; color: #fff; text-align: center; padding: 40px 15px; margin: 0; }
        .card { background: #1a1a24; max-width: 440px; margin: 0 auto; padding: 25px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); box-sizing: border-box; }
        h2 { margin-top: 0; color: #a78bfa; }
        input[type=text] { width: 100%; padding: 14px; margin: 15px 0; border-radius: 10px; border: 1px solid #33334d; background: #0f0f12; color: #fff; font-size: 16px; box-sizing: border-box; }
        button { width: 100%; padding: 14px; background: #7c4dff; color: #fff; border: none; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; }
        button:hover { background: #651fff; }
        .preview { margin-top: 20px; padding: 15px; background: #12121a; border-radius: 12px; border: 1px solid #2d2d3f; }
        .preview img { width: 100%; border-radius: 8px; margin-bottom: 12px; }
        .preview h4 { margin: 5px 0 15px 0; font-size: 15px; color: #e2e8f0; line-height: 1.4; }
        .dl-btn { background: #00e676; color: #000; }
        .dl-btn:hover { background: #00c853; }
        .error { color: #ff5252; margin-top: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Downloader</h2>
        <form action="/fetch" method="post">
            <input type="text" name="url" placeholder="Paste link here..." value="URL_VALUE_HOLDER" required>
            <button type="submit">Fetch Video Info</button>
        </form>

        ERROR_SECTION_HOLDER

        PREVIEW_SECTION_HOLDER
    </div>
</body>
</html>
"""

def render_html(url="", error="", preview=""):
    return (
        HTML_TEMPLATE
        .replace("URL_VALUE_HOLDER", url)
        .replace("ERROR_SECTION_HOLDER", error)
        .replace("PREVIEW_SECTION_HOLDER", preview)
    )

def cleanup_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass

def get_ytdl_opts(extra_opts=None):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android_vr', 'tv_downgraded', 'web_safari']
            }
        },
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
    }
    if extra_opts:
        opts.update(extra_opts)
    return opts

@app.get("/", response_class=HTMLResponse)
def index():
    return render_html()

@app.post("/fetch", response_class=HTMLResponse)
def fetch_info(url: str = Form(...)):
    opts = get_ytdl_opts({'skip_download': True})
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video Preview')
            thumbnail = info.get('thumbnail', '')
            
            thumb_html = f'<img src="{thumbnail}" alt="Thumbnail">' if thumbnail else '<div style="font-size:48px;margin:10px;">🎥</div>'

            preview = f"""
            <div class="preview">
                {thumb_html}
                <h4>{title}</h4>
                <form action="/download" method="post">
                    <input type="hidden" name="url" value="{url}">
                    <button type="submit" class="dl-btn">Download Now</button>
                </form>
            </div>
            """
            return render_html(url=url, preview=preview)
    except Exception as e:
        err_msg = f'<div class="error">Failed to load video: {str(e)[:120]}</div>'
        return render_html(url=url, error=err_msg)

@app.post("/download")
def download(background_tasks: BackgroundTasks, url: str = Form(...)):
    file_id = str(uuid.uuid4())[:8]
    out_path = f"{DOWNLOAD_DIR}/{file_id}_%(title)s.%(ext)s"

    opts = get_ytdl_opts({
        'outtmpl': out_path,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    background_tasks.add_task(cleanup_file, filename)

    return FileResponse(
        path=filename,
        filename=os.path.basename(filename),
        media_type='application/octet-stream'
    )
    except Exception as e:
        err_msg = f'<div class="error">Failed to load video: {str(e)[:120]}</div>'
        return render_html(url=url, error=err_msg)

@app.post("/download")
def download(background_tasks: BackgroundTasks, url: str = Form(...)):
    file_id = str(uuid.uuid4())[:8]
    out_path = f"{DOWNLOAD_DIR}/{file_id}_%(title)s.%(ext)s"

    opts = get_ytdl_opts({
        'outtmpl': out_path,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    })

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    background_tasks.add_task(cleanup_file, filename)

    return FileResponse(
        path=filename,
        filename=os.path.basename(filename),
        media_type='application/octet-stream'
    )
