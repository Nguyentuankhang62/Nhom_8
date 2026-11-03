import time
from collections import deque
import math

class SpeedTracker:
    """Theo dõi tốc độ, tiến độ và thời gian còn lại khi tải file."""

    def __init__(self, window_seconds=3.0):
        if (
            isinstance(window_seconds, bool)
            or not isinstance(window_seconds, (int, float))
            or not math.isfinite(window_seconds)
            or window_seconds <= 0
        ):
            raise ValueError("window_seconds phải là số hữu hạn lớn hơn 0.")

        self.window_seconds = float(window_seconds)
        self.reset()

    def update(self, bytes_received):
        """Cập nhật số byte nhận được trong lần đọc dữ liệu."""
        if isinstance(bytes_received, bool) or not isinstance(
            bytes_received, int
        ):
            raise TypeError("bytes_received phải là số nguyên.")

        if bytes_received < 0:
            raise ValueError("Số byte không được âm.")

        now = time.monotonic()
        self.total_bytes_received += bytes_received
        self.samples.append((now, self.total_bytes_received))

        # Giữ mẫu mới nhất và các mẫu trong cửa sổ thời gian.
        while (
            len(self.samples) > 1
            and now - self.samples[0][0] > self.window_seconds
        ):
            self.samples.popleft()

    def get_speed(self):
        """Trả về tốc độ trung bình từ lúc bắt đầu, đơn vị byte/giây."""
        elapsed = time.monotonic() - self.start_time

        if elapsed <= 0:
            return 0.0

        return self.total_bytes_received / elapsed

    def get_speed_kbps(self):
        """Trả về tốc độ trung bình, đơn vị KB/s (1024 byte)."""
        return self.get_speed() / 1024

    def get_recent_speed(self):
        """Trả về tốc độ gần đây, đơn vị byte/giây."""
        now = time.monotonic()

        if len(self.samples) < 2:
            return 0.0

        oldest_time, oldest_bytes = self.samples[0]
        elapsed = now - oldest_time
        received = self.total_bytes_received - oldest_bytes

        if elapsed <= 0 or received <= 0:
            return 0.0

        return received / elapsed

    def get_recent_speed_kbps(self):
        """Trả về tốc độ gần đây, đơn vị KB/s (1024 byte)."""
        return self.get_recent_speed() / 1024

    @staticmethod
    def _validate_total_size(total_size):
        """Kiểm tra kích thước file là số nguyên không âm."""
        if isinstance(total_size, bool) or not isinstance(total_size, int):
            raise TypeError("total_size phải là số nguyên.")

        if total_size < 0:
            raise ValueError("Kích thước file không được âm.")

    def get_progress(self, total_size):
        """Trả về phần trăm hoàn thành file trong khoảng 0 đến 100."""
        self._validate_total_size(total_size)

        if total_size == 0:
            return 100.0

        progress = self.total_bytes_received / total_size * 100
        return min(100.0, max(0.0, progress))

    def get_eta(self, total_size):
        """Ước tính thời gian còn lại, đơn vị giây.

        Trả về None nếu chưa đủ dữ liệu để ước tính tốc độ.
        """
        self._validate_total_size(total_size)

        remaining = max(0, total_size - self.total_bytes_received)

        if remaining == 0:
            return 0.0

        speed = self.get_recent_speed()

        if speed <= 0:
            return None

        return remaining / speed

    def reset(self):
        """Đặt lại bộ theo dõi cho một lần tải mới."""
        self.start_time = time.monotonic()
        self.total_bytes_received = 0
        self.samples = deque([(self.start_time, 0)])
