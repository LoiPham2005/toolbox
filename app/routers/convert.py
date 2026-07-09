"""Chuyển đổi: PDF↔ảnh, PDF→Word, Office→PDF."""
import os
import glob
import shutil
import subprocess
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import fitz  # PyMuPDF
import img2pdf
from PIL import Image

from ..common import new_workspace, save_uploads, make_zip, cleanup_task

# Tương thích: pdf2docx 0.5.8 gọi Rect.get_area() đã bị PyMuPDF mới bỏ.
if not hasattr(fitz.Rect, "get_area"):
    fitz.Rect.get_area = lambda self, unit="px": abs(self.width * self.height)

router = APIRouter(prefix="/api/convert", tags=["convert"])

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _send(path, folder, media):
    return FileResponse(path, filename=os.path.basename(path),
                        media_type=media, background=cleanup_task(folder))


@router.post("/pdf-to-images")
async def pdf_to_images(files: List[UploadFile] = File(...),
                        format: str = Form("jpg"), dpi: int = Form(150)):
    folder = new_workspace()
    path = save_uploads(files, folder)[0]
    base = os.path.splitext(os.path.basename(path))[0]
    fmt = "jpg" if format.lower() in ("jpg", "jpeg") else "png"
    try:
        doc = fitz.open(path)
        outs = []
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat)
            op = os.path.join(folder, f"{base}_trang{i+1}.{fmt}")
            if fmt == "jpg":
                pix.pil_save(op, format="JPEG", quality=90)
            else:
                pix.save(op)
            outs.append(op)
        doc.close()
    except Exception as e:
        raise HTTPException(400, f"Không chuyển được: {e}")
    if len(outs) == 1:
        media = "image/jpeg" if fmt == "jpg" else "image/png"
        return _send(outs[0], folder, media)
    zip_path = make_zip(outs, folder, f"{base}_anh.zip")
    return _send(zip_path, folder, "application/zip")


@router.post("/images-to-pdf")
async def images_to_pdf(files: List[UploadFile] = File(...)):
    folder = new_workspace()
    paths = save_uploads(files, folder)
    # Chuẩn hóa ảnh (bỏ alpha, xoay theo EXIF) để img2pdf không lỗi
    clean = []
    for p in paths:
        try:
            img = Image.open(p)
            img = img.convert("RGB")
            cp = os.path.splitext(p)[0] + "_rgb.jpg"
            img.save(cp, "JPEG", quality=92)
            clean.append(cp)
        except Exception:
            continue
    if not clean:
        raise HTTPException(400, "Không đọc được ảnh nào hợp lệ.")
    out = os.path.join(folder, "anh-thanh-pdf.pdf")
    try:
        with open(out, "wb") as f:
            f.write(img2pdf.convert(clean))
    except Exception as e:
        raise HTTPException(400, f"Không tạo được PDF: {e}")
    return _send(out, folder, "application/pdf")


@router.post("/pdf-to-word")
async def pdf_to_word(files: List[UploadFile] = File(...)):
    from pdf2docx import Converter
    folder = new_workspace()
    path = save_uploads(files, folder)[0]
    base = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(folder, f"{base}.docx")
    try:
        cv = Converter(path)
        cv.convert(out)
        cv.close()
    except Exception as e:
        raise HTTPException(400, f"Không chuyển được sang Word: {e}")
    if not os.path.exists(out):
        raise HTTPException(400, "Chuyển đổi thất bại (PDF có thể là ảnh scan).")
    return _send(out, folder, DOCX_MIME)


def _find_soffice():
    for c in ("soffice", "libreoffice",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if shutil.which(c) or os.path.exists(c):
            return c
    return None


@router.post("/office-to-pdf")
async def office_to_pdf(files: List[UploadFile] = File(...)):
    soffice = _find_soffice()
    if not soffice:
        raise HTTPException(
            400,
            "Chưa cài LibreOffice trên máy chủ. Cài rồi thử lại — "
            "macOS: brew install --cask libreoffice | Ubuntu: sudo apt install libreoffice",
        )
    folder = new_workspace()
    path = save_uploads(files, folder)[0]
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", folder, path],
            check=True, capture_output=True, timeout=120,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(400, f"Không chuyển được: {e.stderr.decode()[:200]}")
    except subprocess.TimeoutExpired:
        raise HTTPException(400, "Chuyển đổi quá lâu, đã hủy.")
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    if not pdfs:
        raise HTTPException(400, "Không tạo được file PDF.")
    return _send(pdfs[0], folder, "application/pdf")
