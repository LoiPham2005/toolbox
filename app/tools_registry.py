"""
Danh mục công cụ. Dữ liệu này vừa dùng ở backend, vừa gửi cho frontend
(/api/tools) để tự dựng giao diện — thêm 1 công cụ = thêm 1 mục ở đây + 1 endpoint.

Mỗi tool:
  id        : định danh
  name      : tên hiển thị
  icon      : emoji
  category  : nhóm (video/pdf/convert/image/other)
  desc      : mô tả ngắn
  page      : 'generic' (trang xử lý file chung) hoặc 'video' (trang riêng)
  input     : 'files' | 'text'          (chỉ với page=generic)
  accept    : định dạng file cho ô upload
  multiple  : cho chọn nhiều file
  min_files : số file tối thiểu
  endpoint  : API xử lý
  options   : danh sách tùy chọn -> {key,type,label,choices?,default,min?,max?,placeholder?}
"""

CATEGORIES = [
    {"id": "video", "name": "Video", "icon": "🎬"},
    {"id": "pdf", "name": "PDF", "icon": "📄"},
    {"id": "convert", "name": "Chuyển đổi", "icon": "🔄"},
    {"id": "image", "name": "Ảnh", "icon": "🖼️"},
    {"id": "other", "name": "Khác", "icon": "✨"},
]

