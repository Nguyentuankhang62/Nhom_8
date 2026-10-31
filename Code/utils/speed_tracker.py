
import time
from collections import deque


class SpeedTracker:
    """Theo dõi tốc độ và tiến trình tải file."""

    def __init__(self, window_seconds=3.0):
        if window_seconds <= 0:
            raise ValueError("window_seconds phải lớn hơn 0.")

        self.window_seconds = float(window_seconds)
        self.reset()

    def update(self, bytes_received):
        """Cập nhật số byte mới nhận được từ lần đọc dữ liệu."""
        if not isinstance(bytes_received, (int, float)):
            raise TypeError("bytes_received phải là số.")

        if bytes_received < 0:
            raise ValueError("Số byte không được âm.")

        now = time.monotonic()
        self.total_bytes_received += bytes_received
        self.samples.append((now, self.total_bytes_received))

        # Giữ lại mẫu trong khoảng thời gian gần đây.
        while (
            len(self.samples) > 1
            and now - self.samples[0][0] > self.window_seconds
        ):
            self.samples.popleft()

    def get_speed(self):
        """Tốc độ trung bình từ lúc bắt đầu, đơn vị byte/giây."""
        elapsed = time.monotonic() - self.start_time

        if elapsed <= 0:
            return 0.0

        return self.total_bytes_received / elapsed

    def get_speed_kbps(self):
        """Tốc độ trung bình, đơn vị KB/s."""
        return self.get_speed() / 1024

    def get_recent_speed(self):
        """Tốc độ gần đây, đơn vị byte/giây."""
        now = time.monotonic()

        if len(self.samples) < 2:
            return 0.0

        oldest_time, oldest_bytes = self.samples[0]
        elapsed = now - oldest_time
        received = self.total_bytes_received - oldest_bytes

        if elapsed <= 0:
            return 0.0

        return received / elapsed

    def get_recent_speed_kbps(self):
        """Tốc độ gần đây, đơn vị KB/s."""
        return self.get_recent_speed() / 1024

    def get_progress(self, total_size):
        """Phần trăm hoàn thành file."""
        if total_size < 0:
            raise ValueError("Kích thước file không được âm.")

        if total_size == 0:
            return 100.0

        progress = self.total_bytes_received / total_size * 100
        return min(100.0, max(0.0, progress))

    def get_eta(self, total_size):
        """Thời gian còn lại ước tính, đơn vị giây."""
        if total_size < 0:
            raise ValueError("Kích thước file không được âm.")

        remaining = max(
            0, total_size - self.total_bytes_received
        )

        if remaining == 0:
            return 0.0

        speed = self.get_recent_speed()

        if speed <= 0:
            return None

        return remaining / speed

    def reset(self):
        """Đặt lại bộ theo dõi cho lần tải mới."""
        self.start_time = time.monotonic()
        self.total_bytes_received = 0
        self.samples = deque([(self.start_time, 0)])
