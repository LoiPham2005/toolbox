"""Công cụ tải video (YouTube, TikTok, Facebook…) qua yt-dlp."""
import os
import threading
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp

from ..common import WORK_DIR, sanitize

router = APIRouter(prefix="/api/video", tags=["video"])

DOWNLOAD_DIR = os.path.join(WORK_DIR, "video")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

JOBS = {}
JOBS_LOCK = threading.Lock()


class InfoRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    format_id: Optional[str] = None
    audio_only: bool = False


def base_ydl_opts():
    # 'android_vr' lấy được đầy đủ độ phân giải YouTube (tới 4K/8K) mà không cần PO token.
    return {
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["android_vr", "android"]}},
    }


def _human_size(num):
    if not num:
        return ""
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024:
            return f"{num:.0f}{unit}" if unit == "B" else f"{num:.1f}{unit}"
        num /= 1024
    return f"{num:.1f}TB"


@router.post("/info")
def get_info(req: InfoRequest):
    opts = base_ydl_opts()
    opts["skip_download"] = True
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(req.url, download=False)
    except Exception as e:
        raise HTTPException(400, f"Không lấy được video: {e}")
    if info.get("_type") == "playlist" and info.get("entries"):
        info = info["entries"][0]

    seen = {}
    for f in info.get("formats", []):
        if f.get("vcodec") == "none" or not f.get("height"):
            continue
        h = f["height"]
        cur = f.get("tbr") or 0
        if h not in seen or cur > (seen[h].get("tbr") or 0):
            seen[h] = {
                "format_id": f.get("format_id"), "height": h, "label": f"{h}p",
                "ext": f.get("ext"), "fps": f.get("fps"),
                "filesize": _human_size(f.get("filesize") or f.get("filesize_approx")),
                "tbr": cur,
            }
    formats = sorted(seen.values(), key=lambda x: x["height"], reverse=True)
    return {
        "title": info.get("title"), "uploader": info.get("uploader"),
        "duration": info.get("duration"), "thumbnail": info.get("thumbnail"),
        "formats": formats,
    }


def _run_download(job_id, req):
    job_dir = os.path.join(DOWNLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    def hook(d):
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                done = d.get("downloaded_bytes", 0)
                job["progress"] = round(done / total * 100, 1) if total else 0
                job["speed"] = (_human_size(d.get("speed")) + "/s") if d.get("speed") else ""
            elif d["status"] == "finished":
                job["progress"] = 99.0

    opts = base_ydl_opts()
    if req.audio_only:
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3", "preferredquality": "192"}],
        })
    else:
        fmt = (f"{req.format_id}+bestaudio/{req.format_id}/best"
               if req.format_id else "bestvideo+bestaudio/best")
        opts["format"] = fmt
    opts.update({
        "outtmpl": os.path.join(job_dir, "%(title)s.%(ext)s"),
        "noplaylist": True, "merge_output_format": "mp4",
        "progress_hooks": [hook],
    })

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
            if info.get("_type") == "playlist" and info.get("entries"):
                info = info["entries"][0]
        files = [f for f in os.listdir(job_dir) if os.path.isfile(os.path.join(job_dir, f))]
        if not files:
            raise RuntimeError("Không tìm thấy file sau khi tải")
        filepath = os.path.join(job_dir, files[0])
        filename = sanitize(info.get("title", "video")) + os.path.splitext(files[0])[1]
        with JOBS_LOCK:
            JOBS[job_id].update({"status": "done", "progress": 100.0,
                                 "filepath": filepath, "filename": filename})
    except Exception as e:
        with JOBS_LOCK:
            JOBS[job_id].update({"status": "error", "error": str(e)})


@router.post("/download")
def start_download(req: DownloadRequest):
    job_id = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS[job_id] = {"status": "downloading", "progress": 0.0, "speed": ""}
    threading.Thread(target=_run_download, args=(job_id, req), daemon=True).start()
    return {"job_id": job_id}


@router.get("/progress/{job_id}")
def get_progress(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(404, "Không tìm thấy phiên tải")
        return {"status": job["status"], "progress": job.get("progress", 0),
                "speed": job.get("speed", ""), "error": job.get("error"),
                "filename": job.get("filename")}


@router.get("/file/{job_id}")
def get_file(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job or job.get("status") != "done":
        raise HTTPException(404, "File chưa sẵn sàng")
    return FileResponse(job["filepath"], filename=job["filename"],
                        media_type="application/octet-stream")
