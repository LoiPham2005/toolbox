"""Tiện ích dùng chung: thư mục tạm, lưu file upload, nén zip, dọn dẹp."""
import os
import re
import uuid
import shutil
import zipfile
import tempfile
from typing import List

from fastapi import UploadFile
from starlette.background import BackgroundTask

# Thư mục tạm gốc cho toàn bộ app
WORK_DIR = os.path.join(tempfile.gettempdir(), "toolbox")
os.makedirs(WORK_DIR, exist_ok=True)


def new_workspace() -> str:
    """Tạo một thư mục làm việc riêng cho mỗi yêu cầu."""
    d = os.path.join(WORK_DIR, uuid.uuid4().hex)
    os.makedirs(d, exist_ok=True)
    return d


def sanitize(name: str) -> str:
    name = os.path.basename(name or "")
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    return name.strip()[:150] or "file"


def save_upload(upload: UploadFile, folder: str) -> str:
    """Lưu 1 file upload vào folder, trả về đường dẫn."""
    dest = os.path.join(folder, sanitize(upload.filename))
    # tránh trùng tên
    base, ext = os.path.splitext(dest)
    i = 1
    while os.path.exists(dest):
        dest = f"{base}_{i}{ext}"
        i += 1
    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return dest


def save_uploads(uploads: List[UploadFile], folder: str) -> List[str]:
    return [save_upload(u, folder) for u in uploads]


def make_zip(files: List[str], folder: str, zip_name: str = "ketqua.zip") -> str:
    """Gộp nhiều file thành 1 zip trong folder."""
    zip_path = os.path.join(folder, sanitize(zip_name))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, arcname=os.path.basename(f))
    return zip_path


def cleanup_task(folder: str) -> BackgroundTask:
    """Trả về BackgroundTask để xóa folder sau khi đã gửi file về client."""
    return BackgroundTask(shutil.rmtree, folder, ignore_errors=True)


def parse_pages(spec: str, total: int) -> List[int]:
    """Chuyển '1-3,5,7' thành [0,1,2,4,6] (0-indexed), lọc theo tổng số trang."""
    result = []
    if not spec:
        return result
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            a = int(a) if a else 1
            b = int(b) if b else total
            for p in range(a, b + 1):
                if 1 <= p <= total:
                    result.append(p - 1)
        else:
            p = int(part)
            if 1 <= p <= total:
                result.append(p - 1)
    # loại trùng, giữ thứ tự
    seen = set()
    out = []
    for p in result:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out
