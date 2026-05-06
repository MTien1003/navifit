# 🏋️ NaviFit — Ứng dụng tìm kiếm địa điểm tập luyện

> Ứng dụng web hỗ trợ tìm kiếm địa điểm tập luyện tại Hà Nội, hướng đến người dùng Nhật Bản.  
> Tích hợp bản đồ Leaflet, thông tin chất lượng không khí (AQI), tính đường đi và SOS khẩn cấp.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![NiceGUI](https://img.shields.io/badge/NiceGUI-latest-green)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal?logo=fastapi)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📸 Tính năng

| Tính năng | Mô tả |
|---|---|
| 🗺️ **Bản đồ tương tác** | Hiển thị địa điểm tập luyện với icon emoji theo loại (gym/park/pool/badminton) |
| 🔍 **Tìm kiếm thông minh** | Tìm kiếm tên tiếng Việt hoặc tiếng Nhật, gợi ý realtime |
| 🇯🇵 **Hỗ trợ tiếng Nhật** | Lọc địa điểm có nhân viên nói tiếng Nhật |
| 📍 **Gợi ý cùng loại** | Tự động hiển thị các gym/công viên/hồ bơi/sân cầu lông tương tự |
| 🚗 **Tính đường đi** | Hiển thị tuyến đường và thời gian lái xe (OSRM) |
| ⏰ **Thời gian tốt nhất** | Biểu đồ mức độ đông đúc theo ngày/giờ |
| 💨 **Chất lượng không khí** | AQI realtime từ IQAir API |
| 🆘 **SOS khẩn cấp** | Danh sách liên hệ: cảnh sát, cứu thương, Đại sứ quán Nhật |
| ⭐ **Đánh giá** | Xem và gửi đánh giá cho từng địa điểm |

---

## 📋 Yêu cầu hệ thống

| Công cụ | Phiên bản | Kiểm tra |
|---|---|---|
| **Python** | 3.10 trở lên | `python --version` |
| **pip** | 23+ | `pip --version` |

> **Không cần** cài PostgreSQL, MySQL hay bất kỳ database server nào.  
> Dự án dùng **SQLite** — file `.db` tự động tạo khi chạy.

---

## 🚀 Cài đặt và chạy

### 1. Clone hoặc tải source code

```bash
git clone <đường-dẫn-repo>
cd Navifit
```

### 2. Tạo môi trường ảo

```bash
# Tạo venv
python -m venv venv

# Kích hoạt — Windows PowerShell
venv\Scripts\Activate.ps1

# Kích hoạt — Windows CMD
venv\Scripts\activate.bat

# Kích hoạt — macOS / Linux
source venv/bin/activate
```

> Khi venv hoạt động, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Mở file `.env` và cập nhật:

```env
# Bắt buộc — giữ nguyên dòng này (dùng SQLite)
DATABASE_URL=sqlite+aiosqlite:///./navifit.db

# Tùy chọn — lấy miễn phí tại https://www.iqair.com/dashboard
IQAIR_API_KEY=your_iqair_api_key_here

# Tùy chọn — không bắt buộc (app dùng OpenStreetMap miễn phí)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 5. Chạy ứng dụng

```bash
python main.py
```

Lần đầu khởi động, hệ thống sẽ tự động:
- ✅ Tạo file `navifit.db`
- ✅ Khởi tạo toàn bộ bảng dữ liệu
- ✅ Nạp **20 địa điểm tập luyện tại Hà Nội**

```
Database initialized and sample data seeded successfully.
NiceGUI ready to go on http://localhost:8081
```

### 6. Mở trình duyệt

```
http://localhost:8081
```

---

## 📁 Cấu trúc thư mục

```
Navifit/
├── main.py              # Entry point — khởi động server (port 8081)
├── database.py          # Kết nối DB + seed 20 địa điểm Hà Nội
├── requirements.txt     # Danh sách thư viện Python
├── .env                 # Biến môi trường (tạo từ .env.example)
├── .env.example         # Mẫu biến môi trường
├── navifit.db           # File SQLite (tự tạo khi chạy)
│
├── api/                 # REST API (FastAPI Router)
│   ├── places.py        # GET /api/places/nearby, /api/places/{id}/...
│   ├── aqi.py           # GET /api/aqi
│   └── sos.py           # GET /api/sos/channels
│
├── models/              # SQLAlchemy ORM models
│   ├── place.py         # Place, PlaceCategory enum
│   ├── review.py        # Review
│   ├── best_time.py     # BestTime (lịch đông đúc)
│   └── sos_channel.py   # SOSChannel
│
├── schemas/             # Pydantic response schemas
├── services/            # Business logic
│   └── places_service.py # Tính khoảng cách, tìm kiếm, lọc
│
├── pages/               # Giao diện NiceGUI
│   ├── home.py          # / — Trang chủ bản đồ
│   ├── search.py        # /search — Tìm kiếm + bản đồ
│   ├── detail.py        # /detail/{id} — Chi tiết địa điểm
│   ├── sos.py           # /sos — Trang SOS
│   └── safe_area.py     # /safe-area — Khu vực an toàn
│
└── components/          # UI components dùng chung
    ├── sos_button.py    # Nút SOS nổi góc phải màn hình
    └── aqi_button.py    # Nút AQI trong header
```

---

## 🌐 API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/places/nearby` | Lấy địa điểm gần tọa độ chỉ định |
| `GET` | `/api/places/{id}/detail` | Chi tiết 1 địa điểm |
| `GET` | `/api/places/{id}/reviews` | Danh sách đánh giá |
| `POST` | `/api/places/{id}/reviews` | Gửi đánh giá mới |
| `GET` | `/api/places/{id}/best-times` | Biểu đồ thời gian tốt nhất |
| `GET` | `/api/aqi` | Chất lượng không khí |
| `GET` | `/api/sos/channels` | Danh sách kênh SOS |

---

## 🗺️ Dữ liệu mẫu

20 địa điểm tập luyện tại Hà Nội được seed tự động, phân bổ trong bán kính 20km từ trung tâm:

| Loại | Số lượng | Ví dụ |
|---|---|---|
| 🏋️ Gym | 7 | California Fitness, Elite Fitness Ba Đình, Lotte Fitness |
| 🌳 Công viên | 5 | Công viên Thống Nhất, Hồ Tây, Nghĩa Đô |
| 🏊 Hồ bơi | 4 | Bể bơi Mỹ Đình, Hapulico, Trung Tự |
| 🏸 Cầu lông | 4 | Trung tâm Gia Lâm, CLB Đống Đa, Bạch Mai |

**Vị trí mặc định:** Nhà B1 — Đại học Bách khoa Hà Nội `(21.006847, 105.843058)`

---

## ❓ Xử lý sự cố

### `ModuleNotFoundError`
```bash
# Đảm bảo venv đang kích hoạt rồi cài lại
pip install -r requirements.txt
```

### Port 8081 đã bị chiếm
```bash
# Tìm process
netstat -ano | findstr :8081
# Hoặc đổi port trong main.py: ui.run(..., port=8082)
```

### Lỗi kích hoạt venv trên Windows PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Reset database (xóa toàn bộ data)
```bash
del navifit.db      # Windows
rm navifit.db       # macOS/Linux
python main.py      # Tạo lại và seed data
```

---

## 🛠️ Công nghệ sử dụng

| Lớp | Công nghệ |
|---|---|
| **Frontend / UI** | [NiceGUI](https://nicegui.io/) — Python-based web UI |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Database** | SQLite + [SQLAlchemy](https://www.sqlalchemy.org/) (async) |
| **Bản đồ** | [Leaflet.js](https://leafletjs.com/) + OpenStreetMap |
| **Tính đường đi** | [OSRM](https://project-osrm.org/) (miễn phí) |
| **AQI** | [IQAir API](https://www.iqair.com/dashboard) |
| **HTTP Client** | [httpx](https://www.python-httpx.org/) |

---

## 📄 License

MIT License — Dự án học thuật ITSS 2025, Đại học Bách khoa Hà Nội.
