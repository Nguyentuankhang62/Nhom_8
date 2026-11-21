"""Kiểm thử đóng/mở gói giao thức MessageProtocol [Code/server/protocol.py]."""

import unittest

from Code.server.protocol import MessageProtocol


class TestMessageProtocol(unittest.TestCase):
    def test_parse_command_strips_cr_and_preserves_lf(self):
        raw = b"LIST_FILES\r\nDOWNLOAD|a.txt\r\n"
        parsed = MessageProtocol.parse_command(raw)
        self.assertEqual(parsed, "LIST_FILES\nDOWNLOAD|a.txt\n")

    def test_build_file_list_response_sorted_and_counted(self):
        response = MessageProtocol.build_file_list_response(["b.txt", "a.txt"])
        self.assertEqual(response, b"FILE_LIST||2\na.txt\nb.txt\n")

    def test_build_file_list_response_empty(self):
        response = MessageProtocol.build_file_list_response([])
        self.assertEqual(response, b"FILE_LIST||0\n")

    def test_build_file_info_response(self):
        response = MessageProtocol.build_file_info_response("report.pdf", 12345)
        self.assertEqual(response, b"FILE_INFO|report.pdf|12345\n")

    def test_build_error_response(self):
        response = MessageProtocol.build_error_response("Không tìm thấy")
        self.assertEqual(
            response,
            "ERROR|FILE_NOT_FOUND|0\nKhông tìm thấy\n".encode("utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
