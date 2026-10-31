
import socket
from pathlib import Path

from .logger import get_logger


class NetworkErrorHandler:
    """Phân loại và ghi nhận lỗi mạng, lỗi file."""

    def __init__(self, logger=None):
        self.logger = logger or get_logger()

    def handle_error(self, error, filename=None):
        """
        Phân loại lỗi và trả về thông tin để module gọi xử lý.
        Không tự dừng hàng đợi hoặc ứng dụng.
        """
        if isinstance(error, (socket.timeout, TimeoutError)):
            error_type = "TIMEOUT"
            message = "Kết nối quá thời gian chờ."

        elif isinstance(error, ConnectionRefusedError):
            error_type = "CONNECTION_REFUSED"
            message = "Server từ chối kết nối."

        elif isinstance(error, ConnectionResetError):
            error_type = "CONNECTION_RESET"
            message = "Kết nối bị ngắt đột ngột."

        elif isinstance(error, BrokenPipeError):
            error_type = "BROKEN_PIPE"
            message = "Kết nối đã đóng khi đang gửi dữ liệu."

        elif isinstance(error, ConnectionError):
            error_type = "CONNECTION_ERROR"
            message = "Đã xảy ra lỗi kết nối mạng."

        elif isinstance(error, FileNotFoundError):
            error_type = "FILE_NOT_FOUND"
            message = "Không tìm thấy file."

        elif isinstance(error, PermissionError):
            error_type = "PERMISSION_DENIED"
            message = "Không đủ quyền truy cập file hoặc thư mục."

        elif isinstance(error, OSError):
            error_type = "OS_ERROR"
            message = "Đã xảy ra lỗi hệ thống hoặc thao tác file."

        elif isinstance(error, ValueError):
            error_type = "INVALID_VALUE"
            message = "Giá trị đầu vào không hợp lệ."

        else:
            error_type = "UNKNOWN_ERROR"
            message = "Đã xảy ra lỗi không xác định."

        self.logger.error(
            "Lỗi %s | File: %s | Chi tiết: %s",
            error_type,
            filename or "N/A",
            error,
        )

        return {
            "success": False,
            "error_type": error_type,
            "message": message,
            "filename": filename,
            "details": str(error),
        }

    def check_file_exists(self, filepath):
        """Kiểm tra đường dẫn có trỏ đến file tồn tại hay không."""
        try:
            return Path(filepath).is_file()
        except (OSError, ValueError, TypeError) as error:
            self.logger.warning(
                "Không thể kiểm tra file %s: %s",
                filepath,
                error,
            )
            return False
