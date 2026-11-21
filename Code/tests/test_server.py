"""Kiểm thử FileService và xử lý lệnh của TCPServer [Code/server/]."""

import tempfile
import unittest
from pathlib import Path

from Code.server.file_service import FileService
from Code.server.tcp_server import TCPServer
from Code.utils.logger import close_logger


class FakeClientSocket:
    """Socket giả lập trong bộ nhớ để kiểm thử logic xử lý lệnh của TCPServer."""

    def __init__(self, incoming_chunks: list[bytes] | None = None):
        self._incoming = list(incoming_chunks or [])
        self.sent_data = bytearray()
        self.closed = False
        self.timeout = None

    def settimeout(self, value):
        self.timeout = value

    def recv(self, _bufsize: int) -> bytes:
        if not self._incoming:
            return b""
        return self._incoming.pop(0)

    def sendall(self, data: bytes) -> None:
        self.sent_data.extend(data)

    def close(self) -> None:
        self.closed = True


class TestTCPServer(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.shared_path = Path(self.tmp_dir.name)
        (self.shared_path / "alpha.txt").write_bytes(b"Hello Alpha")
        (self.shared_path / "beta.bin").write_bytes(b"\x00\x01\x02\x03")
        self.server = TCPServer(
            host="127.0.0.1", port=5000, shared_dir=self.shared_path
        )

    def tearDown(self):
        close_logger(self.server.logger)
        self.tmp_dir.cleanup()

    def test_file_service_lists_and_resolves_safe_filenames(self):
        service = FileService(self.shared_path)
        self.assertEqual(service.list_files(), ["alpha.txt", "beta.bin"])
        resolved = service.get_file_path("../../alpha.txt")
        self.assertEqual(resolved, (self.shared_path / "alpha.txt").resolve())

        with self.assertRaises(FileNotFoundError):
            service.get_file_path("nonexistent.txt")

    def test_server_handles_list_files_command(self):
        fake_sock = FakeClientSocket([b"LIST_FILES\n"])
        self.server._handle_client(fake_sock, ("127.0.0.1", 55001))
        self.assertTrue(fake_sock.closed)
        self.assertEqual(
            bytes(fake_sock.sent_data),
            b"FILE_LIST||2\nalpha.txt\nbeta.bin\n",
        )

    def test_server_handles_download_command(self):
        fake_sock = FakeClientSocket([b"DOWNLOAD|alpha.txt\n"])
        self.server._handle_client(fake_sock, ("127.0.0.1", 55002))
        self.assertEqual(
            bytes(fake_sock.sent_data),
            b"FILE_INFO|alpha.txt|11\nHello Alpha",
        )

    def test_server_handles_missing_file_and_invalid_command(self):
        fake_sock = FakeClientSocket([b"DOWNLOAD|missing.txt\n", b"PING\n"])
        self.server._handle_client(fake_sock, ("127.0.0.1", 55003))
        output = fake_sock.sent_data.decode("utf-8")
        self.assertIn("ERROR|FILE_NOT_FOUND|0", output)
        self.assertIn("Lệnh không hợp lệ", output)


if __name__ == "__main__":
    unittest.main()
