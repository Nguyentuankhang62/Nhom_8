# UDM_11 – Download Nhiều File (TCP Socket & Client–Server)

Ứng dụng quản lý và truyền tải đồng thời nhiều tệp tin qua mạng theo mô hình Client–Server, sử dụng giao thức TCP Socket kết hợp giao diện đồ họa (GUI), cơ chế hàng đợi (Queue Management), xử lý đa luồng (Multi-threading) và bẫy lỗi độc lập.

---

## Mục Lục
1. [Tổng Quan Dự Án (Overview)](#1-tổng-quan-dự-án-overview)
2. [Tính Năng Chính (Features)](#2-tính-năng-chính-features)
3. [Công Nghệ Sử Dụng (Technology Stack)](#3-công-nghệ-sử-dụng-technology-stack)
4. [Cấu Trúc Dự Án (Project Structure)](#4-cấu-trúc-dự-án-project-structure)
5. [Kiến Trúc Hệ Thống & Luồng Hoạt Động (Architecture & Workflow)](#5-kiến-trúc-hệ-thống--luồng-hoạt-động-architecture--workflow)
6. [Yêu Cầu Tiền Trạm (Prerequisites)](#6-yêu-cầu-tiền-trạm-prerequisites)
7. [Hướng Dẫn Cài Đặt (Installation)](#7-hướng-dẫn-cài-đặt-installation)
8. [Cấu Hình Hệ Thống (Configuration)](#8-cấu-hình-hệ-thống-configuration)
9. [Hướng Dẫn Sử Dụng (Usage)](#9-hướng-dẫn-sử-dụng-usage)
10. [Kiểm Thử (Testing)](#10-kiểm-thử-testing)
11. [Hạn Chế & Phạm Vi Chưa Triển Khai (Limitations)](#11-hạn-chế--phạm-vi-chưa-triển-khai-limitations)
12. [Hướng Phát Triển (Future Improvements / Roadmap)](#12-hướng-phát-triển-future-improvements--roadmap)
13. [Thành Viên Đóng Góp (Contributors)](#13-thành-viên-đóng-góp-contributors)

---

## 1. Tổng Quan Dự Án (Overview)

Đề tài **UDM_11** nhằm vận dụng kiến thức Lập trình mạng nâng cao để giải quyết bài toán tải nhiều tệp tin cùng lúc từ máy chủ (Server) về máy khách (Client) trong môi trường mạng nội bộ (LAN) hoặc trên cùng một máy tính kiểm thử.

### Vấn đề giải quyết:
Thay vì chỉ hỗ trợ tải từng tệp đơn lẻ hoặc làm treo giao diện người dùng khi truyền dữ liệu dung lượng lớn, hệ thống cung cấp:
* Thao tác chọn và kéo thả (Drag-and-Drop) nhiều tệp tin cùng lúc.
* Cơ chế quản lý hàng đợi và giới hạn tác vụ tải song song ($N$ tệp cùng lúc) nhằm tránh quá tải tài nguyên kết nối.
* Khả năng cách ly lỗi (Fault Tolerance): Khi một tệp gặp lỗi (mất mạng, file không tồn tại), các tệp khác trong danh sách vẫn tiếp tục tải bình thường.

---

## 2. Tính Năng Chính (Features)

* **Kết nối Server:** Cho phép nhập địa chỉ IP và Cổng (Port) để thiết lập kết nối TCP, hiển thị trạng thái kết nối trực quan.
* **Lấy danh sách tệp chia sẻ:** Tự động truy vấn và hiển thị danh sách các tệp sẵn có trên Server (tên tệp, kích thước, định dạng).
* **Kéo thả & Lựa chọn tải:** Hỗ trợ kéo thả một hoặc nhiều tệp từ danh sách Server sang danh sách tải xuống của Client.
* **Quản lý Hàng đợi & Tải đồng thời:** Quản lý thứ tự thực thi bằng Queue, giới hạn tối đa $N$ tệp tải cùng lúc (mặc định $N=2$ hoặc $N=3$ tùy cấu hình).
* **Hiển thị Tiến trình Real-time:** Theo dõi trạng thái (Chờ, Đang tải, Hoàn thành, Lỗi), phần trăm tiến độ (%), tốc độ tải (KB/s, MB/s) và thời gian ước tính cho từng tệp.
* **Xử lý Xung đột File trùng tên:** Hỏi xác nhận ghi đè người dùng nếu tệp đã tồn tại trong thư mục lưu trữ đích.
* **Bẫy lỗi mạng độc lập:** Xử lý mất kết nối giữa chừng, lỗi không tìm thấy tệp hoặc lỗi quyền ghi ổ đĩa mà không làm ảnh hưởng đến các tác vụ khác.

---

## 3. Công Nghệ Sử Dụng (Technology Stack)

* **Ngôn ngữ lập trình:** Python 3.x
* **Giao diện người dùng (GUI):** `Tkinter`, `ttk`, `tkinterdnd2` (thư viện kéo thả)
* **Lập trình Mạng:** TCP Socket (`socket`)
* **Xử lý Đồng thời & Đa luồng:** `threading`, `queue` (hoặc `asyncio`)
* **Quản lý Tệp tin & Đường dẫn:** `pathlib`, `os`
* **Nhật ký & Kiểm thử:** `logging`, `unittest`

---

## 4. Cấu Trúc Dự Án (Project Structure)

Dự án được quy hoạch theo mô hình **Lập trình Hướng đối tượng (OOP)** và phân tách vai trò rõ ràng giữa các module:

```text
my-downloader-project/
│
├── Code/                                # Thư mục chứa toàn bộ mã nguồn ứng dụng
│   ├── client/                          # Module Kết nối Mạng phía Client
│   │   ├── __init__.py
│   │   └── tcp_client.py                # Class TCPClient: Xử lý Socket Client kết nối & gửi/nhận byte
│   │
│   ├── server/                          # Module Server Lõi [Nguyễn Thái Lộc]
│   │   ├── __init__.py
│   │   ├── tcp_server.py                # Class TCPServer: Quản lý kết nối Client, tiếp nhận Socket
│   │   ├── protocol.py                  # Class MessageProtocol: Đóng/Mở gói thông điệp TCP
│   │   └── file_service.py              # Class FileService: Đọc và truy xuất dữ liệu đĩa trên Server
│   │
│   ├── gui/                             # Module Giao diện Client [Nguyễn Tuấn Khang]
│   │   ├── __init__.py
│   │   ├── main_window.py               # Class MainWindow: Giao diện Tkinter/ttk, bảng danh sách file
│   │   └── drag_drop_handler.py         # Handler xử lý sự kiện kéo thả tệp (tkinterdnd2)
│   │
│   ├── queue_mgr/                       # Module Quản lý Hàng đợi [Trần Quốc Bảo]
│   │   ├── __init__.py
│   │   └── queue_manager.py             # Class DownloadQueueManager: Quản lý hàng đợi và giới hạn Concurrency
│   │
│   ├── download/                        # Module Quản lý Tác vụ Tải xuống [Chức năng Lõi]
│   │   ├── __init__.py
│   │   ├── download_manager.py          # Class DownloadManager: Điều phối quá trình tải tệp
│   │   └── download_task.py             # Class DownloadTask: Đại diện cho từng đối tượng tệp đang tải
│   │
│   ├── storage/                         # Module Quản lý File Đĩa [Nguyễn Văn Việt]
│   │   ├── __init__.py
│   │   └── file_manager.py              # Class FileManager: Ghi stream đĩa, xử lý file trùng tên
│   │
│   ├── utils/                           # Module Tiện ích & Bẫy lỗi [Lê Tiến Đạt]
│   │   ├── __init__.py
│   │   ├── speed_tracker.py             # Class SpeedTracker: Tính toán tốc độ (KB/s), phần trăm, ETA
│   │   ├── error_handler.py             # Class NetworkErrorHandler: Bẫy ngoại lệ kết nối & file
│   │   └── logger.py                    # Hệ thống ghi log ứng dụng
│   │
│   └── tests/                           # Module Kiểm thử Tự động [Trần Đức Anh]
│       ├── test_server.py               # Kiểm thử kết nối và Socket Server
│       ├── test_client.py               # Kiểm thử Socket Client
│       ├── test_protocol.py             # Kiểm thử đóng/mở gói giao thức
│       ├── test_download.py             # Kiểm thử đa luồng và hàng đợi tải
│       └── test_file_manager.py         # Kiểm thử ghi đĩa và xung đột tên file
│
├── main.py                              # Entry Point - Khởi chạy ứng dụng [Nguyễn Thái Lộc]
├── DOCX/                                # Lưu trữ tài liệu kỹ thuật Word (.docx) của 6 thành viên
├── PPTX/                                # Slide thuyết trình báo cáo đồ án (.pptx) [Trần Đức Anh]
├── Extra/                               # Tài nguyên phụ trợ, dữ liệu kiểm thử
├── .gitignore                           # Cấu hình loại bỏ file rác Git
├── README.md                            # Tài liệu tổng quan dự án GitHub
└── requirements.txt                     # Danh sách thư viện phụ thuộc Python
```

---

## 5. Kiến Trúc Hệ Thống & Luồng Hoạt Động (Architecture & Workflow)

### 5.1. Bộ Thông Điệp Giao Thức TCP (Message Protocol)
Do TCP là giao thức truyền theo dòng Byte (Byte Stream) không tự xác định ranh giới gói tin, hệ thống định dạng cấu trúc thông điệp chuẩn bao gồm các lệnh:

* `LIST_FILES`: Client yêu cầu Server trả về danh sách tệp tin sẵn có.
* `FILE_LIST`: Server phản hồi tên tệp, kích thước và định dạng tệp.
* `DOWNLOAD [filename]`: Client gửi yêu cầu tải một tệp cụ thể.
* `FILE_INFO [size]`: Server phản hồi kích thước tệp trước khi truyền dữ liệu.
* `FILE_DATA [chunk]`: Server truyền khối dữ liệu tệp (Chunk/Buffer) liên tục.
* `ERROR [code/msg]`: Phản hồi lỗi khi không tìm thấy tệp hoặc mất kết nối.

### 5.2. Luồng Hoạt Động Của Ứng Dụng
```text
[Người dùng] ──> Khởi chạy Server (chỉ định thư mục chia sẻ)
[Người dùng] ──> Mở Client ──> Nhập IP/Port ──> Kết nối TCP
 Client ───────> Gửi lệnh LIST_FILES ───────> Server
 Client <─────── Phản hồi FILE_LIST <──────── Server (Hiển thị lên danh sách GUI)
[Người dùng] ──> Kéo thả tệp cần tải ───────> Đưa vào DownloadQueueManager
 QueueMgr ─────> Kích hoạt Task (≤ N slot)──> Tạo kết nối/luồng tải riêng
 Client ───────> Gửi DOWNLOAD [file] ───────> Server
 Client <─────── Nhận FILE_DATA (chunk) <──── Server ──> SpeedTracker (Tính KB/s) ──> FileManager (Ghi đĩa)
```

---

## 6. Yêu Cầu Tiền Trạm (Prerequisites)

* **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux.
* **Ngôn ngữ:** Python **3.8** trở lên.
* **Thư viện phụ thuộc:** Dành cho tính năng kéo thả trên GUI (`tkinterdnd2`).

---

## 7. Hướng Dẫn Cài Đặt (Installation)

1. **Cloning Repository:**
   ```bash
   git clone https://github.com/[Cần bổ sung URL Repo]/my-downloader-project.git
   cd my-downloader-project
   ```

2. **Tạo môi trường ảo (Khuyên dùng):**
   ```bash
   python -m venv venv
   # Trên Windows:
   venv\Scripts\activate
   # Trên Linux/macOS:
   source venv/bin/activate
   ```

3. **Cài đặt thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 8. Cấu Hình Hệ Thống (Configuration)

* **Địa chỉ IP / Cổng mặc định:**
  * Host Server: `0.0.0.0` (Nghe tất cả các card mạng) hoặc `127.0.0.1` (Chạy local).
  * Port Server mặc định: `8888` (hoặc cấu hình tùy ý).
* **Giới hạn số tác vụ tải đồng thời ($N$):** Cấu hình trong file `Code/queue_mgr/queue_manager.py` (Mặc định: `max_concurrent = 2`).
* **Kích thước khối dữ liệu (Chunk size):** Cấu hình mặc định `4096` bytes hoặc `8192` bytes trong protocol.

---

## 9. Hướng Dẫn Sử Dụng (Usage)

### Bước 1: Khởi chạy Server
Mở terminal và chạy lệnh khởi động Server (Chỉ định thư mục chia sẻ):
```bash
python -m Code.server.tcp_server
```

### Bước 2: Khởi chạy ứng dụng Client
Mở terminal thứ hai để khởi chạy giao diện người dùng:
```bash
python main.py
```

### Bước 3: Thao tác trên giao diện
1. Nhập **Địa chỉ IP** và **Cổng** kết nối của Server, bấm **Kết nối**.
2. Khi danh sách tệp Server xuất hiện, chọn các tệp cần tải.
3. Kéo thả các tệp được chọn sang khu vực **Danh sách tải xuống**.
4. Theo dõi phần trăm tiến trình (%), tốc độ (KB/s) và kiểm tra tệp tại thư mục lưu trữ khi tải hoàn tất.

---

## 10. Kiểm Thử (Testing)

Dự án tích hợp bộ kiểm thử tự động `unittest` nằm trong thư mục `Code/tests/`:

Thực hiện toàn bộ bài kiểm thử tự động:
```bash
python -m unittest discover -s Code/tests
```

Các kịch bản kiểm thử đã được xác minh:
* Kiểm thử kết nối TCP Socket và phản hồi câu lệnh Protocol.
* Giả lập tải đồng thời $N$ file cùng lúc dưới áp lực hàng đợi.
* Kiểm thử bẫy lỗi ngắt kết nối đột ngột giữa chừng.
* Kiểm thử xác nhận xử lý trường hợp tệp trùng tên trong thư mục đĩa.

---

## 11. Hạn Chế & Phạm Vi Chưa Triển Khai (Limitations)

Để đảm bảo hoàn thiện đúng mốc thời gian đồ án môn học, ứng dụng **chưa triển khai** các tính năng nâng cao sau trong phiên bản cơ bản:
* Tạm dừng (Pause) và Tiếp tục tải (Resume) từ vị trí dở dang.
* Khôi phục tự động phiên tải sau khi mất kết nối mạng.
* Xác thực tài khoản người dùng (Authentication) và phân quyền nâng cao.
* Mã hóa dòng dữ liệu truyền tải qua Socket (SSL/TLS).
* Triển khai Server công khai qua môi trường Internet.

---

## 12. Hướng Phát Triển (Future Improvements / Roadmap)

* [ ] Hỗ trợ tính năng Resume Download (Tải tiếp file ngắt quãng dựa trên HTTP Range hoặc Custom Offset).
* [ ] Tích hợp mã hóa kênh truyền TLS/SSL cho Socket.
* [ ] Chia nhỏ 1 file lớn thành nhiều phần tải song song (Multi-part Download).
* [ ] Hoàn thiện gói cài đặt file thực thi độc lập (`.exe` trên Windows bằng PyInstaller).

---

## 13. Thành Viên Đóng Góp (Contributors)

Bảng phân công trách nhiệm nhiệm vụ 6 thành viên trong nhóm:

| STT | Họ và Tên | Vai Trò | Phụ Trách Module Code | Phụ Trách Tài Liệu (Docs) |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Nguyễn Thái Lộc** | Nhóm trưởng / Core Server | `Code/server/`, `main.py` | Architecture & Protocol Spec |
| 2 | **Nguyễn Tuấn Khang** | Client GUI | `Code/gui/` | User Manual & UX/UI Screenshots |
| 3 | **Trần Quốc Bảo** | Queue Manager | `Code/queue_mgr/` | Queue & Multi-threading Design |
| 4 | **Nguyễn Văn Việt** | File Manager | `Code/storage/` | File Management & Overwrite Spec |
| 5 | **Lê Tiến Đạt** | Metrics & Error Handling | `Code/utils/` | Error Handling & Speed Metrics |
| 6 | **Trần Đức Anh** | Testing & QA | `Code/tests/` | Software Test Report, Slide & Final Report |
