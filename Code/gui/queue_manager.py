"""Hàng đợi tải TCP chạy nền, không thao tác trực tiếp lên Tkinter."""

from __future__ import annotations

import socket
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from Code.utils.speed_tracker import SpeedTracker


@dataclass(frozen=True)
class DownloadTask:
    """Thông tin cần thiết để worker tải một tệp về máy."""

    filename: str
    destination: Path
    host: str
    port: int


class DownloadQueueManager:
    """Lập lịch tải với giới hạn đồng thời có thể thay đổi khi đang chạy."""

    CHUNK_SIZE = 64 * 1024
    MAX_WORKERS = 16

    def __init__(
        self,
        on_update: Callable[..., None],
        max_concurrent: int = 2,
    ):
        """Tạo hàng đợi và nhóm worker; callback chỉ nên gửi sự kiện an toàn luồng."""
        if not 1 <= max_concurrent <= self.MAX_WORKERS:
            raise ValueError(f"Giới hạn tải phải từ 1 đến {self.MAX_WORKERS}.")

        self.on_update = on_update
        self.max_concurrent = max_concurrent
        self._tasks = deque()
        self._condition = threading.Condition()
        self._active_count = 0
        self._stopping = False
        self._workers = []
        self._ensure_workers(max_concurrent)

    def set_max_concurrent(self, value: int):
        """Đổi giới hạn tải và đánh thức worker đang chờ nếu có thể chạy thêm."""
        if not 1 <= value <= self.MAX_WORKERS:
            raise ValueError(f"Giới hạn tải phải từ 1 đến {self.MAX_WORKERS}.")
        with self._condition:
            self.max_concurrent = value
            self._ensure_workers(value)
            self._condition.notify_all()

    def _ensure_workers(self, count: int):
        """Chỉ tạo thêm worker khi người dùng tăng giới hạn tải đồng thời."""
        while len(self._workers) < count:
            worker = threading.Thread(
                target=self._worker,
                name=f"download-worker-{len(self._workers) + 1}",
                daemon=True,
            )
            self._workers.append(worker)
            worker.start()

    def add_task(self, task: DownloadTask):
        """Thêm một công việc vào cuối hàng đợi và báo worker kiểm tra công việc."""
        with self._condition:
            if self._stopping:
                raise RuntimeError("Hàng đợi tải đã đóng.")
            self._tasks.append(task)
            self._condition.notify_all()

    def shutdown(self):
        """Ngăn nhận công việc mới và yêu cầu worker đang chờ thoát."""
        with self._condition:
            self._stopping = True
            self._condition.notify_all()

    def _worker(self):
        """Chờ tới lượt theo giới hạn đồng thời rồi xử lý từng công việc."""
        while True:
            with self._condition:
                self._condition.wait_for(
                    lambda: self._stopping
                    or (
                        self._tasks
                        and self._active_count < self.max_concurrent
                    )
                )
                if self._stopping:
                    return
                task = self._tasks.popleft()
                self._active_count += 1

            try:
                self._download(task)
            except Exception as exc:
                self.on_update(
                    task.filename, 0.0, "—", "—", f"Thất bại: {exc}"
                )
            finally:
                with self._condition:
                    self._active_count -= 1
                    self._condition.notify_all()

    def _download(self, task: DownloadTask):
        """Tải đúng số byte khai báo, cập nhật tiến trình và thay tệp đích nguyên tử."""
        temporary_path = task.destination.with_name(
            task.destination.name + ".part"
        )
        tracker = SpeedTracker()
        received = 0

        self.on_update(task.filename, 0.0, "0 KB/s", "—", "Đang xử lý")
        try:
            with socket.create_connection(
                (task.host, task.port), timeout=10
            ) as connection:
                connection.settimeout(30)
                connection.sendall(f"DOWNLOAD|{task.filename}\n".encode("utf-8"))
                response = self._read_line(connection)

                if response.startswith("ERROR|"):
                    raise OSError(response.strip())
                parts = response.strip().split("|")
                if len(parts) != 3 or parts[0] != "FILE_INFO":
                    raise OSError(f"Phản hồi tải không hợp lệ: {response!r}")

                remote_name = parts[1]
                total_size = int(parts[2])
                if remote_name != task.filename or total_size < 0:
                    raise OSError("Thông tin tệp từ Server không hợp lệ.")

                task.destination.parent.mkdir(parents=True, exist_ok=True)
                self.on_update(
                    task.filename,
                    0.0,
                    "0 KB/s",
                    "—",
                    "Đang xử lý",
                    self._format_size(total_size),
                )
                with temporary_path.open("wb") as output_file:
                    while received < total_size:
                        chunk = connection.recv(
                            min(self.CHUNK_SIZE, total_size - received)
                        )
                        if not chunk:
                            raise ConnectionError(
                                "Kết nối đóng trước khi tải đủ dữ liệu."
                            )
                        output_file.write(chunk)
                        received += len(chunk)
                        tracker.update(len(chunk))
                        self._report_progress(
                            task.filename, tracker, total_size
                        )
            temporary_path.replace(task.destination)
            self.on_update(
                task.filename, 100.0, self._speed_text(tracker),
                "0 giây", "Thành công"
            )
        except Exception:
            if temporary_path.exists():
                temporary_path.unlink()
            raise

    def _report_progress(self, filename, tracker, total_size):
        """Tính phần trăm, tốc độ và ETA từ SpeedTracker rồi gửi một bản cập nhật."""
        progress = tracker.get_progress(total_size)
        eta = tracker.get_eta(total_size)
        eta_text = "—" if eta is None else self._duration_text(eta)
        self.on_update(
            filename, progress, self._speed_text(tracker), eta_text,
            "Đang xử lý", self._format_size(total_size)
        )

    @staticmethod
    def _read_line(connection: socket.socket) -> str:
        """Đọc tiêu đề đến ký tự xuống dòng mà không tiêu thụ nhầm byte của tệp."""
        result = bytearray()
        while len(result) <= 8192:
            byte = connection.recv(1)
            if not byte:
                raise ConnectionError("Server đóng kết nối trước tiêu đề.")
            result.extend(byte)
            if byte == b"\n":
                return result.decode("utf-8", errors="replace")
        raise OSError("Tiêu đề từ Server dài bất thường.")

    @staticmethod
    def _speed_text(tracker: SpeedTracker) -> str:
        """Định dạng tốc độ theo KB/s hoặc MB/s cho bảng tiến trình."""
        speed_kb = tracker.get_recent_speed_kbps()
        if speed_kb >= 1024:
            return f"{speed_kb / 1024:.2f} MB/s"
        return f"{speed_kb:.1f} KB/s"

    @staticmethod
    def _duration_text(seconds: float) -> str:
        """Đổi thời lượng ETA sang giây hoặc phút, dễ đọc trong cột trạng thái."""
        if seconds < 60:
            return f"{seconds:.0f} giây"
        minutes, remaining_seconds = divmod(int(seconds), 60)
        return f"{minutes} phút {remaining_seconds} giây"

    @staticmethod
    def _format_size(size: int) -> str:
        """Định dạng kích thước do tiêu đề FILE_INFO cung cấp."""
        value = float(size)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if value < 1024 or unit == "TB":
                return f"{value:.1f} {unit}"
            value /= 1024
        return f"{value:.1f} TB"
