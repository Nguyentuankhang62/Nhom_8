"""Class TCPClient: Xử lý Socket Client kết nối, lấy danh sách file và tải file từ TCPServer."""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Callable, Iterator


class TCPClient:
    """TCP Socket Client giao tiếp với TCPServer theo giao thức của dự án UDM_11."""

    CHUNK_SIZE = 64 * 1024

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, timeout: float = 10.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def list_files(self) -> list[str]:
        """Gửi lệnh LIST_FILES và trả về danh sách tên file trên Server."""
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as conn:
            conn.settimeout(self.timeout)
            conn.sendall(b"LIST_FILES\n")
            conn.shutdown(socket.SHUT_WR)
            response = bytearray()
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                response.extend(chunk)

        lines = response.decode("utf-8", errors="replace").splitlines()
        if not lines or not lines[0].startswith("FILE_LIST||"):
            raise OSError("Phản hồi danh sách file từ Server không hợp lệ.")
        count = int(lines[0].split("||", 1)[1])
        return lines[1 : count + 1]

    def download_chunks(
        self,
        filename: str,
        on_info: Callable[[str, int], None] | None = None,
    ) -> Iterator[bytes]:
        """Kết nối tới Server, gửi DOWNLOAD|<filename> và yield từng chunk dữ liệu."""
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as conn:
            conn.settimeout(max(self.timeout, 30.0))
            conn.sendall(f"DOWNLOAD|{filename}\n".encode("utf-8"))
            header = self._read_line(conn)

            if header.startswith("ERROR|"):
                raise FileNotFoundError(header.strip())

            parts = header.strip().split("|")
            if len(parts) != 3 or parts[0] != "FILE_INFO":
                raise OSError(f"Phản hồi tải không hợp lệ: {header!r}")

            remote_name = parts[1]
            total_size = int(parts[2])
            if remote_name != filename or total_size < 0:
                raise OSError("Thông tin tệp từ Server không hợp lệ.")

            if on_info is not None:
                on_info(remote_name, total_size)

            received = 0
            while received < total_size:
                chunk = conn.recv(min(self.CHUNK_SIZE, total_size - received))
                if not chunk:
                    raise ConnectionError("Kết nối đóng trước khi tải đủ dữ liệu.")
                received += len(chunk)
                yield chunk

    def download_file(self, filename: str, destination: str | Path) -> Path:
        """Tải một tệp từ Server về đường dẫn đích an toàn qua file tạm .part."""
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target.with_name(target.name + ".part")
        try:
            with temp_path.open("wb") as out:
                for chunk in self.download_chunks(filename):
                    out.write(chunk)
            temp_path.replace(target)
            return target
        except BaseException:
            if temp_path.exists():
                temp_path.unlink()
            raise

    @staticmethod
    def _read_line(connection: socket.socket) -> str:
        """Đọc dòng tiêu đề phản hồi kết thúc bằng ký tự xuống dòng."""
        result = bytearray()
        while len(result) <= 8192:
            byte = connection.recv(1)
            if not byte:
                raise ConnectionError("Server đóng kết nối trước tiêu đề.")
            result.extend(byte)
            if byte == b"\n":
                return result.decode("utf-8", errors="replace")
        raise OSError("Tiêu đề từ Server dài bất thường.")
