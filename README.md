# 🧰 ToolBox — Bộ công cụ online miễn phí

Một website gom nhiều tiện ích chạy ngay trên máy bạn: tải video, xử lý PDF, ảnh, chuyển đổi tài liệu. Xây trên **FastAPI + Python**, giao diện web tối giản, **không gửi file lên server nào cả**.

## Các công cụ

**🎬 Video**
- **Tải video** — YouTube, TikTok, Facebook, Instagram… chất lượng cao tới 4K, hoặc tách nhạc MP3

**📄 PDF**
- **Gộp PDF** — nối nhiều file thành một
- **Tách PDF** — lấy trang cần, hoặc tách mỗi trang thành 1 file
- **Nén PDF** — giảm dung lượng
- **Xoay PDF** — xoay trang 90/180/270°
- **Xóa trang PDF** — bỏ các trang không cần

**🔄 Chuyển đổi**
- **PDF → Ảnh** (JPG/PNG, chọn độ nét)
- **Ảnh → PDF** — gộp nhiều ảnh thành 1 PDF
- **PDF → Word** (.docx chỉnh sửa được)
- **Office → PDF** — Word/Excel/PowerPoint *(cần LibreOffice)*

**🖼️ Ảnh**
- **Nén ảnh**, **Đổi định dạng** (JPG/PNG/WebP), **Đổi kích thước**

**✨ Khác**
- **Tạo mã QR** từ link hoặc văn bản

## Yêu cầu

- **Python 3.9+**
- **ffmpeg** — cho video chất lượng cao (`brew install ffmpeg`)
- *(Tùy chọn)* **LibreOffice** — chỉ cần nếu dùng "Office → PDF" (`brew install --cask libreoffice`)

## Chạy nhanh

```bash
cd toolbox
./run.sh
```

Mở trình duyệt: **http://127.0.0.1:8000**

## Cấu trúc

```
toolbox/
├── app/
│   ├── main.py              # FastAPI: gắn router, phục vụ trang, /api/tools
│   ├── common.py            # Tiện ích chung: file tạm, zip, dọn dẹp
│   ├── tools_registry.py    # ⭐ Khai báo mọi công cụ (thêm tool sửa ở đây)
│   ├── routers/
│   │   ├── video.py         # Tải video (yt-dlp)
│   │   ├── pdf.py           # Gộp/tách/nén/xoay/xóa trang
│   │   ├── convert.py       # PDF↔ảnh, PDF→Word, Office→PDF
│   │   ├── image.py         # Nén/đổi định dạng/resize ảnh
│   │   └── misc.py          # Mã QR
│   └── static/
│       ├── style.css        # Giao diện dùng chung
│       ├── index.html       # Trang chủ (thư viện công cụ)
│       ├── tool.html        # Trang xử lý file dùng chung (config-driven)
│       └── video.html       # Trang tải video (2 bước)
├── requirements.txt
└── run.sh
```

## Thêm công cụ mới (rất dễ)

Kiến trúc **config-driven**: trang `tool.html` tự dựng giao diện từ khai báo. Để thêm tool:

1. Viết endpoint mới trong `app/routers/…` (nhận file, trả file).
2. Thêm một mục vào `TOOLS` trong [app/tools_registry.py](app/tools_registry.py) (tên, icon, input, options, endpoint).

Xong — công cụ tự hiện ở trang chủ và có sẵn giao diện, không cần viết HTML.

## Ghi chú kỹ thuật

- **Tải video**: dùng client `android_vr` của yt-dlp để lấy full độ phân giải YouTube mà không cần PO token.
- **PDF → Word**: có shim tương thích `Rect.get_area()` cho pdf2docx trên PyMuPDF mới. Hợp với PDF văn bản; PDF scan/layout phức tạp có thể lệch.
- Mọi file xử lý xong được lưu tạm rồi **tự xóa** sau khi tải về.

## Lưu ý pháp lý

Chỉ tải/ xử lý nội dung bạn có quyền sử dụng. Tôn trọng bản quyền và điều khoản dịch vụ của các nền tảng.