TOOLS = [
    # -------------------- VIDEO --------------------
    {
        "id": "video-download",
        "name": "Tải video",
        "icon": "⬇️",
        "category": "video",
        "desc": "Tải video từ YouTube, TikTok, Facebook… chất lượng cao, miễn phí",
        "page": "video",
    },

    # -------------------- PDF --------------------
    {
        "id": "pdf-merge",
        "name": "Gộp PDF",
        "icon": "🔗",
        "category": "pdf",
        "desc": "Gộp nhiều file PDF thành một",
        "page": "generic", "input": "files", "accept": ".pdf",
        "multiple": True, "min_files": 2,
        "endpoint": "/api/pdf/merge",
        "options": [],
    },
    {
        "id": "pdf-split",
        "name": "Tách PDF",
        "icon": "✂️",
        "category": "pdf",
        "desc": "Lấy ra các trang cần, hoặc tách mỗi trang thành một file",
        "page": "generic", "input": "files", "accept": ".pdf",
        "multiple": False, "min_files": 1,
        "endpoint": "/api/pdf/split",
        "options": [
            {"key": "pages", "type": "text", "label": "Các trang cần lấy (vd: 1-3,5,8)",
             "placeholder": "Để trống = tất cả", "default": ""},
            {"key": "each", "type": "checkbox", "label": "Mỗi trang thành 1 file riêng (tải về .zip)",
             "default": False},
        ],
    },
    {
        "id": "pdf-compress",
        "name": "Nén PDF",
        "icon": "🗜️",
        "category": "pdf",
        "desc": "Giảm dung lượng file PDF",
        "page": "generic", "input": "files", "accept": ".pdf",
        "multiple": False, "min_files": 1,
        "endpoint": "/api/pdf/compress",
        "options": [
            {"key": "level", "type": "select", "label": "Mức nén", "default": "medium",
             "choices": [{"value": "low", "label": "Nhẹ (giữ chất lượng)"},
                         {"value": "medium", "label": "Vừa (khuyên dùng)"},
                         {"value": "high", "label": "Mạnh (file nhỏ nhất)"}]},
        ],
    },
    {
        "id": "pdf-rotate",
        "name": "Xoay PDF",
        "icon": "🔃",
        "category": "pdf",
        "desc": "Xoay các trang trong PDF",
        "page": "generic", "input": "files", "accept": ".pdf",
        "multiple": False, "min_files": 1,
        "endpoint": "/api/pdf/rotate",
        "options": [
            {"key": "angle", "type": "select", "label": "Góc xoay", "default": "90",
             "choices": [{"value": "90", "label": "90° (phải)"},
                         {"value": "180", "label": "180°"},
                         {"value": "270", "label": "270° (trái)"}]},
            {"key": "pages", "type": "text", "label": "Trang cần xoay (vd: 1,3-5)",
             "placeholder": "Để trống = tất cả", "default": ""},
        ],
    },
    {
        "id": "pdf-delete",
        "name": "Xóa trang PDF",
        "icon": "🗑️",
        "category": "pdf",
        "desc": "Xóa bớt các trang không cần trong PDF",
        "page": "generic", "input": "files", "accept": ".pdf",
        "multiple": False, "min_files": 1,
        "endpoint": "/api/pdf/delete-pages",
        "options": [
            {"key": "pages", "type": "text", "label": "Các trang cần XÓA (vd: 2,4-6)",
             "placeholder": "Bắt buộc nhập", "default": ""},
        ],
    },

    # -------------------- CONVERT --------------------
    {
        "id": "pdf-to-images",
        "name": "PDF → Ảnh",
        "icon": "🖼️",
        "category": "convert",
        "desc": "Chuyển mỗi trang PDF thành ảnh (JPG/PNG)",
        "page": "generic", "input": "files", "accept": ".pdf",
        "multiple": False, "min_files": 1,
        "endpoint": "/api/convert/pdf-to-images",
        "options": [
            {"key": "format", "type": "select", "label": "Định dạng ảnh", "default": "jpg",
             "choices": [{"value": "jpg", "label": "JPG"}, {"value": "png", "label": "PNG"}]},
            {"key": "dpi", "type": "select", "label": "Độ nét", "default": "150",
             "choices": [{"value": "100", "label": "Thường (100 DPI)"},
                         {"value": "150", "label": "Nét (150 DPI)"},
                         {"value": "300", "label": "Rất nét (300 DPI)"}]},
        ],
    },
    {
        "id": "images-to-pdf",
        "name": "Ảnh → PDF",
        "icon": "📑",
        "category": "convert",
        "desc": "Gộp nhiều ảnh thành một file PDF",
        "page": "generic", "input": "files", "accept": "image/*",
        "multiple": True, "min_files": 1,
        "endpoint": "/api/convert/images-to-pdf",
        "options": [],
    },
    {
        "id": "pdf-to-word",
        "name": "PDF → Word",
        "icon": "📝",
        "category": "convert",
        "desc": "Chuyển PDF thành file Word (.docx) chỉnh sửa được",
        "page": "generic", "input": "files", "accept": ".pdf",
        "multiple": False, "min_files": 1,
        "endpoint": "/api/convert/pdf-to-word",
        "options": [],
        "note": "Hợp nhất với PDF dạng văn bản. PDF scan/ảnh hoặc layout phức tạp có thể bị lệch.",
    },
    {
        "id": "office-to-pdf",
        "name": "Office → PDF",
        "icon": "📕",
        "category": "convert",
        "desc": "Word / Excel / PowerPoint → PDF",
        "page": "generic", "input": "files",
        "accept": ".doc,.docx,.xls,.xlsx,.ppt,.pptx,.odt,.ods,.odp",
        "multiple": False, "min_files": 1,
        "endpoint": "/api/convert/office-to-pdf",
        "options": [],
        "note": "Cần cài LibreOffice trên máy chủ. Nếu chưa có sẽ báo hướng dẫn cài.",
    },

    # -------------------- IMAGE --------------------
    {
        "id": "image-compress",
        "name": "Nén ảnh",
        "icon": "🗜️",
        "category": "image",
        "desc": "Giảm dung lượng ảnh (JPG/PNG/WebP)",
        "page": "generic", "input": "files", "accept": "image/*",
        "multiple": True, "min_files": 1,
        "endpoint": "/api/image/compress",
        "options": [
            {"key": "quality", "type": "select", "label": "Chất lượng", "default": "75",
             "choices": [{"value": "60", "label": "Thấp (nhỏ nhất)"},
                         {"value": "75", "label": "Vừa (khuyên dùng)"},
                         {"value": "85", "label": "Cao"}]},
        ],
    },
    {
        "id": "image-convert",
        "name": "Đổi định dạng ảnh",
        "icon": "🔄",
        "category": "image",
        "desc": "Chuyển ảnh sang JPG / PNG / WebP",
        "page": "generic", "input": "files", "accept": "image/*",
        "multiple": True, "min_files": 1,
        "endpoint": "/api/image/convert",
        "options": [
            {"key": "format", "type": "select", "label": "Định dạng đích", "default": "jpg",
             "choices": [{"value": "jpg", "label": "JPG"}, {"value": "png", "label": "PNG"},
                         {"value": "webp", "label": "WebP"}]},
        ],
    },
    {
        "id": "image-crop",
        "name": "Cắt ảnh",
        "icon": "✂️",
        "category": "image",
        "desc": "Chọn vùng ảnh cần lấy, cắt ra giữ nguyên độ nét cao",
        "page": "crop",
    },
    {
        "id": "image-resize",
        "name": "Đổi kích thước ảnh",
        "icon": "📐",
        "category": "image",
        "desc": "Thu nhỏ / phóng to ảnh theo % hoặc chiều rộng",
        "page": "generic", "input": "files", "accept": "image/*",
        "multiple": True, "min_files": 1,
        "endpoint": "/api/image/resize",
        "options": [
            {"key": "mode", "type": "select", "label": "Cách đổi", "default": "percent",
             "choices": [{"value": "percent", "label": "Theo phần trăm"},
                         {"value": "width", "label": "Theo chiều rộng (px)"}]},
            {"key": "value", "type": "number", "label": "Giá trị (% hoặc px)",
             "default": 50, "min": 1, "max": 10000},
        ],
    },

    # -------------------- OTHER --------------------
    {
        "id": "qr-generate",
        "name": "Tạo mã QR",
        "icon": "🔳",
        "category": "other",
        "desc": "Tạo mã QR từ link hoặc văn bản",
        "page": "generic", "input": "text",
        "endpoint": "/api/misc/qr",
        "options": [
            {"key": "text", "type": "text", "label": "Nội dung / link",
             "placeholder": "https://... hoặc chữ bất kỳ", "default": ""},
            {"key": "size", "type": "select", "label": "Kích thước", "default": "medium",
             "choices": [{"value": "small", "label": "Nhỏ"}, {"value": "medium", "label": "Vừa"},
                         {"value": "large", "label": "Lớn"}]},
        ],
    },
]


def tool_by_id(tool_id: str):
    for t in TOOLS:
        if t["id"] == tool_id:
            return t
    return None
