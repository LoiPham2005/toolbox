"""Công cụ ảnh: nén, đổi định dạng, đổi kích thước, cắt ảnh."""
import os
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from PIL import Image, ImageOps

from ..common import new_workspace, save_uploads, save_upload, make_zip, cleanup_task

router = APIRouter(prefix="/api/image", tags=["image"])

MIME = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}


def _send(path, folder, media):
    return FileResponse(path, filename=os.path.basename(path),
                        media_type=media, background=cleanup_task(folder))


def _finish(outs, folder, single_ext, zip_name):
    """1 file -> trả trực tiếp; nhiều file -> zip."""
    if not outs:
        raise HTTPException(400, "Không xử lý được ảnh nào.")
    if len(outs) == 1:
        return _send(outs[0], folder, MIME.get(single_ext, "application/octet-stream"))
    zip_path = make_zip(outs, folder, zip_name)
    return _send(zip_path, folder, "application/zip")


def _open(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # xoay đúng theo EXIF
    return img


@router.post("/compress")
async def compress(files: List[UploadFile] = File(...), quality: int = Form(75)):
    folder = new_workspace()
    paths = save_uploads(files, folder)
    outs = []
    for p in paths:
        try:
            img = _open(p)
            base, ext = os.path.splitext(os.path.basename(p))
            ext = ext.lower().lstrip(".")
            op = os.path.join(folder, f"{base}_nen.{ext if ext in MIME else 'jpg'}")
            if ext == "png":
                img.save(op, "PNG", optimize=True)
            elif ext == "webp":
                img.save(op, "WEBP", quality=quality)
            else:
                img.convert("RGB").save(op, "JPEG", quality=quality, optimize=True)
            outs.append(op)
        except Exception:
            continue
    ext0 = os.path.splitext(paths[0])[1].lower().lstrip(".")
    return _finish(outs, folder, ext0, "anh-nen.zip")


@router.post("/convert")
async def convert(files: List[UploadFile] = File(...), format: str = Form("jpg")):
    fmt = format.lower()
    if fmt not in ("jpg", "png", "webp"):
        raise HTTPException(400, "Định dạng không hỗ trợ.")
    folder = new_workspace()
    paths = save_uploads(files, folder)
    outs = []
    for p in paths:
        try:
            img = _open(p)
            base = os.path.splitext(os.path.basename(p))[0]
            op = os.path.join(folder, f"{base}.{fmt}")
            if fmt == "jpg":
                img.convert("RGB").save(op, "JPEG", quality=92)
            elif fmt == "png":
                img.save(op, "PNG")
            else:
                img.save(op, "WEBP", quality=92)
            outs.append(op)
        except Exception:
            continue
    return _finish(outs, folder, fmt, f"anh-{fmt}.zip")


@router.post("/resize")
async def resize(files: List[UploadFile] = File(...),
                 mode: str = Form("percent"), value: float = Form(50)):
    if value <= 0:
        raise HTTPException(400, "Giá trị phải lớn hơn 0.")
    folder = new_workspace()
    paths = save_uploads(files, folder)
    outs = []
    for p in paths:
        try:
            img = _open(p)
            w, h = img.size
            if mode == "width":
                nw = int(value)
                nh = max(1, round(h * nw / w))
            else:  # percent
                nw = max(1, round(w * value / 100))
                nh = max(1, round(h * value / 100))
            resized = img.resize((nw, nh), Image.LANCZOS)
            base, ext = os.path.splitext(os.path.basename(p))
            ext = ext.lower().lstrip(".")
            op = os.path.join(folder, f"{base}_{nw}x{nh}.{ext if ext in MIME else 'jpg'}")
            if ext == "png":
                resized.save(op, "PNG")
            elif ext == "webp":
                resized.save(op, "WEBP", quality=92)
            else:
                resized.convert("RGB").save(op, "JPEG", quality=92)
            outs.append(op)
        except Exception:
            continue
    ext0 = os.path.splitext(paths[0])[1].lower().lstrip(".")
    return _finish(outs, folder, ext0, "anh-resize.zip")


def _save_hq(img, path, ext):
    """Lưu ảnh ở chất lượng cao nhất (crop không làm giảm nét)."""
    if ext == "png":
        img.save(path, "PNG")  # không mất dữ liệu
    elif ext == "webp":
        img.save(path, "WEBP", quality=98, method=6)
    else:  # jpg
        img.convert("RGB").save(path, "JPEG", quality=98, subsampling=0, optimize=True)


@router.post("/crop")
async def crop(file: UploadFile = File(...),
               x: float = Form(...), y: float = Form(...),
               w: float = Form(...), h: float = Form(...),
               nat_w: float = Form(...), nat_h: float = Form(...),
               format: str = Form("keep")):
    """
    Cắt ảnh từ BẢN GỐC độ phân giải đầy đủ để giữ nét cao.
    x,y,w,h: vùng chọn (theo pixel ảnh mà trình duyệt thấy).
    nat_w,nat_h: kích thước tự nhiên trình duyệt báo -> để map chính xác về ảnh gốc.
    """
    folder = new_workspace()
    path = save_upload(file, folder)
    try:
        img = _open(path)  # đã tự xoay theo EXIF
    except Exception:
        raise HTTPException(400, "Không đọc được ảnh.")

    W, H = img.size
    # Tỷ lệ giữa ảnh gốc (PIL) và kích thước trình duyệt báo -> map an toàn kể cả lệch nhỏ
    sx = W / nat_w if nat_w else 1
    sy = H / nat_h if nat_h else 1
    left = round(x * sx)
    top = round(y * sy)
    right = round((x + w) * sx)
    bottom = round((y + h) * sy)
    # Kẹp trong biên ảnh
    left = max(0, min(left, W - 1))
    top = max(0, min(top, H - 1))
    right = max(left + 1, min(right, W))
    bottom = max(top + 1, min(bottom, H))

    cropped = img.crop((left, top, right, bottom))

    base, ext = os.path.splitext(os.path.basename(path))
    ext = ext.lower().lstrip(".")
    fmt = format.lower()
    if fmt == "png":
        ext = "png"
    elif fmt == "jpg":
        ext = "jpg"
    elif ext not in MIME:
        ext = "png"  # giữ nét cho định dạng lạ
    op = os.path.join(folder, f"{base}_cat_{right-left}x{bottom-top}.{ext}")
    _save_hq(cropped, op, ext)
    return _send(op, folder, MIME.get(ext, "image/png"))
