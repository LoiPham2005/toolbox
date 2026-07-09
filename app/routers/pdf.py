"""Công cụ PDF: gộp, tách, nén, xoay, xóa trang."""
import os
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF

from ..common import (new_workspace, save_uploads, make_zip, cleanup_task,
                      parse_pages, sanitize)

router = APIRouter(prefix="/api/pdf", tags=["pdf"])


def _send(path: str, folder: str, media="application/pdf"):
    return FileResponse(path, filename=os.path.basename(path),
                        media_type=media, background=cleanup_task(folder))


@router.post("/merge")
async def merge(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(400, "Cần ít nhất 2 file PDF để gộp.")
    folder = new_workspace()
    paths = save_uploads(files, folder)
    writer = PdfWriter()
    try:
        for p in paths:
            writer.append(p)
        out = os.path.join(folder, "da-gop.pdf")
        with open(out, "wb") as f:
            writer.write(f)
    except Exception as e:
        raise HTTPException(400, f"Không gộp được: {e}")
    return _send(out, folder)


@router.post("/split")
async def split(files: List[UploadFile] = File(...),
                pages: str = Form(""), each: bool = Form(False)):
    folder = new_workspace()
    path = save_uploads(files, folder)[0]
    reader = PdfReader(path)
    total = len(reader.pages)
    idxs = parse_pages(pages, total) if pages.strip() else list(range(total))
    if not idxs:
        raise HTTPException(400, "Không có trang hợp lệ để tách.")
    base = os.path.splitext(os.path.basename(path))[0]

    if each:
        outs = []
        for i in idxs:
            w = PdfWriter()
            w.add_page(reader.pages[i])
            op = os.path.join(folder, f"{base}_trang{i+1}.pdf")
            with open(op, "wb") as f:
                w.write(f)
            outs.append(op)
        zip_path = make_zip(outs, folder, f"{base}_cac-trang.zip")
        return _send(zip_path, folder, "application/zip")

    w = PdfWriter()
    for i in idxs:
        w.add_page(reader.pages[i])
    out = os.path.join(folder, f"{base}_da-tach.pdf")
    with open(out, "wb") as f:
        w.write(f)
    return _send(out, folder)


@router.post("/compress")
async def compress(files: List[UploadFile] = File(...), level: str = Form("medium")):
    folder = new_workspace()
    path = save_uploads(files, folder)[0]
    # Ngưỡng DPI ảnh theo mức nén: mạnh hơn -> ảnh nhỏ hơn
    dpi_map = {"low": 200, "medium": 120, "high": 72}
    target_dpi = dpi_map.get(level, 120)
    base = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(folder, f"{base}_da-nen.pdf")
    try:
        doc = fitz.open(path)
        # Giảm mẫu ảnh nhúng để giảm dung lượng
        doc.rewrite_images(dpi_threshold=target_dpi + 1, dpi_target=target_dpi,
                           quality=70, lossy=True)
        doc.save(out, garbage=4, deflate=True, clean=True)
        doc.close()
    except Exception as e:
        raise HTTPException(400, f"Không nén được: {e}")
    # Nếu nén xong lớn hơn bản gốc thì trả lại bản gốc
    if os.path.getsize(out) >= os.path.getsize(path):
        return _send(path, folder)
    return _send(out, folder)


@router.post("/rotate")
async def rotate(files: List[UploadFile] = File(...),
                 angle: int = Form(90), pages: str = Form("")):
    folder = new_workspace()
    path = save_uploads(files, folder)[0]
    reader = PdfReader(path)
    total = len(reader.pages)
    idxs = set(parse_pages(pages, total)) if pages.strip() else set(range(total))
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i in idxs:
            page.rotate(angle)
        writer.add_page(page)
    base = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(folder, f"{base}_da-xoay.pdf")
    with open(out, "wb") as f:
        writer.write(f)
    return _send(out, folder)


@router.post("/delete-pages")
async def delete_pages(files: List[UploadFile] = File(...), pages: str = Form("")):
    if not pages.strip():
        raise HTTPException(400, "Hãy nhập các trang cần xóa (vd: 2,4-6).")
    folder = new_workspace()
    path = save_uploads(files, folder)[0]
    reader = PdfReader(path)
    total = len(reader.pages)
    remove = set(parse_pages(pages, total))
    keep = [i for i in range(total) if i not in remove]
    if not keep:
        raise HTTPException(400, "Không thể xóa hết tất cả các trang.")
    writer = PdfWriter()
    for i in keep:
        writer.add_page(reader.pages[i])
    base = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(folder, f"{base}_da-xoa-trang.pdf")
    with open(out, "wb") as f:
        writer.write(f)
    return _send(out, folder)
