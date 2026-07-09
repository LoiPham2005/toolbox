#!/bin/bash
# ============================================================
#  ToolBox — Bộ công cụ online. Script chạy tất-cả-trong-một.
# ============================================================
set -e
cd "$(dirname "$0")"

command -v python3 >/dev/null || { echo "❌ Cần cài Python 3"; exit 1; }
command -v ffmpeg  >/dev/null || echo "⚠️  Chưa có ffmpeg — cần cho video chất lượng cao. macOS: brew install ffmpeg"

if [ ! -d "venv" ]; then
  echo "==> Tạo môi trường ảo Python (lần đầu)..."
  python3 -m venv venv
fi
source venv/bin/activate

echo "==> Cài đặt thư viện (lần đầu hơi lâu)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "======================================================"
echo "  🧰 ToolBox đang chạy"
echo "  ✅ Mở trình duyệt:  http://127.0.0.1:8000"
echo "  Nhấn Ctrl+C để dừng"
echo "======================================================"
echo ""
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
