# ToolBox — FastAPI. Bản gọn: ffmpeg (video) + deps Python.
# (Office→PDF cần LibreOffice — bỏ để image nhẹ; app tự báo "chưa cài" nếu dùng.
#  Muốn bật: thêm `libreoffice` vào apt-get bên dưới — image sẽ ~+600MB.)
FROM python:3.12-slim

# ffmpeg: tải/xử lý video (yt-dlp). libglib2.0-0: opencv trong pdf2docx (PDF→Word).
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài thư viện trước (tận dụng cache layer khi chỉ đổi code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Bind 0.0.0.0 để DeployBox proxy vào được (run.sh dùng 127.0.0.1 chỉ cho chạy local).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
