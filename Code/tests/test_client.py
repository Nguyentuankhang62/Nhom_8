"""Kiểm thử TCPClient và NetworkErrorHandler [Code/client/, Code/utils/]."""

import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Code.client.tcp_client import TCPClient
from Code.utils.error_handler import NetworkErrorHandler
from Code.utils.logger import close_logger


class FakeConnection:
    """Kết nối socket giả lập cho TCPClient."""

    def __init__(self, response_bytes: bytes):
        self._buffer = bytearray(response_bytes)
        self.sent = bytearray()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def settimeout(self, _timeout):
        pass

    def sendall(self, data: bytes):
        self.sent.extend(data)

    def shutdown(self, _how):
        pass

    def recv(self, bufsize: int) -> bytes:
        if not self._buffer:
            return b""
        chunk = bytes(self._buffer[:bufsize])
        del self._buffer[:bufsize]
        return chunk


class TestTCPClientAndErrorHandler(unittest.TestCase):
    def test_list_files_parses_server_response(self):
        fake_conn = FakeConnection(b"FILE_LIST||2\nfile1.txt\nfile2.png\n")
        client = TCPClient("127.0.0.1", 5000)
        with patch("socket.create_connection", return_value=fake_conn):
            files = client.list_files()
        self.assertEqual(files, ["file1.txt", "file2.png"])
        self.assertEqual(bytes(fake_conn.sent), b"LIST_FILES\n")

    def test_download_file_saves_complete_content(self):
        fake_conn = FakeConnection(b"FILE_INFO|demo.txt|12\nHello World!")
        client = TCPClient("127.0.0.1", 5000)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "demo.txt"
            with patch("socket.create_connection", return_value=fake_conn):
                saved = client.download_file("demo.txt", dest)
            self.assertEqual(saved.read_bytes(), b"Hello World!")
            self.assertFalse(dest.with_name("demo.txt.part").exists())

    def test_download_file_cleans_up_part_file_on_truncated_stream(self):
        fake_conn = FakeConnection(b"FILE_INFO|demo.txt|20\nShortData")
        client = TCPClient("127.0.0.1", 5000)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "demo.txt"
            with patch("socket.create_connection", return_value=fake_conn):
                with self.assertRaises(ConnectionError):
                    client.download_file("demo.txt", dest)
            self.assertFalse(dest.exists())
            self.assertFalse(dest.with_name("demo.txt.part").exists())

    def test_network_error_handler_classifies_exceptions(self):
        handler = NetworkErrorHandler()
        try:
            res_timeout = handler.handle_error(socket.timeout("timed out"), "a.bin")
            self.assertEqual(res_timeout["error_type"], "TIMEOUT")
            self.assertFalse(res_timeout["success"])

            res_refused = handler.handle_error(ConnectionRefusedError("refused"), "b.bin")
            self.assertEqual(res_refused["error_type"], "CONNECTION_REFUSED")

            res_missing = handler.handle_error(FileNotFoundError("no file"), "c.bin")
            self.assertEqual(res_missing["error_type"], "FILE_NOT_FOUND")
        finally:
            close_logger(handler.logger)


if __name__ == "__main__":
    unittest.main()
