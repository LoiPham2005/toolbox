"""Tiện ích khác: tạo mã QR."""
import os

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
import qrcode

from ..common import new_workspace, cleanup_task

router = APIRouter(prefix="/api/misc", tags=["misc"])

SIZE_MAP = {"small": 6, "medium": 10, "large": 16}


@router.post("/qr")
async def qr(text: str = Form(""), size: str = Form("medium")):
    if not text.strip():
        raise HTTPException(400, "Hãy nhập nội dung hoặc link để tạo mã QR.")
    folder = new_workspace()
    qr_obj = qrcode.QRCode(
        box_size=SIZE_MAP.get(size, 10), border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
    )
    qr_obj.add_data(text)
    qr_obj.make(fit=True)
    img = qr_obj.make_image(fill_color="black", back_color="white")
    out = os.path.join(folder, "ma-qr.png")
    img.save(out)
    return FileResponse(out, filename="ma-qr.png", media_type="image/png",
                        background=cleanup_task(folder))
