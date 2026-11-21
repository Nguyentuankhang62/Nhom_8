# Hướng Dẫn Cài Đặt, Chạy Dự Án & Kiểm Thử (UDM_11 – Download Nhiều File)

Tài liệu này hướng dẫn từng bước cách cài đặt môi trường, khởi chạy **TCP Server**, mở giao diện **Client GUI**, chạy bộ **34 bài kiểm thử tự động (`unittest`)** và các kịch bản kiểm thử thực tế (Demo) cho dự án **UDM_11**.

---

## 1. Yêu Cầu Môi Trường & Cài Đặt Thư Viện

- **Hệ điều hành:** Windows 10/11, macOS hoặc Linux.
- **Python:** Phiên bản **3.9** trở lên (khuyến nghị Python 3.10 – 3.13).
- **Thư viện bắt buộc:** `tkinterdnd2` (hỗ trợ kéo thả tệp trên giao diện Tkinter).

### Bước 1: Mở Terminal (PowerShell) và di chuyển vào thư mục gốc của dự án
```powershell
cd D:\HocTap\LapTrinhMang\UDM_11\UDM_11
```

### Bước 2: Cài đặt thư viện phụ thuộc
```powershell
python -m pip install -r requirements.txt
```
*(Nếu lệnh `python` chưa được thêm vào biến môi trường `PATH` trên máy Windows của bạn, hãy thay chữ `python` bằng đường dẫn đầy đủ: `& "C:\Users\PC\AppData\Local\Programs\Python\Python313\python.exe"`).*

---

## 2. Hướng Dẫn Khởi Chạy Ứng Dụng (Server & Client GUI)

Theo yêu cầu của môn học, **Server** và **Client** phải chạy trên **2 tiến trình (2 cửa sổ Terminal) riêng biệt** giao tiếp qua mạng TCP Socket.

### Bước 1: Khởi chạy TCP Server (Terminal thứ 1)
Mở cửa sổ PowerShell thứ nhất, di chuyển vào thư mục dự án và chạy:

```powershell
cd D:\HocTap\LapTrinhMang\UDM_11\UDM_11
python main.py
```
*(Hoặc chạy trực tiếp module Server: `python -m Code.server.tcp_server`)*

- **Thông số mặc định của Server:**
  - **Địa chỉ lắng nghe (`Host`):** `0.0.0.0` (chấp nhận kết nối từ cả máy cục bộ `127.0.0.1` lẫn các máy khác trong cùng mạng LAN).
  - **Cổng (`Port`):** `5000`
  - **Thư mục chứa file chia sẻ:** `shared_files/`
  - **File nhật ký hệ thống (Log):** Tự động ghi ra màn hình Console và lưu vào `logs/app.log`.
- **Dấu hiệu Server chạy thành công:**
  ```text
  2026-11-21 20:04:35 | INFO | UDM_11.Server | TCP server is listening on 0.0.0.0:5000
  ```

---

### Bước 2: Khởi chạy Giao diện Client GUI (Terminal thứ 2)
Giữ nguyên cửa sổ Server đang chạy, mở thêm **cửa sổ PowerShell thứ hai**, di chuyển vào thư mục dự án và chạy:

```powershell
cd D:\HocTap\LapTrinhMang\UDM_11\UDM_11
python -m Code.gui.main_window
```
Cửa sổ giao diện **"UDM_11 - Download nhiều file"** sẽ xuất hiện.

---

## 3. Hướng Dẫn Thao Tác Trên Giao Diện Client GUI

1. **Kết nối tới Server:**
   - Tại khung **"Kết nối Server"**, nhập:
     - **IP:** `127.0.0.1` *(hoặc địa chỉ IPv4 LAN của máy chạy Server nếu chạy trên 2 máy khác nhau)*.
     - **Port:** `5000`
   - Bấm nút **"Kết nối"**.
   - Khi kết nối thành công, trạng thái đổi sang màu xanh lá **`Trạng thái: Đã kết nối - 127.0.0.1:5000`**, và danh sách các tệp trong thư mục `shared_files/` của Server sẽ hiển thị tại **Khu vực 1**.

2. **Cấu hình trước khi tải (Khung "Cấu hình tải xuống"):**
   - **Giới hạn tải cùng lúc:** Chọn số tệp tối đa được phép tải song song từ `1` đến `16` tệp (mặc định là `2` tệp). Có thể thay đổi ngay cả khi đang tải.
   - **Nếu tệp đích đã tồn tại:** Chọn 1 trong 4 quy tắc xử lý xung đột tên tệp:
     - `Hỏi xác nhận (Ask)`: Bật hộp thoại hỏi `Yes/No` trước khi ghi đè.
     - `Tự động đổi tên (Auto-rename)`: Tự động giữ tệp cũ và lưu tệp mới thành `ten_file (1).ext`, `ten_file (2).ext`...
     - `Ghi đè (Overwrite)`: Tự động ghi đè lên tệp cũ mà không hỏi.
     - `Bỏ qua (Skip)`: Không tải nếu tệp đã có trong thư mục lưu.
   - **Thư mục lưu:** Mặc định trỏ tới thư mục `Downloads` của máy. Bấm nút **"Chọn..."** để đổi sang thư mục khác nếu muốn.

3. **Bắt đầu tải tệp (3 cách):**
   - **Cách 1 (Kéo thả nội bộ):** Chọn 1 hoặc nhiều tệp ở **Khu vực 1** (giữ phím `Ctrl` hoặc `Shift` để chọn nhiều dòng), nhấn giữ chuột trái và kéo thả xuống **Khu vực 2**.
   - **Cách 2 (Kéo thả từ Windows File Explorer):** Kéo các tệp có tên khớp với danh sách trên Server từ File Explorer thả vào **Khu vực 2**.
   - **Cách 3 (Nút bấm):** Chọn các tệp ở **Khu vực 1** rồi bấm nút **"Thêm file đã chọn vào Download"**.

4. **Theo dõi tiến trình & Quản lý danh sách tải (Khu vực 2):**
   - Mỗi tệp hiển thị độc lập: **Tên file**, **Kích thước**, **Tiến trình (`%`)**, **Tốc độ (`KB/s`, `MB/s`)**, **Thời gian còn lại (`ETA`)**, và **Trạng thái** (`Đang chờ` $\rightarrow$ `Đang xử lý` $\rightarrow$ `Thành công` / `Thất bại`).
   - Dòng tổng kết ở góc dưới bên trái hiển thị trực tiếp: `Tổng: X tệp | Chờ: ... | Đang tải: ... | Xong: ... | Lỗi: ...`
   - Các nút hỗ trợ góc dưới bên phải:
     - **"Thử lại mục lỗi"**: Tự động đưa các tệp bị lỗi (`Thất bại`) vào hàng đợi để tải lại.
     - **"Xóa (đã xong / lỗi)"**: Dọn sạch các dòng đã hoàn tất hoặc bị lỗi khỏi bảng (các tệp đang chờ hoặc đang tải được bảo vệ không bị xóa).
     - **"Xóa mục đã chọn"**: Xóa các dòng đã kết thúc đang được bôi chọn.

---

## 4. Hướng Dẫn Chạy Kiểm Thử Tự Động (`unittest`)

Dự án có bộ **34 bài kiểm thử tự động (`unittest`)** nằm trong thư mục `Code/tests/`, bao phủ toàn bộ 7 phần: khởi tạo (`test_init.py`), giao thức (`test_protocol.py`), Server (`test_server.py`), Client & phân loại lỗi (`test_client.py`), đa luồng & cô lập lỗi (`test_download.py`), ghi đĩa & trùng tên (`test_file_manager.py`), giao diện & hàng đợi (`test_gui_queue.py`).

Để chạy toàn bộ 34 bài test, mở Terminal tại thư mục gốc dự án và chạy:

```powershell
cd D:\HocTap\LapTrinhMang\UDM_11\UDM_11
python -m unittest discover -s Code/tests -t . -v
```

**Kết quả chuẩn khi hệ thống hoạt động ổn định:**
```text
Ran 34 tests in 0.170s

OK
```

---

## 5. Mẹo Tạo Tệp Dung Lượng Lớn Để Demo Hàng Đợi & Tốc Độ Tải

Khi chạy thử trên cùng một máy (`127.0.0.1`), tốc độ truyền loopback rất cao nên các tệp nhỏ vài chục KB sẽ tải xong ngay lập tức (`100%`). Để quan sát rõ hiệu ứng **hàng đợi giới hạn `N` file tải cùng lúc**, **tiến trình `%` nhảy dần**, **tốc độ `MB/s`** và **`ETA`**, bạn có thể chạy các lệnh PowerShell sau để tạo nhanh 4 tệp mẫu (`40 MB – 60 MB`) trong thư mục `shared_files/`:

```powershell
cd D:\HocTap\LapTrinhMang\UDM_11\UDM_11
fsutil file createnew shared_files\demo_video_1.mp4 52428800
fsutil file createnew shared_files\demo_video_2.mp4 52428800
fsutil file createnew shared_files\demo_dataset_3.zip 41943040
fsutil file createnew shared_files\demo_backup_4.iso 62914560
```
Sau khi tạo xong, bấm nút **"Làm mới danh sách"** trên Client GUI và kéo cả 4 tệp xuống **Khu vực 2** để quan sát hàng đợi hoạt động.
